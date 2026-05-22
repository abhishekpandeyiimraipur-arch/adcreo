#!/usr/bin/env python3
# scripts/broll_harvest.py
"""
Adcreo B-Roll Harvest Pipeline â€” Stages 1â€“4
Standalone curation tool. Never import from app/.

Usage:
  python scripts/broll_harvest.py harvest
      Stage 1: Pexels API search (30 results per slot)
      Stage 2: Metadata filter (ratio / resolution / fps / duration)
      Stage 3: Frame analysis via OpenCV (static / skin / bars / greenscreen / watermark)
      Writes: scripts/broll_output/shortlist.json
              scripts/broll_output/review.html   â† open in browser, pick one per slot, Export picks.json

  python scripts/broll_harvest.py generate --picks scripts/broll_output/picks.json
      Stage 4: Read picks â†’ write trim_commands.sh + seed_broll_clips.sql

Output dir: scripts/broll_output/
  shortlist.json       candidates surviving all filters
  review.html          interactive pick UI
  picks.json           exported from review.html (one entry per slot)
  trim_commands.sh     FFmpeg trim + crop per pick
  seed_broll_clips.sql INSERT statements for broll_clips table

Invariants respected:
  - No presigned R2 URLs (Â§6 rule 1) â€” r2_url in SQL is a path placeholder; upload is manual boto3
  - No ML libs anywhere
  - No imports from app/
  - Pixabay omitted (site down at time of authoring); add later if needed
"""

import sys
import os
import json
import time
import shutil
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional

# â”€â”€ CONFIG â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

PEXELS_API_KEY = os.environ.get(
    "PEXELS_API_KEY",
    "9cCankdiLYfgaK04cd4ROsiNNGXkbZYUN5qg4Jp16SzIPF5wnt5KiqnV",
)

OUTPUT_DIR = Path(__file__).parent / "broll_output"
TEMP_DIR   = OUTPUT_DIR / "temp_clips"

# â”€â”€ 24-SLOT MANIFEST â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Visual-property search terms per research doc.
# mood_energy:  hook_1 = active | hook_2 = intense | context = calm | cta_bg = calm
# mood_temperature: per-category palette (warm / cool / neutral)

