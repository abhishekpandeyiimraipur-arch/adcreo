"""
backend/app/gateway/health.py
HealthManager — provider health scoring + circuit breaker.
All state lives in Redis DB3. No-ops silently when redis is None (test mode).
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

CB_FAILURE_THRESHOLD = 3      # consecutive failures before circuit OPEN
CB_OPEN_TTL_S        = 120    # seconds circuit stays OPEN
HEALTH_SUCCESS_DELTA = +10
HEALTH_FAILURE_DELTA = -30
HEALTH_DEFAULT       = 70
HEALTH_MIN           = 0
HEALTH_MAX           = 100
AFFINITY_BOOST       = 500    # guarantees top placement when healthy


class HealthManager:
    """
    Owns all provider health state in Redis DB3.
    get_ranked_providers() is called before every capability request.
    record_success/failure() is called after every attempt.
    """

    def __init__(self, redis_client=None):
        self.redis = redis_client

    def _health_key(self, capability: str, provider: str) -> str:
        return f"health:{capability}:{provider}"

    def _cb_key(self, provider: str) -> str:
        return f"cb:{provider}"

    def _fail_count_key(self, provider: str) -> str:
        return f"cb_fail:{provider}"

    async def get_score(self, capability: str, provider: str) -> int:
        if self.redis is None:
            return HEALTH_DEFAULT
        try:
            val = await self.redis.get(self._health_key(capability, provider))
            return int(val) if val else HEALTH_DEFAULT
        except Exception:
            return HEALTH_DEFAULT

    async def is_circuit_open(self, provider: str) -> bool:
        if self.redis is None:
            return False
        try:
            return await self.redis.exists(self._cb_key(provider)) == 1
        except Exception:
            return False

    async def get_ranked_providers(
        self,
        capability: str,
        providers: list[str],
        affinity_provider: Optional[str] = None,
    ) -> list[str]:
        """
        Returns providers sorted by effective health score.
        Skips providers with circuit breaker OPEN.
        If ALL circuits are open, returns full pool anyway
        so failures are visible rather than silently blocked.
        affinity_provider gets +AFFINITY_BOOST to its score.
        """
        available = []
        circuit_open = []

        for p in providers:
            if await self.is_circuit_open(p):
                circuit_open.append(p)
                continue
            score = await self.get_score(capability, p)
            if p == affinity_provider:
                score += AFFINITY_BOOST
            available.append((p, score))

        available.sort(key=lambda x: -x[1])
        ranked = [p for p, _ in available]

        if not ranked:
            logger.warning(
                f"All {capability} providers have open circuit breakers. "
                f"Returning full pool — expect failures."
            )
            return providers

        return ranked + circuit_open

    async def record_success(self, capability: str, provider: str) -> None:
        if self.redis is None:
            return
        try:
            key = self._health_key(capability, provider)
            current = int(await self.redis.get(key) or HEALTH_DEFAULT)
            await self.redis.set(key, min(current + HEALTH_SUCCESS_DELTA, HEALTH_MAX), ex=3600)
            await self.redis.delete(self._fail_count_key(provider))
            await self.redis.delete(self._cb_key(provider))
        except Exception as exc:
            logger.warning(f"HealthManager.record_success failed {provider}: {exc}")

    async def record_failure(self, capability: str, provider: str) -> None:
        if self.redis is None:
            return
        try:
            key = self._health_key(capability, provider)
            current = int(await self.redis.get(key) or HEALTH_DEFAULT)
            await self.redis.set(key, max(current + HEALTH_FAILURE_DELTA, HEALTH_MIN), ex=3600)

            fail_key = self._fail_count_key(provider)
            fail_count = int(await self.redis.incr(fail_key))
            await self.redis.expire(fail_key, 60)

            if fail_count >= CB_FAILURE_THRESHOLD:
                await self.redis.set(self._cb_key(provider), "OPEN", ex=CB_OPEN_TTL_S)
                logger.warning(
                    f"Circuit breaker OPEN: {provider} "
                    f"(capability={capability}, {fail_count} failures in 60s)"
                )
        except Exception as exc:
            logger.warning(f"HealthManager.record_failure failed {provider}: {exc}")
