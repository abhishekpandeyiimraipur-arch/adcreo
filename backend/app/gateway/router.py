"""
backend/app/gateway/router.py
ModelGateway — unified capability router with health-aware provider selection.
External interface unchanged: gateway.route(capability, input_data, max_tokens)
All provider HTTP handlers live here. Config lives in config.py. Health in health.py.
"""
import asyncio
import base64
import io
import json
import logging
import os
import time
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

import httpx

from app.gateway.config import (
    COST_RATES,
    PROVIDER_CONFIG,
    PROVIDER_POOLS,
    SARVAM_LANG_MAP,
    TTS_LANGUAGE_AFFINITY,
)
from app.gateway.health import HealthManager
from app.core.exceptions import ProviderUnavailableError

logger = logging.getLogger(__name__)

VISION_PROMPT = """You are a product analyst for Indian D2C brands.
Analyze this product image and return a JSON object with exactly these fields:
{
  "product_name": "string — specific product name",
  "category": "one of: d2c_beauty | packaged_food | hard_accessories | electronics | home_kitchen | d2c_fashion. Use d2c_fashion for clothing, kurta, saree, lehenga, ethnic wear, western wear, fashion, apparel, footwear, bags",
  "price_inr": null or number — estimated Indian retail price,
  "key_features": ["list", "of", "3-5", "key", "features"],
  "color_palette": ["#hex1", "#hex2", "#hex3"],
  "shape": "one of: bottle, box, pouch, tube, jar, can, irregular"
}
Return ONLY the JSON object. No markdown, no explanation, no backticks."""


def _parse_json_response(raw: str) -> dict:
    clean = raw.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        clean = parts[1]
        if clean.startswith("json"):
            clean = clean[4:]
    return json.loads(clean.strip())


@dataclass
class GatewayResponse:
    """Uniform response contract for all gateway capabilities."""
    text:        str            = ""
    cost_inr:    Decimal        = Decimal("0.00")
    model_used:  str            = ""
    tokens_in:   int            = 0
    tokens_out:  int            = 0
    latency_ms:  int            = 0
    audio_bytes: Optional[bytes]= None
    video_url:   Optional[str]  = None
    embedding:   Optional[list] = None