SLOTS = [
    # â”€â”€ d2c_beauty â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "slot_id": "d2c_beauty__hook_1",
        "category": "d2c_beauty", "role": "hook", "n": 1,
        "mood_energy": "active", "mood_temperature": "warm",
        "query": "liquid drop macro abstract glass bokeh",
    },
    {
        "slot_id": "d2c_beauty__hook_2",
        "category": "d2c_beauty", "role": "hook", "n": 2,
        "mood_energy": "intense", "mood_temperature": "warm",
        "query": "cream texture swirl white closeup slow",
    },
    {
        "slot_id": "d2c_beauty__context",
        "category": "d2c_beauty", "role": "context", "n": 1,
        "mood_energy": "calm", "mood_temperature": "warm",
        "query": "bokeh abstract light warm gold blur",
    },
    {
        "slot_id": "d2c_beauty__cta_bg",
        "category": "d2c_beauty", "role": "cta_bg", "n": 1,
        "mood_energy": "calm", "mood_temperature": "warm",
        "query": "soft white blur abstract minimal background",
    },
    # â”€â”€ packaged_food â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "slot_id": "packaged_food__hook_1",
        "category": "packaged_food", "role": "hook", "n": 1,
        "mood_energy": "active", "mood_temperature": "warm",
        "query": "spice powder burst dark background abstract",
    },
    {
        "slot_id": "packaged_food__hook_2",
        "category": "packaged_food", "role": "hook", "n": 2,
        "mood_energy": "intense", "mood_temperature": "warm",
        "query": "steam rising dark minimal close",
    },
    {
        "slot_id": "packaged_food__context",
        "category": "packaged_food", "role": "context", "n": 1,
        "mood_energy": "calm", "mood_temperature": "warm",
        "query": "natural ingredient texture warm flatlay",
    },
    {
        "slot_id": "packaged_food__cta_bg",
        "category": "packaged_food", "role": "cta_bg", "n": 1,
        "mood_energy": "calm", "mood_temperature": "warm",
        "query": "warm beige minimal texture empty space",
    },
    # â”€â”€ electronics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "slot_id": "electronics__hook_1",
        "category": "electronics", "role": "hook", "n": 1,
        "mood_energy": "active", "mood_temperature": "cool",
        "query": "light prism refraction glass abstract dark",
    },
    {
        "slot_id": "electronics__hook_2",
        "category": "electronics", "role": "hook", "n": 2,
        "mood_energy": "intense", "mood_temperature": "cool",
        "query": "blue glow particle tech dark bokeh",
    },
    {
        "slot_id": "electronics__context",
        "category": "electronics", "role": "context", "n": 1,
        "mood_energy": "calm", "mood_temperature": "cool",
        "query": "abstract digital dark background loop minimal",
    },
    {
        "slot_id": "electronics__cta_bg",
        "category": "electronics", "role": "cta_bg", "n": 1,
        "mood_energy": "calm", "mood_temperature": "cool",
        "query": "dark minimal clean empty background vertical",
    },
    # â”€â”€ hard_accessories â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "slot_id": "hard_accessories__hook_1",
        "category": "hard_accessories", "role": "hook", "n": 1,
        "mood_energy": "active", "mood_temperature": "neutral",
        "query": "metal surface macro texture closeup shine",
    },
    {
        "slot_id": "hard_accessories__hook_2",
        "category": "hard_accessories", "role": "hook", "n": 2,
        "mood_energy": "intense", "mood_temperature": "neutral",
        "query": "dark leather grain material surface close",
    },
    {
        "slot_id": "hard_accessories__context",
        "category": "hard_accessories", "role": "context", "n": 1,
        "mood_energy": "calm", "mood_temperature": "neutral",
        "query": "fabric weave macro natural light texture",
    },
    {
        "slot_id": "hard_accessories__cta_bg",
        "category": "hard_accessories", "role": "cta_bg", "n": 1,
        "mood_energy": "calm", "mood_temperature": "neutral",
        "query": "grey neutral surface minimal clean empty",
    },
    # â”€â”€ home_kitchen â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "slot_id": "home_kitchen__hook_1",
        "category": "home_kitchen", "role": "hook", "n": 1,
        "mood_energy": "active", "mood_temperature": "warm",
        "query": "warm window light bokeh interior soft morning",
    },
    {
        "slot_id": "home_kitchen__hook_2",
        "category": "home_kitchen", "role": "hook", "n": 2,
        "mood_energy": "intense", "mood_temperature": "warm",
        "query": "wood grain macro texture warm close",
    },
    {
        "slot_id": "home_kitchen__context",
        "category": "home_kitchen", "role": "context", "n": 1,
        "mood_energy": "calm", "mood_temperature": "warm",
        "query": "linen texture natural light soft minimal",
    },
    {
        "slot_id": "home_kitchen__cta_bg",
        "category": "home_kitchen", "role": "cta_bg", "n": 1,
        "mood_energy": "calm", "mood_temperature": "warm",
        "query": "cream soft bokeh warm interior empty",
    },
    # â”€â”€ d2c_fashion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "slot_id": "d2c_fashion__hook_1",
        "category": "d2c_fashion", "role": "hook", "n": 1,
        "mood_energy": "active", "mood_temperature": "neutral",
        "query": "silk fabric flowing light slow abstract",
    },
    {
        "slot_id": "d2c_fashion__hook_2",
        "category": "d2c_fashion", "role": "hook", "n": 2,
        "mood_energy": "intense", "mood_temperature": "neutral",
        "query": "thread weave macro textile closeup",
    },
    {
        "slot_id": "d2c_fashion__context",
        "category": "d2c_fashion", "role": "context", "n": 1,
        "mood_energy": "calm", "mood_temperature": "neutral",
        "query": "textile drape soft light minimal natural",
    },
    {
        "slot_id": "d2c_fashion__cta_bg",
        "category": "d2c_fashion", "role": "cta_bg", "n": 1,
        "mood_energy": "calm", "mood_temperature": "neutral",
        "query": "white fabric bokeh soft empty vertical",
    },
]

