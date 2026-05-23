"""
backend/app/workers/strategist.py
WorkerStrategist — Phase 3. Zero external API.
v4-delta1: 5-step atomic flow.
  1. Resolve active_season
  2. Resolve brand_tier + brand_color_primary
  3. Resolve structure_template (2D routing, T4 only on emotion+season)
  4. Call BRollPlanner 6-arg contract
  5. Atomic persist: b_roll_plan + structure_template + active_season
     + broll_clip_usage rows in one transaction
"""
import json
import uuid
import logging
from app.types.script import Script
from app.broll.planner import (
    BRollPlanner,
    BRollCoverageError,
    MOTION_NAMES,
    ENV_NAMES,
    COLD_START_DEFAULTS,
    DEFAULT_STYLE_FALLBACK,
)
from app.broll.templates import (
    TEMPLATE_BY_CONTEXT,
    DEFAULT_TEMPLATE,
    FESTIVE_TEMPLATE,
)

logger = logging.getLogger(__name__)

TTS_LANGUAGE_MAP: dict[str, str] = {
    "hindi":    "sarvam",
    "hinglish": "sarvam",
    "marathi":  "sarvam",
    "punjabi":  "sarvam",
    "bengali":  "sarvam",
    "tamil":    "sarvam",
    "telugu":   "sarvam",
    "english":  "elevenlabs",
}


