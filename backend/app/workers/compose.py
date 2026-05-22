"""
backend/app/workers/compose.py
WorkerCompose — Assembles the 15s fractional render.
[TDD-WORKERS]-H  [TDD-VIDEO]-B  [TDD-BROLL]-H

v4-Δ1:
  - b_roll_plan is a dict {template, hook, context, cta} — S14 (object not array)
  - Branches on structure_template (T1..T5) from b_roll_plan["template"]
  - CTA: real clip for T1, FFmpeg text-card for T2/T3/T4/T5
  - Variable-arity filter_complex concat (3-segment T1/T2/T5, 4-segment T3/T4)

No DB access. No state transitions.
All temp files written to /tmp/{gen_id}_*.
Cleanup runs in finally block — always executes.
"""
import asyncio
import logging
import os
from pathlib import Path

from app.broll.templates import TEMPLATE_DURATIONS, CTA_COPY
from app.core.exceptions import ComposeError, ComposeDurationError

logger = logging.getLogger(__name__)

CANONICAL_DURATION_S  = 15.0
MAX_SEGMENT_DURATION_S = 10.0

# LUT directory: backend/app/luts/*.cube
LUT_DIR = Path(__file__).parent.parent / "luts"
BENEFIT_LUT_MAP: dict[str, str] = {
    "premium":  "premium_warm.cube",
    "trending": "trending_vivid.cube",
    "gift":     "gift_festive.cube",
    "natural":  "natural_green.cube",
}
DEFAULT_LUT = "neutral_balanced.cube"

SGI_WATERMARK_TEXT = "AI Generated | Adcreo"
DEFAULT_BRAND_COLOR = "#1A1A1A"   # neutral charcoal — legible on any product bg
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 1080, 1920