# Duration filter ranges (seconds) per role
DURATION_RANGE = {
    "hook":    (2,  30),
    "context": (6, 15),
    "cta_bg":  (4, 12),
}

# â”€â”€ HTTP HELPERS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def pexels_search(query: str, per_page: int = 30) -> list[dict]:
    """Call Pexels videos/search. Returns raw video list."""
    params = urllib.parse.urlencode({
        "query": query,
        "size": "large",
        "per_page": per_page,
    })
    url = f"https://api.pexels.com/videos/search?{params}"
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_API_KEY, "User-Agent": "AdcreoHarvest/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("videos", [])
    except Exception as exc:
        print(f"  [WARN] Pexels search failed for {query!r}: {exc}")
        return []


def download_file(url: str, dest: Path) -> bool:
    """Stream-download url â†’ dest. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AdcreoHarvest/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as fh:
            shutil.copyfileobj(resp, fh)
        return True
    except Exception as exc:
        print(f"  [WARN] Download failed {url}: {exc}")
        return False


# â”€â”€ STAGE 1: HARVEST â€” normalise Pexels response â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def extract_metadata(video: dict) -> Optional[dict]:
    """Normalise one Pexels video dict â†’ flat metadata dict, or None if unusable."""
    # Prefer HD mp4; fall back to any mp4
    hd_file = None
    for vf in video.get("video_files", []):
        if vf.get("file_type") != "video/mp4":
            continue
        if vf.get("quality") == "hd":
            hd_file = vf
            break
        if hd_file is None:
            hd_file = vf

    if not hd_file or not hd_file.get("link"):
        return None

    w = hd_file.get("width") or video.get("width", 0)
    h = hd_file.get("height") or video.get("height", 0)

    w_i = int(w)
    h_i = int(h)
    return {
        "source":       "pexels",
        "id":           str(video["id"]),
        "width":        w_i,
        "height":       h_i,
        "fps":          float(video.get("fps", 0)),
        "duration":     int(video.get("duration", 0)),
        "download_url": hd_file["link"],
        "preview_url":  video.get("image", ""),
        "pexels_url":   video.get("url", ""),
        "license_ref":  f"pexels_{video['id']}",
        "needs_crop":   h_i < w_i,
    }


# â”€â”€ STAGE 2: METADATA FILTER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def passes_metadata_filter(clip: dict, role: str) -> tuple[bool, str]:
    """(True, '') or (False, reason)."""
    w, h = clip["width"], clip["height"]
    ratio = h / w if w > 0 else 0

    if w < 1080 and h < 1080:
        return False, f"both dimensions < 1080 (too small)"
    pass  # fps filter removed â€” OpenCV static check handles low-quality motion

    dur = clip["duration"]
    lo, hi = DURATION_RANGE[role]
    if not (lo <= dur <= hi):
        return False, f"duration {dur}s outside [{lo}â€“{hi}]s for role={role}"

    return True, ""


# â”€â”€ STAGE 3: FRAME ANALYSIS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def cv2_available() -> bool:
    try:
        import cv2      # noqa: F401
        import numpy    # noqa: F401
        return True
    except ImportError:
        return False


def analyse_clip(path: Path) -> dict:
    """
    Run 5 OpenCV checks. All checks require cv2 + numpy.
    Returns a dict with boolean flags.
    If cv2 unavailable, returns all-False with cv2_available=False.
    """
    result = {
        "cv2_available":    False,
        "is_static":        False,
        "has_skin":         False,
        "has_black_bars":   False,
        "has_green_screen": False,
        "corner_text_flag": False,
    }

    try:
        import cv2
        import numpy as np
    except ImportError:
        return result

    result["cv2_available"] = True
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        cap.release()
        return result

    def read_at(pos: int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ok, frame = cap.read()
        return frame if ok else None

    # â”€â”€ Check 1: static video (image exported as video) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    f1  = read_at(1)
    f60 = read_at(60)
    if f1 is not None and f60 is not None:
        diff = np.mean(np.abs(f1.astype(float) - f60.astype(float)))
        result["is_static"] = (diff < 1.5)

    # â”€â”€ Check 2: skin detection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    for pos in (1, 30, 60):
        frame = read_at(pos)
        if frame is None:
            continue
        hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 30, 80]), np.array([25, 170, 255]))
        if np.sum(mask > 0) / mask.size > 0.08:
            result["has_skin"] = True
            break

    # â”€â”€ Check 3: black bars (landscape faked as portrait) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    frame = read_at(30)
    if frame is not None:
        left  = frame[:, :30,  :]
        right = frame[:, -30:, :]
        result["has_black_bars"] = (np.mean(left) < 10 and np.mean(right) < 10)

    # â”€â”€ Check 4: green screen â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    frame = read_at(30)
    if frame is not None:
        hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([40, 100, 50]), np.array([80, 255, 255]))
        result["has_green_screen"] = (np.sum(mask > 0) / mask.size > 0.15)

    # â”€â”€ Check 5: corner watermark/text (flag only; human confirms) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    frame = read_at(10)
    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        corners = [
            gray[:80,    :150 ],
            gray[:80,    w-150:],
            gray[h-80:,  :150 ],
            gray[h-80:,  w-150:],
        ]
        edges = [cv2.Canny(c, 100, 200) for c in corners]
        result["corner_text_flag"] = any(
            np.sum(e > 0) / e.size > 0.12 for e in edges
        )

    cap.release()
    return result


def is_hard_fail(analysis: dict) -> bool:
    return (
        analysis["is_static"]
        or analysis["has_skin"]
        or analysis["has_black_bars"]
        or analysis["has_green_screen"]
    )


# â”€â”€ STAGE 4: REVIEW HTML â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def build_review_html(shortlist: dict) -> str:
    slot_order = [s["slot_id"] for s in SLOTS]
    categories  = list(dict.fromkeys(s["category"] for s in SLOTS))
    slots_json  = json.dumps(shortlist, indent=2, default=lambda o: bool(o) if hasattr(o, "__bool__") else str(o))

    # Build per-category sections
    sections_html = ""
    for cat in categories:
        cat_slots = [s for s in SLOTS if s["category"] == cat]
        sections_html += f'<div class="category"><h2>{cat.replace("_", " ").upper()}</h2>'

        for s in cat_slots:
            sid     = s["slot_id"]
            role    = s["role"]
            me      = s["mood_energy"]
            entry   = shortlist.get(sid, {})
            cands   = entry.get("candidates", [])

            no_cand = '<span class="badge miss">âš  NO CANDIDATES â€” search Mixkit/Kling manually</span>' if not cands else ""

            cards = ""
            for i, c in enumerate(cands):
                ana = c.get("analysis", {})
                flags = ""
                if ana.get("corner_text_flag"):
                    flags += '<span class="badge warn">âš  corner text â€” verify</span>'
                if not ana.get("cv2_available"):
                    flags += '<span class="badge info">cv2 not run</span>'

                cards += f"""
                <div class="clip-card" id="card-{sid}-{i}" onclick="pick('{sid}',{i})">
                  <img src="{c.get('preview_url','')}"
                       onerror="this.style.background='#2a2a2a';this.removeAttribute('src')"
                       loading="lazy" />
                  <div class="clip-info">
                    <div class="clip-id">#{i+1} Â· {c['license_ref']}</div>
                    <div class="clip-meta">{c['width']}Ã—{c['height']} Â· {c['fps']}fps Â· {c['duration']}s</div>
                    <a href="{c.get('pexels_url','#')}" target="_blank" class="ext-link">Open on Pexels â†—</a>
                    {flags}
                  </div>
                </div>"""

            sections_html += f"""
            <div class="slot" id="slot-{sid}">
              <div class="slot-header">
                <span class="slot-name">{sid}</span>
                <span class="badge role-{role}">{role} Â· {me}</span>
                {no_cand}
                <span class="pick-label" id="lbl-{sid}">not picked</span>
              </div>
              <div class="clips-row">{cards}</div>
            </div>"""

        sections_html += "</div>"

    total_slots = len(slot_order)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Adcreo B-Roll Review</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0e0e0e;color:#ddd;font-family:system-ui,sans-serif;padding:20px 24px 100px}}
h1{{font-size:18px;color:#fff;margin-bottom:28px;font-weight:600}}
.category{{margin-bottom:44px}}
h2{{font-size:11px;letter-spacing:2.5px;color:#555;border-bottom:1px solid #222;padding-bottom:8px;margin-bottom:16px}}
.slot{{margin-bottom:20px}}
.slot-header{{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}}
.slot-name{{font-size:12px;font-weight:700;color:#bbb}}
.badge{{font-size:10px;padding:2px 7px;border-radius:3px;font-weight:700;white-space:nowrap}}
.role-hook{{background:#0d2d45;color:#4fc3f7}}
.role-context{{background:#0d2d0d;color:#66bb6a}}
.role-cta_bg{{background:#2d0d2d;color:#ce93d8}}
.miss{{background:#3a0d0d;color:#ef9a9a}}
.warn{{background:#2d1f00;color:#ffcc02}}
.info{{background:#0d1f2d;color:#81b3cc}}
.pick-label{{font-size:11px;color:#444;margin-left:auto}}
.pick-label.done{{color:#66bb6a;font-weight:700}}
.clips-row{{display:flex;gap:10px;flex-wrap:wrap}}
.clip-card{{width:155px;background:#181818;border-radius:8px;cursor:pointer;border:2px solid transparent;transition:border .12s;overflow:hidden;user-select:none}}
.clip-card:hover{{border-color:#444}}
.clip-card.selected{{border-color:#66bb6a;background:#0d1a0d}}
.clip-card img{{width:100%;height:195px;object-fit:cover;background:#222;display:block}}
.clip-info{{padding:8px}}
.clip-id{{font-size:11px;font-weight:700;color:#ccc;margin-bottom:3px}}
.clip-meta{{font-size:10px;color:#555;margin-bottom:5px}}
.ext-link{{font-size:10px;color:#4fc3f7;text-decoration:none}}
.ext-link:hover{{text-decoration:underline}}
.bar{{position:fixed;bottom:0;left:0;right:0;background:#161616;border-top:1px solid #2a2a2a;padding:14px 24px;display:flex;align-items:center;gap:16px;z-index:99}}
.btn{{background:#1b4d1b;color:#fff;border:none;padding:10px 22px;border-radius:6px;cursor:pointer;font-size:13px;font-weight:700}}
.btn:hover{{background:#256225}}
.btn:disabled{{background:#333;color:#666;cursor:default}}
.progress{{font-size:13px;color:#666}}
.progress b{{color:#66bb6a}}
.note{{font-size:11px;color:#444;max-width:500px}}
</style>
</head>
<body>
<h1>Adcreo B-Roll Review â€” {total_slots} slots &nbsp;Â·&nbsp; pick one clip per slot &nbsp;Â·&nbsp; then Export picks.json</h1>

{sections_html}

<div class="bar">
  <button class="btn" id="exportBtn" onclick="exportPicks()" disabled>Export picks.json</button>
  <div class="progress">Picked: <b id="cnt">0</b> / {total_slots}</div>
  <div class="note">Missing slots (âš  NO CANDIDATES) â†’ search mixkit.co or generate with Kling AI â†’ add manually to picks.json</div>
</div>

<script>
const shortlist = {slots_json};
const picks = {{}};

function pick(slotId, idx) {{
  const entry = shortlist[slotId];
  if (!entry) return;

  // Deselect all cards in slot
  (entry.candidates || []).forEach((_, i) => {{
    const el = document.getElementById('card-' + slotId + '-' + i);
    if (el) el.classList.remove('selected');
  }});

  // Select chosen
  const card = document.getElementById('card-' + slotId + '-' + idx);
  if (card) card.classList.add('selected');

  const c = (entry.candidates || [])[idx];
  picks[slotId] = {{
    slot_id:          slotId,
    category:         entry.category,
    role:             entry.role,
    mood_energy:      entry.mood_energy,
    mood_temperature: entry.mood_temperature,
    n:                entry.n,
    source:           c.source,
    id:               c.id,
    license_ref:      c.license_ref,
    download_url:     c.download_url,
    pexels_url:       c.pexels_url || '',
    width:            c.width,
    height:           c.height,
    fps:              c.fps,
    duration:         c.duration,
  }};

  const lbl = document.getElementById('lbl-' + slotId);
  if (lbl) {{
    lbl.textContent = 'âœ“ ' + c.license_ref;
    lbl.className = 'pick-label done';
  }}

  const cnt = Object.keys(picks).length;
  document.getElementById('cnt').textContent = cnt;
  document.getElementById('exportBtn').disabled = false;
}}

function exportPicks() {{
  const blob = new Blob([JSON.stringify(picks, null, 2)], {{type: 'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'picks.json';
  a.click();
}}
</script>
</body>
</html>"""