class WorkerStrategist:
    def __init__(self, db_pool, redis_db3=None):
        self.db = db_pool
        self.redis_db3 = redis_db3
        self.broll_planner = BRollPlanner(db_pool)

    async def _get_best_i2v_provider(self, redis_db3, plan_tier: str) -> str:
        providers = ["fal_ai", "minimax"]
        if redis_db3 is None:
            return providers[0]
        try:
            best = providers[0]
            best_score = -1
            for p in providers:
                score_str = await redis_db3.get(f"health:i2v:{p}")
                score = int(score_str) if score_str else 70
                if score > best_score:
                    best_score = score
                    best = p
            return best
        except Exception as e:
            logger.warning(f"Redis DB3 health read failed: {e}. Using fal_ai.")
            return "fal_ai"

    async def _flag_enabled(self, flag_key: str) -> bool:
        """Read a boolean feature flag from the feature_flags table."""
        try:
            async with self.db.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT value FROM feature_flags WHERE key = $1",
                    flag_key
                )
            if row is None:
                return False
            val = row["value"]
            # value is JSONB — could be true (bool) or "true" (string)
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() == "true"
            return bool(val)
        except Exception as e:
            logger.warning(f"feature_flags read failed for {flag_key}: {e}. Defaulting False.")
            return False

    async def process(self, gen_id: str) -> dict:
        # ── Read generation row ───────────────────────────────────
        async with self.db.acquire() as conn:
            gen = await conn.fetchrow(
                """SELECT safe_scripts, selected_script_id,
                          motion_archetype_id, environment_preset_id,
                          tts_language, plan_tier, chat_turns_used,
                          cogs_total, product_brief, confidence_score,
                          routed_frameworks, routing_rationale,
                          user_id
                   FROM generations
                   WHERE gen_id = $1
                     AND status IN (
                         'scripts_ready'::job_status,
                         'strategy_preview'::job_status
                     )""",
                uuid.UUID(gen_id)
            )

        if gen is None:
            raise ValueError(
                f"Generation {gen_id} not found or not in scripts_ready state"
            )

        user_id = str(gen["user_id"])

        # ── Parse selected script ─────────────────────────────────
        safe_scripts_list = json.loads(gen["safe_scripts"])
        idx = (gen["selected_script_id"] or 1) - 1
        idx = max(0, min(idx, len(safe_scripts_list) - 1))
        selected_script = Script(**safe_scripts_list[idx])

        # ── Parse product brief ───────────────────────────────────
        product_brief = gen["product_brief"]
        if isinstance(product_brief, str):
            product_brief = json.loads(product_brief)
        category = product_brief.get("category", "packaged_food")

        # ── Cold-start style defaults ─────────────────────────────
        motion_id = gen["motion_archetype_id"]
        env_id = gen["environment_preset_id"]
        if motion_id is None or env_id is None:
            defaults = COLD_START_DEFAULTS.get(category, DEFAULT_STYLE_FALLBACK)
            motion_id = motion_id or defaults["motion_archetype_id"]
            env_id = env_id or defaults["environment_preset_id"]

        tts_language = gen["tts_language"] or "hindi"
        tts_provider = TTS_LANGUAGE_MAP.get(tts_language, "sarvam")
        i2v_provider = await self._get_best_i2v_provider(
            self.redis_db3, gen["plan_tier"]
        )
        framework_angle = selected_script.framework_angle

        # ── STEP 1: Resolve active_season ─────────────────────────
        active_season = None
        try:
            async with self.db.acquire() as conn:
                season_row = await conn.fetchrow(
                    """SELECT season_tag FROM seasons
                       WHERE is_active = TRUE
                         AND NOW()::DATE BETWEEN active_from AND active_to
                       ORDER BY season_tag
                       LIMIT 1"""
                )
            active_season = season_row["season_tag"] if season_row else None
        except Exception as e:
            logger.warning(f"seasons lookup failed for gen_id={gen_id}: {e}. Defaulting None.")

        # ── STEP 2: Resolve brand_tier + brand_color_primary ──────
        brand_tier = "mass"
        brand_color_primary = None
        try:
            async with self.db.acquire() as conn:
                style_row = await conn.fetchrow(
                    """SELECT brand_tier, brand_color_primary
                       FROM user_style_profiles
                       WHERE user_id = $1::uuid
                         AND category = $2
                       LIMIT 1""",
                    user_id, category
                )
            if style_row:
                brand_tier = style_row["brand_tier"] or "mass"
                brand_color_primary = style_row["brand_color_primary"]
        except Exception as e:
            logger.warning(
                f"user_style_profiles lookup failed for gen_id={gen_id}: {e}. "
                f"Defaulting brand_tier=mass."
            )

        # ── STEP 3: Resolve structure_template ────────────────────
        routing_enabled = await self._flag_enabled("broll_v4_routing_enabled")

        if not routing_enabled:
            # Feature flag off — T1 baseline, no routing
            structure_template = DEFAULT_TEMPLATE
        elif active_season and framework_angle == "emotion":
            # Festive override — only when ad angle is emotional
            structure_template = FESTIVE_TEMPLATE
        else:
            structure_template = TEMPLATE_BY_CONTEXT.get(
                (framework_angle, brand_tier),
                DEFAULT_TEMPLATE,
            )

        # ── STEP 4: Call BRollPlanner ─────────────────────────────
        b_roll_plan = None
        b_roll_available = False
        try:
            b_roll_plan = await self.broll_planner.plan(
                template=structure_template,
                angle=framework_angle,
                category=category,
                brand_tier=brand_tier,
                user_id=user_id,
                active_season=active_season,
            )
            b_roll_available = b_roll_plan.get("hook") is not None
        except BRollCoverageError as e:
            logger.error(
                f"BRollCoverageError for gen_id={gen_id}: {e}. "
                f"b_roll_plan will be null. Check clip library."
            )
            b_roll_plan = {
                "template": structure_template,
                "hook": None,
                "context": None,
                "cta": None,
            }
            b_roll_available = False
        except Exception as e:
            logger.error(
                f"BRollPlanner.plan failed for gen_id={gen_id}: {e}. "
                f"b_roll_plan will be null."
            )
            b_roll_plan = {
                "template": structure_template,
                "hook": None,
                "context": None,
                "cta": None,
            }
            b_roll_available = False

        # ── STEP 5: Atomic persist ────────────────────────────────
        # Single transaction:
        #   UPDATE generations (b_roll_plan, structure_template, active_season, strategy_card)
        #   INSERT broll_clip_usage for every non-null clip in the plan
        chat_cost = float(gen["chat_turns_used"] or 0) * 0.08
        cogs_so_far = float(gen["cogs_total"] or 0)
        phase4_estimate = 0.50
        total_estimate = cogs_so_far + chat_cost + phase4_estimate

        strategy_card = {
            "product_summary": {
                "name":       product_brief.get("product_name", ""),
                "category":   category,
                "confidence": float(gen["confidence_score"] or 0),
            },
            "script_summary": {
                "text":             selected_script.full_text[:120],
                "hook":             selected_script.hook,
                "cta":              selected_script.cta,
                "score":            selected_script.critic_score,
                "framework":        selected_script.framework,
                "framework_angle":  selected_script.framework_angle,
            },
            "frameworks_considered": {
                "selected":  gen["routed_frameworks"] or [],
                "rationale": gen["routing_rationale"] or {},
            },
            "voice": {
                "language": tts_language,
                "provider": tts_provider,
            },
            "motion": {
                "archetype_id": motion_id,
                "name":         MOTION_NAMES.get(motion_id, "Drift"),
            },
            "environment": {
                "preset_id": env_id,
                "name":      ENV_NAMES.get(env_id, "Clean White"),
            },
            "provider": {
                "i2v_primary": i2v_provider,
            },
            "cost_estimate": {
                "cogs_so_far_inr":    round(cogs_so_far, 4),
                "chat_cost_inr":      round(chat_cost, 4),
                "phase4_estimate_inr": phase4_estimate,
                "total_estimate_inr": round(total_estimate, 4),
            },
            "compliance": {
                "sgi":          True,
                "c2pa":         True,
                "it_rules_2026": True,
            },
            "chat_turns_used":    gen["chat_turns_used"] or 0,
            "b_roll_plan":        b_roll_plan,
            "b_roll_available":   b_roll_available,
            "structure_template": structure_template,
            "active_season":      active_season,
            "brand_color_primary": brand_color_primary,
        }

        b_roll_json      = json.dumps(b_roll_plan)
        strategy_card_json = json.dumps(strategy_card)

        async with self.db.acquire() as conn:
            async with conn.transaction():
                # UPDATE generations
                updated = await conn.execute(
                    """UPDATE generations
                       SET strategy_card      = $2::jsonb,
                           b_roll_plan        = $3::jsonb,
                           structure_template = $4,
                           active_season      = $5,
                           status             = 'strategy_preview',
                           updated_at         = NOW()
                       WHERE gen_id = $1
                         AND status IN (
                             'scripts_ready'::job_status,
                             'strategy_preview'::job_status
                         )""",
                    uuid.UUID(gen_id),
                    strategy_card_json,
                    b_roll_json,
                    structure_template,
                    active_season,
                )

                if updated == "UPDATE 0":
                    raise ValueError(
                        f"State drift: gen_id={gen_id} not in scripts_ready state"
                    )

                # INSERT broll_clip_usage for every non-null clip
                clips_to_log = [
                    b_roll_plan.get("hook"),
                    b_roll_plan.get("context"),
                    b_roll_plan.get("cta"),
                ]
                for clip in clips_to_log:
                    if clip and clip.get("clip_id"):
                        await conn.execute(
                            """INSERT INTO broll_clip_usage
                                   (user_id, clip_id, gen_id, used_at)
                               VALUES ($1::uuid, $2, $3::uuid, NOW())
                               ON CONFLICT (user_id, clip_id, gen_id) DO NOTHING""",
                            user_id,
                            clip["clip_id"],
                            gen_id,
                        )

        return strategy_card