class ModelGateway:
    """
    Single chokepoint for all external AI provider calls.
    Every capability uses the same health-aware routing loop.
    Workers never call provider APIs directly.
    """

    def __init__(self, redis_client=None):
        self.health         = HealthManager(redis_client)
        self.redis_client   = redis_client
        self.last_call_cost = Decimal("0.00")
        self.last_model_used = ""
        # Read keys once at init for providers that need instance-level access
        self._together_key  = os.environ.get("TOGETHER_API_KEY", "")
        self._gemini_key    = os.environ.get("GEMINI_API_KEY", "")
        self._openai_key    = os.environ.get("OPENAI_API_KEY", "")
        self._atlascloud_key= os.environ.get("ATLAS_CLOUD_API_KEY", "")

    # ── Public entry point ────────────────────────────────────────────────────

    async def route(
        self,
        capability: str,
        input_data: dict,
        max_tokens: int = 1024,
    ) -> GatewayResponse:
        """Single entry point. Dispatches by capability."""
        start = time.monotonic()

        if capability == "vision":
            raw = await self._route_vision(input_data)
            response = GatewayResponse(
                text=json.dumps(raw),
                model_used="vision-pool",
                latency_ms=int((time.monotonic() - start) * 1000),
            )
        elif capability == "llm":
            response = await self._route_pool(
                capability="llm",
                input_data=input_data,
                handler_map=self._llm_handler_map(),
                extra={"max_tokens": max_tokens},
            )
            response.latency_ms = int((time.monotonic() - start) * 1000)
        elif capability == "tts":
            language = input_data.get("language", "hindi")
            affinity = TTS_LANGUAGE_AFFINITY.get(language)
            response = await self._route_pool(
                capability="tts",
                input_data=input_data,
                handler_map=self._tts_handler_map(),
                affinity_provider=affinity,
            )
            response.latency_ms = int((time.monotonic() - start) * 1000)
        elif capability == "moderation":
            response = await self._route_pool(
                capability="moderation",
                input_data=input_data,
                handler_map=self._moderation_handler_map(),
            )
            response.latency_ms = int((time.monotonic() - start) * 1000)
        elif capability == "i2v":
            response = await self._route_i2v(input_data)
            response.latency_ms = int((time.monotonic() - start) * 1000)
        elif capability == "embedding":
            raise NotImplementedError("Embedding: Micro-phase 5.")
        else:
            raise ValueError(f"Unknown gateway capability: '{capability}'")

        self.last_call_cost  = response.cost_inr
        self.last_model_used = response.model_used
        return response

    # ── Unified routing loop ──────────────────────────────────────────────────

    async def _route_pool(
        self,
        capability: str,
        input_data: dict,
        handler_map: dict,
        affinity_provider: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> GatewayResponse:
        """
        THE SINGLE ROUTING LOOP used by LLM, TTS, moderation.
        1. Ask HealthManager for ranked provider list (health-filtered).
        2. Try each in order.
        3. On success: record health, return.
        4. On failure: record health, continue to next.
        5. All exhausted: raise ProviderUnavailableError.
        """
        providers = PROVIDER_POOLS[capability]
        ranked = await self.health.get_ranked_providers(
            capability, providers, affinity_provider
        )

        last_error = None
        for provider in ranked:
            if provider not in handler_map:
                logger.warning(f"No handler for {capability} provider {provider} — skipping")
                continue
            try:
                if extra:
                    result = await handler_map[provider](input_data, **extra)
                else:
                    result = await handler_map[provider](input_data)
                await self.health.record_success(capability, provider)
                return result
            except Exception as exc:
                logger.warning(f"{capability} provider {provider} failed: {exc}")
                await self.health.record_failure(capability, provider)
                last_error = exc
                continue

        raise ProviderUnavailableError(
            f"All {capability} providers exhausted. Last error: {last_error}"
        )

    # ── Handler maps ──────────────────────────────────────────────────────────

    def _llm_handler_map(self) -> dict:
        return {
            "groq-llama-3.3-70b": self._call_groq_llm,
            "together-llama-3.3": self._call_together_llm,
            "siliconflow-qwen":   self._call_openai_compat_llm_factory("siliconflow-qwen"),
            "deepseek-v3":        self._call_openai_compat_llm_factory("deepseek-v3"),
            "openai-gpt4o-mini":  self._call_openai_llm,
        }

    def _tts_handler_map(self) -> dict:
        return {
            "sarvam-bulbul":    self._call_sarvam_tts,
            "elevenlabs-rachel": self._call_elevenlabs_tts,
        }

    def _moderation_handler_map(self) -> dict:
        return {
            "groq-llama-guard":  self._call_groq_moderation,
            "openai-moderation": self._call_openai_moderation,
        }

    # ── Cost helper ───────────────────────────────────────────────────────────

    def _calculate_cost(self, provider: str, tokens_in: int, tokens_out: int) -> Decimal:
        rates = COST_RATES.get(provider, (Decimal("0.00"), Decimal("0.00")))
        return (
            rates[0] * Decimal(tokens_in) / 1000
            + rates[1] * Decimal(tokens_out) / 1000
        ).quantize(Decimal("0.000001"))

    # ── LLM handlers ─────────────────────────────────────────────────────────

    async def _call_openai_compat_llm(
        self,
        input_data: dict,
        max_tokens: int,
        provider: str,
    ) -> GatewayResponse:
        """Generic OpenAI-compatible handler. Used by DeepSeek, SiliconFlow."""
        cfg     = PROVIDER_CONFIG[provider]
        api_key = os.environ.get(cfg["key_env"], "")
        payload = {
            "model":           cfg["model_id"],
            "messages": [
                {"role": "system", "content": input_data.get("system_prompt", "")},
                {"role": "user",   "content": input_data.get("user_prompt", "")},
            ],
            "response_format": input_data.get("response_format", {"type": "text"}),
            "max_tokens":      max_tokens,
            "temperature":     0.3,
        }
        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            resp = await client.post(
                cfg["url"],
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
        data       = resp.json()
        text       = data["choices"][0]["message"]["content"]
        usage      = data.get("usage", {})
        tokens_in  = usage.get("prompt_tokens", 0)
        tokens_out = usage.get("completion_tokens", 0)
        return GatewayResponse(
            text=text,
            cost_inr=self._calculate_cost(provider, tokens_in, tokens_out),
            model_used=provider,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
        )

    def _call_openai_compat_llm_factory(self, provider: str):
        """Returns a bound handler for a given OpenAI-compat provider."""
        async def handler(input_data: dict, max_tokens: int = 1024) -> GatewayResponse:
            return await self._call_openai_compat_llm(input_data, max_tokens, provider)
        return handler

    async def _call_groq_llm(self, input_data: dict, max_tokens: int = 1024) -> GatewayResponse:
        return await self._call_openai_compat_llm(input_data, max_tokens, "groq-llama-3.3-70b")

    async def _call_together_llm(self, input_data: dict, max_tokens: int = 1024) -> GatewayResponse:
        return await self._call_openai_compat_llm(input_data, max_tokens, "together-llama-3.3")

    async def _call_openai_llm(self, input_data: dict, max_tokens: int = 1024) -> GatewayResponse:
        cfg     = PROVIDER_CONFIG["openai-gpt4o-mini"]
        api_key = os.environ.get(cfg["key_env"], "")
        resp_fmt = input_data.get("response_format", {})
        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            resp = await client.post(
                cfg["url"],
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": cfg["model_id"],
                    "messages": [
                        {"role": "system", "content": input_data.get("system_prompt", "")},
                        {"role": "user",   "content": input_data.get("user_prompt", "")},
                    ],
                    "max_tokens": max_tokens,
                    "response_format": (
                        {"type": "json_object"}
                        if resp_fmt.get("type") == "json_object"
                        else {"type": "text"}
                    ),
                },
            )
            resp.raise_for_status()
        data       = resp.json()
        text       = data["choices"][0]["message"]["content"]
        usage      = data.get("usage", {})
        tokens_in  = usage.get("prompt_tokens", 0)
        tokens_out = usage.get("completion_tokens", 0)
        return GatewayResponse(
            text=text,
            cost_inr=self._calculate_cost("openai-gpt4o-mini", tokens_in, tokens_out),
            model_used="openai-gpt4o-mini",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
        )

    # ── TTS handlers ──────────────────────────────────────────────────────────

    async def _call_sarvam_tts(self, input_data: dict) -> GatewayResponse:
        cfg      = PROVIDER_CONFIG["sarvam-bulbul"]
        api_key  = os.environ.get(cfg["key_env"], "")
        text     = input_data.get("text", "")
        language = input_data.get("language", "hindi")
        gen_id   = input_data.get("gen_id", "")
        lang_code = SARVAM_LANG_MAP.get(language, "hi-IN")

        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            resp = await client.post(
                cfg["url"],
                headers={
                    "api-subscription-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "inputs":               [text],
                    "target_language_code": lang_code,
                    "speaker":              cfg["speaker"],
                    "speech_sample_rate":   22050,
                    "enable_preprocessing": True,
                    "model":                cfg["model_id"],
                },
            )

        if resp.status_code != 200:
            raise ProviderUnavailableError(
                f"Sarvam TTS {resp.status_code}: {resp.text[:200]}"
            )

        data        = resp.json()
        audio_b64   = data.get("audios", [""])[0]
        audio_bytes = base64.b64decode(audio_b64)
        logger.info(f"Sarvam TTS done gen={gen_id} lang={lang_code} bytes={len(audio_bytes)}")
        return GatewayResponse(
            audio_bytes=audio_bytes,
            model_used="sarvam-bulbul",
            cost_inr=cfg["cost_inr"],
        )

    async def _call_elevenlabs_tts(self, input_data: dict) -> GatewayResponse:
        cfg     = PROVIDER_CONFIG["elevenlabs-rachel"]
        api_key = os.environ.get(cfg["key_env"], "")
        text    = input_data.get("text", "")
        gen_id  = input_data.get("gen_id", "")

        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            resp = await client.post(
                cfg["url"],
                headers={
                    "xi-api-key":   api_key,
                    "Content-Type": "application/json",
                    "Accept":       "audio/mpeg",
                },
                json={
                    "text":     text,
                    "model_id": cfg["model_id"],
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                },
            )

        if resp.status_code != 200:
            raise ProviderUnavailableError(
                f"ElevenLabs TTS {resp.status_code}: {resp.text[:200]}"
            )

        audio_bytes = resp.content
        logger.info(f"ElevenLabs TTS done gen={gen_id} bytes={len(audio_bytes)}")
        return GatewayResponse(
            audio_bytes=audio_bytes,
            model_used="elevenlabs-rachel",
            cost_inr=cfg["cost_inr"],
        )

    # ── Moderation handlers ───────────────────────────────────────────────────

    async def _call_groq_moderation(self, input_data: dict) -> GatewayResponse:
        cfg     = PROVIDER_CONFIG["groq-llama-guard"]
        api_key = os.environ.get(cfg["key_env"], "")
        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            resp = await client.post(
                cfg["url"],
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": cfg["model_id"],
                    "messages": [{"role": "user", "content": input_data.get("text", "")}],
                },
            )
            resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return GatewayResponse(text=text, model_used="groq-llama-guard", cost_inr=Decimal("0.00"))

    async def _call_openai_moderation(self, input_data: dict) -> GatewayResponse:
        cfg     = PROVIDER_CONFIG["openai-moderation"]
        api_key = os.environ.get(cfg["key_env"], "")
        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            resp = await client.post(
                cfg["url"],
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": cfg["model_id"], "input": input_data.get("text", "")},
            )
            resp.raise_for_status()
        flagged = resp.json()["results"][0]["flagged"]
        return GatewayResponse(
            text="unsafe" if flagged else "safe",
            model_used="openai-moderation",
            cost_inr=Decimal("0.00"),
        )

    # ── Vision handlers ───────────────────────────────────────────────────────

    async def _route_vision(self, input_data: dict) -> dict:
        gen_id    = input_data.get("gen_id", "unknown")
        image_b64 = input_data["image_b64"]
        providers = [
            ("openai", self._call_openai_vision),
            ("gemini", self._call_gemini_vision),
        ]
        last_error = None
        for name, fn in providers:
            try:
                logger.info(f"Vision attempt via {name} gen={gen_id}")
                result = await fn(image_b64, gen_id)
                logger.info(f"Vision success via {name} gen={gen_id}")
                return result
            except Exception as exc:
                logger.warning(f"Vision {name} failed gen={gen_id}: {exc}")
                last_error = exc
        raise ProviderUnavailableError(
            f"All vision providers failed gen={gen_id}. Last: {last_error}"
        )

    async def _call_openai_vision(self, image_b64: str, gen_id: str) -> dict:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                            {"type": "text", "text": VISION_PROMPT},
                        ],
                    }],
                    "max_tokens": 512,
                    "temperature": 0.1,
                },
            )
            resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        return _parse_json_response(raw)

    async def _call_gemini_vision(self, image_b64: str, gen_id: str) -> dict:
        import google.generativeai as genai
        from PIL import Image as PILImage
        genai.configure(api_key=self._gemini_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        image = PILImage.open(io.BytesIO(base64.b64decode(image_b64)))
        raw   = await asyncio.to_thread(
            lambda: model.generate_content([VISION_PROMPT, image]).text
        )
        return _parse_json_response(raw)

    # ── I2V routing (sequential fallback with health recording) ───────────────

    async def _route_i2v(self, input_data: dict) -> GatewayResponse:
        """
        I2V uses sequential fallback (not _route_pool) because each provider
        has a unique async polling contract that doesn't fit the generic loop.
        Health is still recorded per provider for observability.
        """
        gen_id    = input_data.get("gen_id", "")
        providers = PROVIDER_POOLS["i2v"]
        ranked    = await self.health.get_ranked_providers("i2v", providers)

        handler_map = {
            "fal-wan-i2v":    self._call_fal_i2v,
            "atlascloud-wan": self._call_atlascloud_i2v,
            "minimax-hailuo": self._call_minimax_i2v,
            "replicate-wan":  self._call_replicate_i2v,
        }

        last_error = None
        for provider in ranked:
            if provider not in handler_map:
                continue
            try:
                result = await handler_map[provider](input_data)
                await self.health.record_success("i2v", provider)
                return result
            except ProviderUnavailableError as exc:
                logger.warning(f"I2V provider {provider} failed gen={gen_id}: {exc}")
                await self.health.record_failure("i2v", provider)
                last_error = exc
                continue

        raise ProviderUnavailableError(
            f"All I2V providers exhausted gen={gen_id}. Last: {last_error}"
        )

    async def _call_fal_i2v(self, input_data: dict) -> GatewayResponse:
        cfg       = PROVIDER_CONFIG["fal-wan-i2v"]
        api_key   = os.environ.get(cfg["key_env"], "")
        gen_id    = input_data.get("gen_id", "")
        headers   = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            payload = {
                "image_url": input_data.get("image_url", ""),
                "prompt":    input_data.get("prompt", ""),
                "duration":  input_data.get("duration", 9),
                "seed":      input_data.get("seed", 42),
            }
            if input_data.get("aspect_ratio"):
                payload["aspect_ratio"] = input_data["aspect_ratio"]
            submit = await client.post(
                cfg["submit_url"],
                headers=headers,
                json=payload,
            )
            if submit.status_code not in (200, 201, 202):
                raise ProviderUnavailableError(
                    f"Fal.ai submit {submit.status_code}: {submit.text[:300]}"
                )
            request_id = submit.json().get("request_id", "")
            if not request_id:
                raise ProviderUnavailableError(f"Fal.ai no request_id gen={gen_id}")

            logger.info(f"Fal.ai queued gen={gen_id} request_id={request_id}")

            for attempt in range(cfg["max_polls"]):
                await asyncio.sleep(cfg["poll_interval_s"])
                status_resp = await client.get(
                    cfg["status_url"].format(request_id=request_id),
                    headers=headers, timeout=10.0,
                )
                if status_resp.status_code != 200:
                    continue
                status = status_resp.json().get("status", "")
                logger.info(f"Fal.ai poll gen={gen_id} attempt={attempt+1} status={status}")
                if status == "COMPLETED":
                    break
                if status in ("FAILED", "CANCELLED"):
                    raise ProviderUnavailableError(f"Fal.ai {status} gen={gen_id}")
            else:
                raise ProviderUnavailableError(
                    f"Fal.ai timeout {cfg['max_polls']*cfg['poll_interval_s']}s gen={gen_id}"
                )

            result_resp = await client.get(
                cfg["result_url"].format(request_id=request_id),
                headers=headers, timeout=10.0,
            )
            if result_resp.status_code != 200:
                raise ProviderUnavailableError(f"Fal.ai result {result_resp.status_code} gen={gen_id}")

            result    = result_resp.json()
            video_url = result.get("video", {}).get("url") or result.get("video_url", "")
            if not video_url:
                raise ProviderUnavailableError(f"Fal.ai no video URL gen={gen_id}")

        logger.info(f"Fal.ai done gen={gen_id} url={video_url[:60]}...")
        return GatewayResponse(video_url=video_url, model_used="fal-wan-i2v", cost_inr=cfg["cost_inr"])

    async def _call_atlascloud_i2v(self, input_data: dict) -> GatewayResponse:
        cfg     = PROVIDER_CONFIG["atlascloud-wan"]
        api_key = self._atlascloud_key
        gen_id  = input_data.get("gen_id", "")
        if not api_key:
            raise ProviderUnavailableError("ATLAS_CLOUD_API_KEY not set")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            submit = await client.post(
                cfg["submit_url"], headers=headers,
                json={
                    "model":    cfg["model_id"],
                    "image":    input_data.get("image_url", ""),
                    "prompt":   input_data.get("prompt", ""),
                    "duration": input_data.get("duration", 9),
                },
            )
            if submit.status_code not in (200, 201):
                raise ProviderUnavailableError(
                    f"Atlas Cloud submit {submit.status_code}: {submit.text[:200]}"
                )
            resp_json     = submit.json()
            prediction_id = resp_json.get("data", {}).get("id", "") or resp_json.get("id", "")
            if not prediction_id:
                raise ProviderUnavailableError(f"Atlas Cloud no prediction_id gen={gen_id}")
            logger.info(f"Atlas Cloud queued gen={gen_id} id={prediction_id}")

            for attempt in range(cfg["max_polls"]):
                await asyncio.sleep(cfg["poll_interval_s"])
                poll = await client.get(
                    cfg["poll_url"].format(prediction_id=prediction_id),
                    headers=headers, timeout=10.0,
                )
                if poll.status_code != 200:
                    continue
                poll_data = poll.json().get("data", {})
                status    = poll_data.get("status", "")
                logger.info(f"Atlas Cloud poll gen={gen_id} attempt={attempt+1} status={status}")
                if status in ("succeeded", "completed", "success"):
                    outputs   = poll_data.get("outputs", [])
                    video_url = outputs[0] if outputs else poll_data.get("output", "")
                    if not video_url:
                        raise ProviderUnavailableError(f"Atlas Cloud no output gen={gen_id}")
                    v = video_url if isinstance(video_url, str) else video_url.get("url", "")
                    logger.info(f"Atlas Cloud done gen={gen_id}")
                    return GatewayResponse(video_url=v, model_used="atlascloud-wan", cost_inr=cfg["cost_inr"])
                if status in ("failed", "error", "canceled"):
                    raise ProviderUnavailableError(
                        f"Atlas Cloud {status} gen={gen_id}: {poll_data.get('error','unknown')}"
                    )
            raise ProviderUnavailableError(f"Atlas Cloud timeout gen={gen_id}")

    async def _call_minimax_i2v(self, input_data: dict) -> GatewayResponse:
        cfg     = PROVIDER_CONFIG["minimax-hailuo"]
        api_key = os.environ.get(cfg["key_env"], "")
        gen_id  = input_data.get("gen_id", "")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            submit = await client.post(
                cfg["submit_url"], headers=headers,
                json={
                    "model":             cfg["model_id"],
                    "prompt":            input_data.get("prompt", ""),
                    "first_frame_image": input_data.get("image_url", ""),
                    "duration": 6, "resolution": "768P",
                },
            )
            if submit.status_code not in (200, 201):
                raise ProviderUnavailableError(
                    f"Minimax submit {submit.status_code}: {submit.text[:300]}"
                )
            task_id = submit.json().get("task_id", "")
            if not task_id:
                raise ProviderUnavailableError(f"Minimax no task_id gen={gen_id}")
            logger.info(f"Minimax queued gen={gen_id} task_id={task_id}")

            file_id = None
            for attempt in range(cfg["max_polls"]):
                await asyncio.sleep(cfg["poll_interval_s"])
                poll = await client.get(
                    cfg["poll_url"], params={"task_id": task_id},
                    headers=headers, timeout=10.0,
                )
                if poll.status_code != 200:
                    continue
                poll_data = poll.json()
                status    = poll_data.get("status", "")
                logger.info(f"Minimax poll gen={gen_id} attempt={attempt+1} status={status}")
                if status == "Success":
                    file_id = poll_data.get("file_id", "")
                    break
                if status in ("Fail", "Failed", "Cancelled"):
                    raise ProviderUnavailableError(f"Minimax {status} gen={gen_id}")
            else:
                raise ProviderUnavailableError(f"Minimax timeout gen={gen_id}")

            file_resp = await client.get(
                cfg["file_url"], params={"file_id": file_id},
                headers=headers, timeout=10.0,
            )
            if file_resp.status_code != 200:
                raise ProviderUnavailableError(f"Minimax file retrieve {file_resp.status_code} gen={gen_id}")
            video_url = file_resp.json().get("file", {}).get("download_url", "")
            if not video_url:
                raise ProviderUnavailableError(f"Minimax no download_url gen={gen_id}")

        logger.info(f"Minimax done gen={gen_id}")
        return GatewayResponse(video_url=video_url, model_used="minimax-hailuo", cost_inr=cfg["cost_inr"])

    async def _call_replicate_i2v(self, input_data: dict) -> GatewayResponse:
        cfg     = PROVIDER_CONFIG["replicate-wan"]
        api_key = os.environ.get(cfg["key_env"], "")
        gen_id  = input_data.get("gen_id", "")
        if not api_key:
            raise ProviderUnavailableError("REPLICATE_API_TOKEN not set")
        headers = {"Authorization": f"Token {api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=cfg["timeout_s"]) as client:
            submit = await client.post(
                cfg["submit_url"], headers=headers,
                json={
                    "version": cfg["model_version"],
                    "input": {
                        "image":  input_data.get("image_url", ""),
                        "prompt": input_data.get("prompt", ""),
                        "seed":   input_data.get("seed", 42),
                    },
                },
            )
            if submit.status_code not in (200, 201):
                raise ProviderUnavailableError(
                    f"Replicate submit {submit.status_code}: {submit.text[:300]}"
                )
            prediction_id = submit.json().get("id", "")
            if not prediction_id:
                raise ProviderUnavailableError(f"Replicate no prediction_id gen={gen_id}")
            logger.info(f"Replicate queued gen={gen_id} id={prediction_id}")

            for attempt in range(cfg["max_polls"]):
                await asyncio.sleep(cfg["poll_interval_s"])
                poll = await client.get(
                    cfg["poll_base"].format(prediction_id=prediction_id),
                    headers=headers, timeout=10.0,
                )
                if poll.status_code != 200:
                    continue
                poll_data = poll.json()
                status    = poll_data.get("status", "")
                logger.info(f"Replicate poll gen={gen_id} attempt={attempt+1} status={status}")
                if status == "succeeded":
                    output    = poll_data.get("output", [])
                    video_url = output[0] if output else ""
                    if not video_url:
                        raise ProviderUnavailableError(f"Replicate no output gen={gen_id}")
                    logger.info(f"Replicate done gen={gen_id}")
                    return GatewayResponse(video_url=video_url, model_used="replicate-wan", cost_inr=cfg["cost_inr"])
                if status in ("failed", "canceled"):
                    raise ProviderUnavailableError(
                        f"Replicate {status} gen={gen_id}: {poll_data.get('error','unknown')}"
                    )
            raise ProviderUnavailableError(f"Replicate timeout gen={gen_id}")


# ── Singleton factory ─────────────────────────────────────────────────────────

_gateway_instance: Optional[ModelGateway] = None


def get_gateway(redis_client=None) -> ModelGateway:
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = ModelGateway(redis_client=redis_client)
    return _gateway_instance


# ── Stub for CI (AW_API_MODE=stub) ───────────────────────────────────────────

class StubGateway:
    async def route(
        self, capability: str, input_data: dict, max_tokens: int = None
    ) -> GatewayResponse:
        raise NotImplementedError(
            f"StubGateway called capability='{capability}' "
            f"gen_id={input_data.get('gen_id')}"
        )