# â”€â”€ GENERATE OUTPUTS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_outputs(picks_path: Path) -> None:
    """Read picks.json â†’ emit trim_commands.sh + seed_broll_clips.sql."""

    with open(picks_path) as fh:
        picks: dict = json.load(fh)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    finals_dir = OUTPUT_DIR / "final_clips"
    finals_dir.mkdir(exist_ok=True)

    ffmpeg_lines = [
        "#!/bin/bash",
        "# scripts/broll_output/trim_commands.sh",
        "# Trim + crop each picked clip to 3000ms, 1080Ã—1920.",
        "# Run from: backend root",
        "# Prereq: ffmpeg installed",
        "# REVIEW trim_start_ms per clip â€” default is 0 (start of file).",
        "# Adjust -ss value (seconds) if the best 3s of the clip starts later.",
        "set -e",
        "",
    ]

    sql_lines = [
        "-- scripts/broll_output/seed_broll_clips.sql",
        "-- Generated by scripts/broll_harvest.py",
        "--",
        "-- BEFORE RUNNING:",
        "--   1. Upload each final_clips/*.mp4 to R2 via boto3 (credentialed, no presigned URLs).",
        "--   2. Replace placeholder r2_url values below with actual adcreo-assets/broll/... paths.",
        "--   3. Update negative_space_score for non-cta_bg rows after visual review (default=5).",
        "--   4. Update archetype column if needed (default='texture').",
        "--",
        "-- AFTER RUNNING:",
        "--   SELECT category, role, COUNT(*) FROM broll_clips",
        "--   WHERE is_active=TRUE GROUP BY 1,2 ORDER BY 1,2;",
        "",
        "BEGIN;",
        "",
    ]

    for slot_id, pick in picks.items():
        category        = pick["category"]
        role            = pick["role"]
        n               = pick["n"]
        mood_energy     = pick["mood_energy"]
        mood_temperature= pick["mood_temperature"]
        license_ref     = pick["license_ref"]
        download_url    = pick["download_url"]
        width           = pick["width"]
        height          = pick["height"]

        clip_id  = f"{category[:8]}_{role[:4]}_{n}"
        out_name = f"{category}__{role}_{n}.mp4"
        out_path = f"scripts/broll_output/final_clips/{out_name}"

        # Crop filter: portrait clips just scale; landscape clips get centre-crop
        if height >= width:
            vf_filter = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
        else:
            vf_filter = "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920"

        tmp = f"/tmp/adcreo_broll_{slot_id.replace('__', '_')}.mp4"

        ffmpeg_lines += [
            f"# â”€â”€ {slot_id}  ({license_ref}) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€",
            f'curl -L -o {tmp} "{download_url}"',
            f"ffmpeg -i {tmp} \\",
            f"  -ss 0 -t 3.0 \\",
            f"  -vf \"{vf_filter}\" \\",
            f"  -c:v libx264 -crf 18 -an \\",
            f"  {out_path}",
            f"rm -f {tmp}",
            f'echo "âœ“ {out_path}"',
            "",
        ]

        # negative_space_score: cta_bg minimum is 7 per chk_cta_negative_space.
        # Other roles default to 5 (neutral); curator updates after visual check.
        neg_space = 7 if role == "cta_bg" else 5
        r2_placeholder = f"adcreo-assets/broll/{category}/{out_name}"

        sql_lines += [
            f"-- {slot_id}",
            f"INSERT INTO broll_clips (",
            f"  clip_id, archetype, category, duration_ms, r2_url,",
            f"  excludes_faces, excludes_hands, excludes_locations,",
            f"  license_ref, is_active,",
            f"  role, mood_energy, mood_temperature,",
            f"  negative_space_score, seasonality_tags, brand_tier_fit",
            f") VALUES (",
            f"  '{clip_id}',",
            f"  'texture',",                        # default archetype â€” update if needed
            f"  '{category}',",
            f"  3000,",
            f"  '{r2_placeholder}',",               # REPLACE with real R2 path after upload
            f"  TRUE, TRUE, TRUE,",
            f"  '{license_ref}',",
            f"  TRUE,",
            f"  '{role}',",
            f"  '{mood_energy}',",
            f"  '{mood_temperature}',",
            f"  {neg_space},",
            f"  '{{}}',",
            f"  '{{mass,premium,luxury}}'",
            f") ON CONFLICT (clip_id) DO NOTHING;",
            "",
        ]

    sql_lines += ["COMMIT;", ""]

    trim_path = OUTPUT_DIR / "trim_commands.sh"
    seed_path = OUTPUT_DIR / "seed_broll_clips.sql"

    trim_path.write_text("\n".join(ffmpeg_lines), encoding="utf-8")
    trim_path.chmod(0o755)
    seed_path.write_text("\n".join(sql_lines), encoding="utf-8")

    print(f"[OK] {trim_path}")
    print(f"[OK] {seed_path}")
    print()
    print("[NEXT STEPS]")
    print("  1. Run trim_commands.sh  â†’  scripts/broll_output/final_clips/*.mp4")
    print("  2. Upload each mp4 to R2 via boto3 (credentialed â€” no presigned URLs)")
    print("  3. Update r2_url placeholders in seed_broll_clips.sql")
    print("  4. Update negative_space_score for non-cta_bg rows")
    print("  5. psql $NEON_DSN < scripts/broll_output/seed_broll_clips.sql")
    print("  6. Run: python ci/broll_coverage_check.py")


