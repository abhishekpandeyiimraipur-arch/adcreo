"""
backend/app/broll/planner.py
BRollPlanner — deterministic role-first B-roll clip selection.
v4-delta1: 6-arg contract. Role-based SQL per slot. Rotation-aware.
Zero LLM. Zero external API. Pure SQL.
"""
import logging
from typing import Optional
from app.broll.templates import (
    TEMPLATE_DURATIONS,
    TEMPLATE_ROLES,
    MOOD_BY_SLOT,
)

logger = logging.getLogger(__name__)

# ── Motion Archetype Constants ────────────────────────────────────
MOTION_NAMES: dict[int, str] = {
    1: "Orbit",
    2: "Drift",
    3: "Hero Zoom",
    4: "Unbox",
    5: "Liquid Pour",
}

# ── Environment Preset Constants ─────────────────────────────────
ENV_NAMES: dict[int, str] = {
    1: "Clean White",
    2: "Minimal Studio",
    3: "Kitchen Warm",
    4: "Outdoor Natural",
    5: "Living Room Warm",
    6: "Outdoor Fashion",
    7: "Home Interior",
    8: "Product Focus",
}

# ── Cold-Start Style Defaults (BEF GAP-12) ───────────────────────
COLD_START_DEFAULTS: dict[str, dict] = {
    "packaged_food":    {"motion_archetype_id": 2, "environment_preset_id": 3},
    "d2c_beauty":       {"motion_archetype_id": 4, "environment_preset_id": 1},
    "electronics":      {"motion_archetype_id": 1, "environment_preset_id": 2},
    "hard_accessories": {"motion_archetype_id": 3, "environment_preset_id": 2},
    "home_kitchen":     {"motion_archetype_id": 2, "environment_preset_id": 3},
}
DEFAULT_STYLE_FALLBACK = {"motion_archetype_id": 2, "environment_preset_id": 1}


class BRollCoverageError(Exception):
    """Raised when hook slot returns zero active clips. Deploy-time CI catches this."""
    pass


