#!/usr/bin/env python3
"""Assemble a final Short: Manim raw video + voice (+ optional music and
burned-in captions) -> final.mp4, audio normalized to -16 LUFS.

Project audio standard (measured from real reference videos):
voice from ~0.1 s, normalize to -16 LUFS, true peak <= -1 dBTP,
speech 150-165 wpm. No LaTeX anywhere in this pipeline.

Lessons from v001 (2026-11-15, verified the hard way):
- Do NOT use the ffmpeg ``subtitles`` filter on an .srt: libass renders
  the SRT at PlayRes 384x288 and scales it 6.67x onto a 1080x1920 frame,
  so the text lands invisible / off-frame. Convert the .srt to .ass
  with PlayResX=1080 / PlayResY=1920 first and use the ``ass`` filter.
- True-peak limiting: ``alimiter=limit=0.7:level=false`` AFTER loudnorm.
  ``level=true`` is auto-gain, not true-peak mode — it once boosted a
  v001 build to -13.16 LUFS.

Usage:
    python tools/assemble.py --video videos/2026-11-15_x/output/raw.mp4 \\
        --voice videos/2026-11-15_x/voice.wav \\
        --srt videos/2026-11-15_x/captions.srt \\
        --music src/assets/audio/music/bgm.mp3 \\
        --out videos/2026-11-15_x/output/final.mp4
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

TARGET_LUFS = -16.0
TRUE_PEAK = -1.5
LRA = 11

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Be Vietnam Pro,56,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,40,40,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _srt_time_to_ass(t: str) -> str:
    """00:00:04,800 -> 0:00:04.80 (ASS wants H:MM:SS.cc)."""
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return f"{int(h)}:{m}:{s}.{ms[:2]}"


def srt_to_ass(srt_path: str) -> str:
    """Convert an .srt to an .ass next to it (PlayRes 1080x1920).

    Returns the .ass path. Style matches the v001-proven captions
    (Be Vietnam Pro 56, white + black outline, bottom-centre, 300px up).
    """
    with open(srt_path, encoding="utf-8") as f:
        text = f.read()
    blocks = re.split(r"\n\s*\n", text.strip())
    events = []
    for block in blocks:
        lines = [ln for ln in block.strip().splitlines() if ln.strip()]
        if len(lines) < 3:
            continue
        m = re.match(r"(\d\d:\d\d:\d\d,\d+)\s*-->\s*(\d\d:\d\d:\d\d,\d+)", lines[1])
        if not m:
            continue
        start, end = _srt_time_to_ass(m.group(1)), _srt_time_to_ass(m.group(2))
        caption = "\\N".join(lines[2:])
        events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{caption}")
    ass_path = os.path.splitext(srt_path)[0] + ".ass"
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        f.write("\n".join(events) + "\n")
    print(f"converted {srt_path} -> {ass_path} ({len(events)} events)")
    return ass_path


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def _ffmpeg_filter_path(path: str) -> str:
    """Escape a filesystem path for FFmpeg libass filter on both Windows & POSIX."""
    norm = os.path.abspath(path).replace("\\", "/")
    norm = norm.replace(":", r"\:").replace("'", r"\'")
    return norm


def _measure_loudnorm(voice: str) -> dict[str, str] | None:
    """Run pass-1 loudnorm analysis so pass-2 linear=true works accurately."""
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats", "-i", voice,
        "-af", f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA={LRA}:print_format=json",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", proc.stderr or "")
    if not m:
        return None
    try:
        stats = json.loads(m.group(0))
        if stats.get("input_i") in (None, "-inf", "inf"):
            return None
        return stats
    except Exception:
        return None


def assemble(
    video: str,
    voice: str,
    out: str,
    srt: str | None = None,
    music: str | None = None,
    ass: str | None = None,
) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    inputs = ["-i", video, "-i", voice]
    if music:
        inputs += ["-stream_loop", "-1", "-i", music]

    stats = _measure_loudnorm(voice)
    if stats:
        ln_filter = (
            f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA={LRA}"
            f":measured_I={stats['input_i']}"
            f":measured_TP={stats['input_tp']}"
            f":measured_LRA={stats['input_lra']}"
            f":measured_thresh={stats['input_thresh']}"
            f":offset={stats['target_offset']}:linear=true"
        )
    else:
        ln_filter = f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA={LRA}"

    filters = [f"[1:a]{ln_filter},alimiter=limit=0.7:level=false[voice]"]
    if music:
        filters.append("[2:a]volume=0.12[bgm]")
        filters.append("[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]")
        audio_map = "[aout]"
    else:
        audio_map = "[voice]"

    vf = []
    ass_target = ass or (srt_to_ass(srt) if srt else None)
    if ass_target:
        escaped_ass = _ffmpeg_filter_path(ass_target)
        vf = ["-vf", f"ass='{escaped_ass}'"]

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + ["-filter_complex", "; ".join(filters)]
        + vf
        + [
            "-map", "0:v", "-map", audio_map,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", out,
        ]
    )
    run(cmd)
    print(f"wrote {out}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video", required=True, help="Manim raw.mp4 (no audio)")
    p.add_argument("--voice", required=True, help="voice.wav / voice.mp3")
    p.add_argument("--out", required=True, help="output final.mp4")
    p.add_argument("--srt", help="optional captions.srt to burn in")
    p.add_argument("--ass", help="optional pre-built captions.ass to burn in")
    p.add_argument("--music", help="optional background music file")
    a = p.parse_args()
    assemble(a.video, a.voice, a.out, a.srt, a.music, ass=a.ass)
    return 0


if __name__ == "__main__":
    sys.exit(main())