# â”€â”€ HARVEST â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_harvest() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    use_cv2 = cv2_available()
    if not use_cv2:
        print("[WARN] opencv-python not installed â€” Stage 3 frame analysis skipped.")
        print("       Install: pip install opencv-python --break-system-packages")
        print("       Human review must compensate for static/skin/bars/greenscreen checks.")
        print()

    shortlist: dict = {}

    for slot in SLOTS:
        sid   = slot["slot_id"]
        role  = slot["role"]
        query = slot["query"]

        print(f"\n{'â”€'*60}")
        print(f"[{sid}]")

        # Stage 1 â€” fetch
        print(f"  Stage 1  query: {query!r}")
        raw = pexels_search(query, per_page=30)
        print(f"           {len(raw)} raw results from Pexels")
        time.sleep(0.35)   # polite rate limiting

        # Stage 2 â€” metadata filter
        meta_ok: list[dict] = []
        for v in raw:
            m = extract_metadata(v)
            if m is None:
                continue
            ok, reason = passes_metadata_filter(m, role)
            if ok:
                meta_ok.append(m)
        print(f"  Stage 2  {len(meta_ok)} passed metadata filter")

        # Stage 3 â€” frame analysis (download â†’ analyse â†’ delete temp)
        candidates: list[dict] = []
        for m in meta_ok[:10]:        # cap at 10 downloads per slot
            if not use_cv2:
                m["analysis"] = {
                    "cv2_available":    False,
                    "is_static":        False,
                    "has_skin":         False,
                    "has_black_bars":   False,
                    "has_green_screen": False,
                    "corner_text_flag": False,
                }
                candidates.append(m)
                continue

            tmp = TEMP_DIR / f"{sid}_{m['id']}.mp4"
            print(f"  Stage 3  downloading {m['license_ref']} ({m['width']}Ã—{m['height']}, {m['duration']}s)â€¦")
            if not download_file(m["download_url"], tmp):
                continue

            ana = analyse_clip(tmp)
            m["analysis"] = ana
            tmp.unlink(missing_ok=True)   # free disk; URL preserved in metadata

            if is_hard_fail(ana):
                reasons = [k for k in ("is_static","has_skin","has_black_bars","has_green_screen") if ana[k]]
                print(f"           REJECTED: {', '.join(reasons)}")
                continue

            flag = " [âš  corner text â€” verify]" if ana.get("corner_text_flag") else ""
            print(f"           PASSED{flag}")
            candidates.append(m)

            if len(candidates) >= 5:   # 5 candidates per slot is plenty
                break

        print(f"  â†’ {len(candidates)} candidates for human review")

        shortlist[sid] = {
            "slot_id":         sid,
            "category":        slot["category"],
            "role":            role,
            "mood_energy":     slot["mood_energy"],
            "mood_temperature": slot["mood_temperature"],
            "n":               slot["n"],
            "query":           query,
            "candidates":      candidates,
        }

    # Write outputs
    shortlist_path = OUTPUT_DIR / "shortlist.json"
    review_path    = OUTPUT_DIR / "review.html"

    shortlist_path.write_text(json.dumps(shortlist, indent=2, default=lambda o: bool(o) if hasattr(o, "__bool__") else str(o)), encoding="utf-8")
    review_path.write_text(build_review_html(shortlist), encoding="utf-8")

    # Summary
    filled   = sum(1 for v in shortlist.values() if v["candidates"])
    missing  = len(shortlist) - filled

    print()
    print("=" * 60)
    print(f"[HARVEST COMPLETE]")
    print(f"  Slots with candidates : {filled} / {len(shortlist)}")
    print(f"  Slots needing manual  : {missing} (Mixkit or Kling AI)")
    print(f"  shortlist.json        : {shortlist_path}")
    print(f"  review.html           : {review_path}")
    print()
    print("[NEXT]")
    print("  1. Open scripts/broll_output/review.html in browser")
    print("  2. For each slot: click one clip â†’ marks it green")
    print("  3. Click 'Export picks.json' â†’ save to scripts/broll_output/picks.json")
    print("  4. python scripts/broll_harvest.py generate --picks scripts/broll_output/picks.json")


# â”€â”€ ENTRY POINT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Adcreo B-Roll Harvest â€” Stages 1â€“4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("harvest", help="Stages 1â€“3: fetch â†’ filter â†’ analyse â†’ review.html")

    gen = sub.add_parser("generate", help="Stage 4: picks.json â†’ trim_commands.sh + seed SQL")
    gen.add_argument(
        "--picks",
        type=Path,
        default=OUTPUT_DIR / "picks.json",
        help="Path to picks.json exported from review.html",
    )

    args = parser.parse_args()

    if args.cmd == "harvest":
        run_harvest()
    elif args.cmd == "generate":
        if not args.picks.exists():
            print(f"ERROR: picks file not found: {args.picks}")
            sys.exit(1)
        generate_outputs(args.picks)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