class BRollPlanner:
    """
    Deterministic role-first B-roll clip selection.

    plan(template, angle, category, brand_tier, user_id, active_season)
    -> {template, hook, context, cta}

    hook  : always non-null (raises BRollCoverageError if no clip found)
    context: non-null for T3, T4 only
    cta   : non-null when a cta_bg clip exists; None triggers text-card fallback
    """

    def __init__(self, db_pool):
        self.db = db_pool

    async def plan(
        self,
        template: str,
        angle: str,
        category: str,
        brand_tier: str,
        user_id: str,
        active_season: Optional[str],
    ) -> dict:
        required_roles = TEMPLATE_ROLES[template]
        durations = TEMPLATE_DURATIONS[template]

        result: dict = {
            "template": template,
            "hook": None,
            "context": None,
            "cta": None,
        }

        for role in required_roles:
            mood = MOOD_BY_SLOT.get(
                (template, role),
                {"energy": "calm", "temperature": "neutral"}
            )
            required_duration_ms = int(
                self._slot_duration_for_role(role, durations) * 1000
            )
            is_festive_slot = (
                template == "T4" and role in ("hook", "context")
            )

            clip = await self._pick_one(
                role=role,
                category=category,
                brand_tier=brand_tier,
                mood_energy=mood["energy"],
                mood_temperature=mood["temperature"],
                required_duration_ms=required_duration_ms,
                user_id=user_id,
                active_season=active_season if is_festive_slot else None,
            )

            # Festive slot fallback to year-round
            if clip is None and is_festive_slot:
                logger.warning(
                    f"BRollPlanner: no festive clip for role={role} "
                    f"season={active_season} category={category}. "
                    f"Falling back to year-round."
                )
                clip = await self._pick_one(
                    role=role,
                    category=category,
                    brand_tier=brand_tier,
                    mood_energy=mood["energy"],
                    mood_temperature=mood["temperature"],
                    required_duration_ms=required_duration_ms,
                    user_id=user_id,
                    active_season=None,
                )

            # Hook is mandatory
            if clip is None and role == "hook":
                raise BRollCoverageError(
                    f"No active hook clip for category={category} "
                    f"brand_tier={brand_tier}. "
                    f"Run ci/broll_coverage_check.py to diagnose."
                )

            if clip is None:
                logger.warning(
                    f"BRollPlanner: no clip found for role={role} "
                    f"template={template} category={category} "
                    f"brand_tier={brand_tier}. Slot will be None."
                )
                continue

            if role == "hook":
                result["hook"] = clip
            elif role == "context":
                result["context"] = clip
            elif role == "cta_bg":
                result["cta"] = clip

        return result

    async def _pick_one(
        self,
        role: str,
        category: str,
        brand_tier: str,
        mood_energy: str,
        mood_temperature: str,
        required_duration_ms: int,
        user_id: str,
        active_season: Optional[str],
    ) -> Optional[dict]:
        """
        One SQL query per slot.
        Order: mood match score DESC, rotation (least recently used first),
               clip_id ASC as deterministic tiebreak.
        """
        try:
            async with self.db.acquire() as conn:
                if active_season:
                    row = await conn.fetchrow(
                        """
                        SELECT
                            bc.clip_id,
                            bc.r2_url,
                            bc.duration_ms,
                            bc.archetype,
                            bc.role,
                            bc.mood_energy,
                            bc.mood_temperature,
                            bc.negative_space_score,
                            bc.seasonality_tags,
                            bc.brand_tier_fit,
                            bc.trim_start_ms,
                            bc.has_ambient_audio,
                            bc.visual_tone,
                            CASE
                                WHEN bc.mood_energy = $4
                                 AND bc.mood_temperature = $5 THEN 2
                                WHEN bc.mood_energy = $4 THEN 1
                                ELSE 0
                            END AS mood_score,
                            MAX(bcu.used_at) AS last_used_at
                        FROM broll_clips bc
                        LEFT JOIN broll_clip_usage bcu
                            ON bcu.clip_id = bc.clip_id
                           AND bcu.user_id = $6::uuid
                        WHERE bc.role      = $1
                          AND bc.category  = $2::green_zone_category
                          AND $3           = ANY(bc.brand_tier_fit)
                          AND bc.is_active = TRUE
                          AND bc.duration_ms >= $7
                          AND $8           = ANY(bc.seasonality_tags)
                        GROUP BY bc.clip_id
                        ORDER BY
                            mood_score DESC,
                            last_used_at ASC NULLS FIRST,
                            bc.clip_id ASC
                        LIMIT 1
                        """,
                        role, category, brand_tier,
                        mood_energy, mood_temperature,
                        str(user_id),
                        required_duration_ms,
                        active_season,
                    )
                else:
                    row = await conn.fetchrow(
                        """
                        SELECT
                            bc.clip_id,
                            bc.r2_url,
                            bc.duration_ms,
                            bc.archetype,
                            bc.role,
                            bc.mood_energy,
                            bc.mood_temperature,
                            bc.negative_space_score,
                            bc.seasonality_tags,
                            bc.brand_tier_fit,
                            bc.trim_start_ms,
                            bc.has_ambient_audio,
                            bc.visual_tone,
                            CASE
                                WHEN bc.mood_energy = $4
                                 AND bc.mood_temperature = $5 THEN 2
                                WHEN bc.mood_energy = $4 THEN 1
                                ELSE 0
                            END AS mood_score,
                            MAX(bcu.used_at) AS last_used_at
                        FROM broll_clips bc
                        LEFT JOIN broll_clip_usage bcu
                            ON bcu.clip_id = bc.clip_id
                           AND bcu.user_id = $6::uuid
                        WHERE bc.role      = $1
                          AND bc.category  = $2::green_zone_category
                          AND $3           = ANY(bc.brand_tier_fit)
                          AND bc.is_active = TRUE
                          AND bc.duration_ms >= $7
                        GROUP BY bc.clip_id
                        ORDER BY
                            mood_score DESC,
                            last_used_at ASC NULLS FIRST,
                            bc.clip_id ASC
                        LIMIT 1
                        """,
                        role, category, brand_tier,
                        mood_energy, mood_temperature,
                        str(user_id),
                        required_duration_ms,
                    )

                if row is None:
                    return None

                return {
                    "clip_id":              row["clip_id"],
                    "r2_url":               row["r2_url"],
                    "duration_ms":          row["duration_ms"],
                    "archetype":            row["archetype"],
                    "role":                 row["role"],
                    "mood_energy":          row["mood_energy"],
                    "mood_temperature":     row["mood_temperature"],
                    "negative_space_score": row["negative_space_score"],
                    "seasonality_tags":     list(row["seasonality_tags"] or []),
                    "brand_tier_fit":       list(row["brand_tier_fit"] or []),
                    "trim_start_ms":        row["trim_start_ms"],
                    "has_ambient_audio":    row["has_ambient_audio"],
                    "visual_tone":          row["visual_tone"],
                }

        except BRollCoverageError:
            raise
        except Exception as e:
            logger.error(
                f"BRollPlanner._pick_one failed: role={role} "
                f"category={category} brand_tier={brand_tier}: {e}"
            )
            return None

    @staticmethod
    def _slot_duration_for_role(role: str, durations: dict) -> float:
        mapping = {
            "hook":    durations["hook"],
            "context": durations["context"] or 0.0,
            "cta_bg":  durations["cta"],
        }
        return mapping.get(role, 3.0)