class WorkerCompose:
    """
    Assembles the 15s fractional render.
    Template-driven: reads structure_template from b_roll_plan["template"].
    Applies LUT color grade + SGI watermark per IT Rules 2026.
    """

    def __init__(self, r2_client):
        self.r2_client = r2_client

    # ── Infrastructure helpers ─────────────────────────────────────────────

    def _select_lut(self, benefit: str) -> Path:
        """Maps benefit string → absolute LUT path. Falls back to DEFAULT_LUT."""
        return LUT_DIR / BENEFIT_LUT_MAP.get(benefit, DEFAULT_LUT)

    def _get_temp_path(self, gen_id: str, suffix: str) -> str:
        """Returns /tmp/{gen_id}_{suffix}."""
        return f"/tmp/{gen_id}_{suffix}"

    def _cleanup_temp_files(self, paths: list[str]) -> None:
        """Deletes temp files. Silently ignores missing files. Must never raise."""
        for path in paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as exc:
                logger.warning(f"Temp cleanup failed for {path}: {exc}")

    async def _probe_duration(self, file_path: str) -> float:
        """Uses ffprobe to get duration in seconds. Raises ComposeError on failure."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise ComposeError(
                    f"ffprobe non-zero exit for {file_path}: "
                    f"{stderr.decode().strip()}"
                )
            return float(stdout.decode().strip())
        except ComposeError:
            raise
        except Exception as exc:
            raise ComposeError(f"ffprobe failed: {exc}") from exc

    def _build_ffmpeg_cmd(
        self,
        inputs: list[str],
        output_path: str,
        filter_graph: str,
    ) -> list[str]:
        return [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_graph,
            "-map", "[final_v]",
            "-map", "[padded_a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-r", "30",
            "-t", "15",
            output_path,
        ]

    # ── CTA text-card renderer ─────────────────────────────────────────────

    async def _render_cta_text_card(
        self,
        gen_id: str,
        brand_color: str,
        cta_text: str,
        duration_s: float,
    ) -> str:
        """
        Render a CTA text card via FFmpeg lavfi color + drawtext.
        No new dependencies — mirrors SGI watermark pattern (F-403).
        Returns local path to rendered mp4.
        """
        output_path = self._get_temp_path(gen_id, "cta_card.mp4")
        hex_color   = brand_color.lstrip("#") if brand_color else "1A1A1A"
        safe_text   = (cta_text or "").replace("'", "\u2019")
        safe_wm     = SGI_WATERMARK_TEXT.replace("'", "\u2019")

        vf_parts = ["fps=30,setsar=1"]
        if safe_text:
            vf_parts.append(
                f"drawtext=text='{safe_text}':"
                f"fontfile={FONT_PATH}:"
                f"fontsize=56:fontcolor=white:"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"shadowcolor=black@0.8:shadowx=2:shadowy=2"
            )
        vf_parts.append(
            f"drawtext=text='{safe_wm}':"
            f"fontsize=28:box=1:boxcolor=black@0.4:boxborderw=6:"
            f"fontcolor=white@0.85:x=20:y=h-36"
        )

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=#{hex_color}:s={W}x{H}:r=30:d={duration_s:.3f}",
            "-vf", ",".join(vf_parts),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-t", f"{duration_s:.3f}",
            output_path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise ComposeError(
                f"_render_cta_text_card failed gen={gen_id}: "
                f"{stderr.decode()[:400]}"
            )
        return output_path

    # ── Template segment builder ───────────────────────────────────────────

    async def _build_segments_for_template(
        self,
        gen_id: str,
        structure_template: str,
        b_roll_plan: dict,
        i2v_r2_key: str,
        brand_color: str,
        brand_tier: str,
        hook_text: str,
        cta_text_raw: str,
    ) -> list[dict]:
        """
        Returns ordered segment list per [TDD-BROLL]-H and [TDD-BROLL]-C.
        Each segment dict:
            kind        : hook | context | i2v | cta_clip | cta_card
            r2_url      : R2 key (None for cta_card — pre-rendered locally)
            local_path  : /tmp path (download destination, or pre-rendered path)
            duration_s  : float
            overlay_text: str | None (hook text overlay only)
        [TDD-BROLL]-K invariant 6: unrecognized template raises before any R2 downloads.
        """
        hook_clip = b_roll_plan.get("hook")
        ctx_clip  = b_roll_plan.get("context")
        cta_clip  = b_roll_plan.get("cta")

        # Hook is always required — CI coverage check enforces this at deploy time
        if not hook_clip:
            raise ComposeError(
                f"b_roll_plan missing hook clip gen={gen_id} "
                f"template={structure_template}. "
                "Run ci/broll_coverage_check.py to diagnose."
            )

        # Tier-aware CTA copy (T5 only; others use brand-color gradient alone)
        cta_display = CTA_COPY.get(
            (structure_template, brand_tier),
            cta_text_raw or "",
        )

        def _seg(kind: str, r2_url, duration_s: float, overlay_text=None) -> dict:
            return {
                "kind":         kind,
                "r2_url":       r2_url,
                "local_path":   self._get_temp_path(gen_id, f"{kind}.mp4"),
                "duration_s":   duration_s,
                "overlay_text": overlay_text,
            }

        d = TEMPLATE_DURATIONS[structure_template]

        if structure_template == "T1":
            # hook(3s) + I2V(9s) + cta_clip(3s)
            # cta_clip is a real B-roll clip — falls back to text-card if None
            if cta_clip:
                cta_seg = _seg("cta_clip", cta_clip["r2_url"], d["cta"])
            else:
                logger.warning(
                    f"T1 cta_clip is None gen={gen_id} — "
                    f"rendering text-card fallback"
                )
                cta_path = await self._render_cta_text_card(
                    gen_id, brand_color, cta_display, d["cta"]
                )
                cta_seg = {
                    "kind": "cta_card", "r2_url": None,
                    "local_path": cta_path,
                    "duration_s": d["cta"], "overlay_text": None,
                }
            return [
                _seg("hook", hook_clip["r2_url"], d["hook"], hook_text),
                _seg("i2v",  i2v_r2_key,          d["i2v"]),
                cta_seg,
            ]

        if structure_template == "T2":
            # hook(2s) + I2V(10s) + text-card(3s)
            cta_path = await self._render_cta_text_card(
                gen_id, brand_color, cta_display, d["cta"]
            )
            return [
                _seg("hook", hook_clip["r2_url"], d["hook"], hook_text),
                _seg("i2v",  i2v_r2_key,          d["i2v"]),
                {"kind": "cta_card", "r2_url": None,
                 "local_path": cta_path,
                 "duration_s": d["cta"], "overlay_text": None},
            ]

        if structure_template == "T3":
            # hook(3s) + context(3s) + I2V(6s) + text-card(3s)
            # context clip is required; fall back to T1 if missing
            if ctx_clip is None:
                logger.warning(
                    f"T3 missing context clip gen={gen_id} — "
                    f"falling back to T1"
                )
                return await self._build_segments_for_template(
                    gen_id, "T1", b_roll_plan, i2v_r2_key,
                    brand_color, brand_tier, hook_text, cta_text_raw,
                )
            cta_path = await self._render_cta_text_card(
                gen_id, brand_color, cta_display, d["cta"]
            )
            return [
                _seg("hook",    hook_clip["r2_url"], d["hook"], hook_text),
                _seg("context", ctx_clip["r2_url"],  d["context"]),
                _seg("i2v",     i2v_r2_key,          d["i2v"]),
                {"kind": "cta_card", "r2_url": None,
                 "local_path": cta_path,
                 "duration_s": d["cta"], "overlay_text": None},
            ]

        if structure_template == "T4":
            # hook(3s festive) + context(4s festive) + I2V(5s) + text-card(3s)
            if ctx_clip is None:
                logger.warning(
                    f"T4 missing context clip gen={gen_id} — "
                    f"falling back to T1"
                )
                return await self._build_segments_for_template(
                    gen_id, "T1", b_roll_plan, i2v_r2_key,
                    brand_color, brand_tier, hook_text, cta_text_raw,
                )
            cta_path = await self._render_cta_text_card(
                gen_id, brand_color, cta_display, d["cta"]
            )
            return [
                _seg("hook",    hook_clip["r2_url"], d["hook"], hook_text),
                _seg("context", ctx_clip["r2_url"],  d["context"]),
                _seg("i2v",     i2v_r2_key,          d["i2v"]),
                {"kind": "cta_card", "r2_url": None,
                 "local_path": cta_path,
                 "duration_s": d["cta"], "overlay_text": None},
            ]

        if structure_template == "T5":
            # hook(2s) + I2V(10s) + text-card(3s urgency)
            cta_path = await self._render_cta_text_card(
                gen_id, brand_color, cta_display, d["cta"]
            )
            return [
                _seg("hook", hook_clip["r2_url"], d["hook"], hook_text),
                _seg("i2v",  i2v_r2_key,          d["i2v"]),
                {"kind": "cta_card", "r2_url": None,
                 "local_path": cta_path,
                 "duration_s": d["cta"], "overlay_text": None},
            ]

        # [TDD-BROLL]-K invariant 6: fail fast before any R2 downloads
        raise ComposeError(
            f"Unrecognized structure_template={structure_template!r} "
            f"gen={gen_id}. Valid: T1 T2 T3 T4 T5."
        )

    # ── Filter graph builder ───────────────────────────────────────────────

    def _build_filter_graph(
        self,
        segments: list[dict],
        tts_path: str,
        lut_path: str,
    ) -> tuple[str, list[str]]:
        """
        Builds variable-arity FFmpeg filter_complex.
        All segment local_paths must exist before this is called.
        TTS is appended as the last input.
        Returns (filter_graph_string, ffmpeg_inputs_list).
        Handles 3-segment (T1/T2/T5) and 4-segment (T3/T4) templates.
        """
        parts         = []
        ffmpeg_inputs = []
        seg_labels    = []
        input_idx     = 0

        for i, seg in enumerate(segments):
            duration_s   = seg["duration_s"]
            scaled_label = f"seg{i}_s"
            final_label  = f"seg{i}_v"

            ffmpeg_inputs += ["-i", seg["local_path"]]

            # I2V: preserve full product frame — scale to fit, pad black edges
            # B-roll/cta_card: fill frame — scale up and crop (abstract clips)
            if seg["kind"] == "i2v":
                scale_filter = (
                    f"scale={W}:{H}:"
                    f"force_original_aspect_ratio=decrease,"
                    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black"
                )
            else:
                scale_filter = (
                    f"scale={W}:{H}:"
                    f"force_original_aspect_ratio=increase,"
                    f"crop={W}:{H}"
                )
            parts.append(
                f"[{input_idx}:v]fps=30,"
                f"{scale_filter},"
                f"tpad=stop_mode=clone:"
                f"stop_duration={max(0.0, duration_s - 0.033):.3f},"
                f"trim=end={duration_s:.3f},"
                f"setsar=1[{scaled_label}]"
            )
            input_idx += 1

            # Hook text overlay only — other segments have no overlay
            # (cta_card text is already drawn in by _render_cta_text_card)
            overlay_text = seg.get("overlay_text")
            if overlay_text and seg["kind"] == "hook":
                safe_text = overlay_text.replace("'", "\u2019")[:40]
                parts.append(
                    f"[{scaled_label}]drawtext="
                    f"text='{safe_text}':"
                    f"fontfile={FONT_PATH}:"
                    f"fontsize=64:fontcolor=white:"
                    f"x=(w-text_w)/2:y=140:"
                    f"shadowcolor=black@0.8:"
                    f"shadowx=2:shadowy=2[{final_label}]"
                )
            else:
                parts.append(f"[{scaled_label}]null[{final_label}]")

            seg_labels.append(f"[{final_label}]")

        # TTS audio — always last input
        tts_input_idx = input_idx
        ffmpeg_inputs += ["-i", tts_path]

        # Variable-arity concat — works for n=3 (T1/T2/T5) and n=4 (T3/T4)
        n = len(segments)
        concat_in = "".join(seg_labels)
        parts.append(f"{concat_in}concat=n={n}:v=1:a=0[concat_v]")

        # LUT color grade
        parts.append(f"[concat_v]lut3d={lut_path}[graded_v]")

        # SGI watermark — mandatory, bottom-left, per IT Rules 2026 (F-403)
        safe_wm = SGI_WATERMARK_TEXT.replace("'", "\u2019")
        parts.append(
            f"[graded_v]drawtext="
            f"text='{safe_wm}':"
            f"fontsize=38:box=1:boxcolor=black@0.4:boxborderw=8:"
            f"fontcolor=white@0.85:x=20:y=h-44[final_v]"
        )

        # Audio: trim to 15s then pad to 15s if shorter
        parts.append(
            f"[{tts_input_idx}:a]"
            f"atrim=end=15.0,apad=whole_dur=15.0[padded_a]"
        )

        return ";\n".join(parts), ffmpeg_inputs

    # ── Main process ───────────────────────────────────────────────────────

    async def process(
        self,
        gen_id: str,
        i2v_r2_key: str,
        tts_r2_key: str,
        strategy_card: dict,
        b_roll_plan: dict,      # {template, hook, context, cta} — S14 object form
        brand_profile: dict,
        plan_tier: str,
    ) -> str:
        """
        Assembles 15s MP4 per structure_template.
        Reads structure_template from b_roll_plan["template"].
        Applies LUT color grade + SGI watermark.
        Uploads result to R2. Returns R2 key string.
        Raises ComposeError on unrecoverable failure.
        Raises ComposeDurationError if I2V segment exceeds MAX_SEGMENT_DURATION_S.
        Temp files always cleaned up in finally block.
        """
        # ── Guard: b_roll_plan must be a dict (S14) ───────────────────────
        if not isinstance(b_roll_plan, dict):
            raise ComposeError(
                f"b_roll_plan must be a dict, got {type(b_roll_plan).__name__} "
                f"gen={gen_id}. S14 violation — check strategist output."
            )

        # ── Read structure_template from plan (single source of truth) ────
        structure_template = b_roll_plan.get("template") or "T1"

        # ── Brand tokens ──────────────────────────────────────────────────
        brand_color = (
            strategy_card.get("brand_color_primary")
            or brand_profile.get("primary_color")
            or DEFAULT_BRAND_COLOR
        )
        brand_tier = strategy_card.get("brand_tier", "mass") or "mass"

        # ── Text overlays from strategy_card ──────────────────────────────
        script_summary = strategy_card.get("script_summary", {})
        hook_text = (
            (script_summary.get("hook") or "")[:40]
        )
        cta_text_raw = (
            (script_summary.get("cta") or "")[:40]
        )

        # ── LUT selection ─────────────────────────────────────────────────
        benefit  = strategy_card.get("benefit", "natural") or "natural"
        lut_path = str(self._select_lut(benefit)).replace(os.sep, "/")

        # ── Temp file tracking ────────────────────────────────────────────
        output_path = self._get_temp_path(gen_id, "preview.mp4")
        tts_path    = self._get_temp_path(gen_id, "tts.mp3")
        temp_files  = [output_path, tts_path]

        try:
            # ── Step 1: Build segment list ─────────────────────────────────
            # Also renders cta_card locally if template requires text-card CTA
            segments = await self._build_segments_for_template(
                gen_id=gen_id,
                structure_template=structure_template,
                b_roll_plan=b_roll_plan,
                i2v_r2_key=i2v_r2_key,
                brand_color=brand_color,
                brand_tier=brand_tier,
                hook_text=hook_text,
                cta_text_raw=cta_text_raw,
            )

            # Track cta_card temp files for cleanup
            for seg in segments:
                if seg["kind"] == "cta_card":
                    temp_files.append(seg["local_path"])

            logger.info(
                f"[compose] gen={gen_id} template={structure_template} "
                f"segments={[s['kind'] for s in segments]}"
            )

            # ── Step 2: Download all R2 assets concurrently ────────────────
            bucket = os.environ["R2_BUCKET_NAME"]

            async def _dl(r2_key: str, local_path: str) -> None:
                resp = await asyncio.to_thread(
                    self.r2_client.get_object,
                    Bucket=bucket, Key=r2_key,
                )
                data = resp["Body"].read()
                await asyncio.to_thread(
                    Path(local_path).write_bytes, data
                )
                temp_files.append(local_path)

            downloads = [_dl(tts_r2_key, tts_path)]
            for seg in segments:
                if seg["r2_url"] is not None:
                    downloads.append(_dl(seg["r2_url"], seg["local_path"]))

            await asyncio.gather(*downloads)
            logger.info(
                f"[compose] downloads done gen={gen_id} "
                f"count={len(downloads)}"
            )

            # ── Step 3: Probe + clamp I2V duration ────────────────────────
            i2v_seg = next(s for s in segments if s["kind"] == "i2v")
            i2v_dur = await self._probe_duration(i2v_seg["local_path"])
            if i2v_dur > MAX_SEGMENT_DURATION_S:
                raise ComposeDurationError(
                    f"I2V duration {i2v_dur:.1f}s exceeds "
                    f"max {MAX_SEGMENT_DURATION_S}s gen={gen_id}"
                )
            # Clamp to actual probed duration if shorter than template slot
            i2v_seg["duration_s"] = min(i2v_dur, i2v_seg["duration_s"])

            # ── Step 4: Build filter graph ─────────────────────────────────
            filter_graph, ffmpeg_inputs = self._build_filter_graph(
                segments=segments,
                tts_path=tts_path,
                lut_path=lut_path,
            )

            # ── Step 5: Run FFmpeg ─────────────────────────────────────────
            cmd = self._build_ffmpeg_cmd(ffmpeg_inputs, output_path, filter_graph)
            logger.info(
                f"[compose] FFmpeg start gen={gen_id} "
                f"template={structure_template} lut={self._select_lut(benefit).name}"
            )
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise ComposeError(
                    f"FFmpeg failed gen={gen_id} "
                    f"rc={proc.returncode}: {stderr.decode()[:800]}"
                )
            logger.info(f"[compose] FFmpeg done gen={gen_id}")

            # ── Step 6: Upload to R2 ───────────────────────────────────────
            r2_key        = f"{gen_id}/compose/preview_15s.mp4"
            preview_bytes = await asyncio.to_thread(
                Path(output_path).read_bytes
            )
            await asyncio.to_thread(
                self.r2_client.put_object,
                Bucket=bucket,
                Key=r2_key,
                Body=preview_bytes,
                ContentType="video/mp4",
            )
            logger.info(f"[compose] uploaded gen={gen_id} key={r2_key}")
            return r2_key

        except (ComposeError, ComposeDurationError):
            raise
        except Exception as exc:
            raise ComposeError(
                f"Compose unexpected error gen={gen_id}: {exc}"
            ) from exc
        finally:
            self._cleanup_temp_files(temp_files)
