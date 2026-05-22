"""
backend/app/broll/templates.py
FOUNDER-EXCLUSIVE — CI-locked. Agent reads only, never edits.
Routing dict: (framework_angle, brand_tier) -> structure_template
Category is NOT a routing axis — it is a clip filter in planner.py.
"""
from typing import Literal

TemplateID = Literal["T1", "T2", "T3", "T4", "T5"]

# Slot durations in seconds per template (must sum to 15.0)
TEMPLATE_DURATIONS: dict[str, dict] = {
    "T1": {"hook": 3.0, "context": None, "i2v": 9.0,  "cta": 3.0},
    "T2": {"hook": 2.0, "context": None, "i2v": 10.0, "cta": 3.0},
    "T3": {"hook": 3.0, "context": 3.0,  "i2v": 6.0,  "cta": 3.0},
    "T4": {"hook": 3.0, "context": 4.0,  "i2v": 5.0,  "cta": 3.0},
    "T5": {"hook": 2.0, "context": None, "i2v": 10.0, "cta": 3.0},
}

# Required B-roll roles per template
# All templates now request cta_bg — real clip is primary, text-card is fallback
TEMPLATE_ROLES: dict[str, list[str]] = {
    "T1": ["hook", "cta_bg"],
    "T2": ["hook", "cta_bg"],
    "T3": ["hook", "context", "cta_bg"],
    "T4": ["hook", "context", "cta_bg"],
    "T5": ["hook", "cta_bg"],
}

# Template routing: (framework_angle, brand_tier) -> template_id
# Precedence applied in strategist.py:
#   (1) broll_v4_routing_enabled = FALSE  -> T1 short-circuit
#   (2) active_season + angle == emotion  -> T4
#   (3) this dict lookup
#   (4) DEFAULT_TEMPLATE fallback
TEMPLATE_BY_CONTEXT: dict[tuple[str, str], TemplateID] = {
    ("emotion",    "mass"):    "T1",
    ("emotion",    "premium"): "T2",
    ("emotion",    "luxury"):  "T2",
    ("logic",      "mass"):    "T3",
    ("logic",      "premium"): "T3",
    ("logic",      "luxury"):  "T2",
    ("conversion", "mass"):    "T5",
    ("conversion", "premium"): "T5",
    ("conversion", "luxury"):  "T2",
}

DEFAULT_TEMPLATE: TemplateID = "T1"
FESTIVE_TEMPLATE: TemplateID = "T4"

# Mood target per (template, role)
# Tells planner.py which mood_energy + mood_temperature to prefer
MOOD_BY_SLOT: dict[tuple[str, str], dict] = {
    ("T1", "hook"):    {"energy": "active",  "temperature": "warm"},
    ("T1", "cta_bg"):  {"energy": "calm",    "temperature": "warm"},
    ("T2", "hook"):    {"energy": "active",  "temperature": "cool"},
    ("T2", "cta_bg"):  {"energy": "calm",    "temperature": "cool"},
    ("T3", "hook"):    {"energy": "active",  "temperature": "neutral"},
    ("T3", "context"): {"energy": "calm",    "temperature": "neutral"},
    ("T3", "cta_bg"):  {"energy": "calm",    "temperature": "neutral"},
    ("T4", "hook"):    {"energy": "active",  "temperature": "warm"},
    ("T4", "context"): {"energy": "calm",    "temperature": "warm"},
    ("T4", "cta_bg"):  {"energy": "calm",    "temperature": "warm"},
    ("T5", "hook"):    {"energy": "intense", "temperature": "neutral"},
    ("T5", "cta_bg"):  {"energy": "calm",    "temperature": "neutral"},
}

# CTA copy per (template, brand_tier) — passed to _render_cta_text_card
CTA_COPY: dict[tuple[str, str], str] = {
    ("T5", "mass"):    "LIMITED TIME OFFER",
    ("T5", "premium"): "Exclusive Offer",
    ("T5", "luxury"):  "",
    ("T2", "premium"): "",
    ("T2", "luxury"):  "",
}
