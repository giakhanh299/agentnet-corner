#!/usr/bin/env python3
"""Assemble a final Short: Manim raw video + voice (+ optional music and
burned-in captions) -> final.mp4, audio normalized to -16 LUFS.

Project audio standard (measured from real reference videos):
voice from ~0.1 s, normalize to -16 LUFS, true peak <= -1 dBTP,
speech 150-165 wpm. No LaTeX anywhere in this pipeline.

Usage:
    python tools/assemble.py --video videos/2026-11-15_x/output/raw.mp4 \\
        --voice videos/2026-11-15_x/voice.wav \\
        --srt videos/2026-11-15_x/captions.srt \\
        --music src/assets/audio/music/bgm.mp3 \\
        --out videos/2026-11-15_x/output/final.mp4
"""

from __future__ import annotations

import argparse
import subprocess
import sys

TARGET_LUFS = -16.0
TRUE_PEAK = -1.5
LRA = 11


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def assemble(video: str, voice: str, out: str, srt: str | None, music: str | None) -> None:
    inputs = ["-i", video, "-i", voice]
    if music:
        inputs += ["-stream_loop", "-1", "-i", music]

    # Voice -> -16 LUFS. Music (if any) sits 0.12 under the voice.
    filters = [f"[1:a]loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA={LRA}:linear=true[voice]"]
    if music:
        filters.append("[2:a]volume=0.12[bgm]")
        filters.append("[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]")
        audio_map = "[aout]"
    else:
        audio_map = "[voice]"

    vf = []
    if srt:
        # Burn captions; force the repo font so diacritics render correctly.
        style = (
            "FontName=Be Vietnam Pro,FontSize=28,"
            "PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,"
            "BorderStyle=1,Outline=2,Alignment=2,MarginV=140"
        )
        vf = ["-vf", f"subtitles='{srt}':force_style='{style}'"]

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + ["-filter_complex", "; ".join(filters)]
        + vf
        + [
            "-map", "0:v", "-map", audio_map,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
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
    p.add_argument("--music", help="optional background music file")
    a = p.parse_args()
    assemble(a.video, a.voice, a.out, a.srt, a.music)
    return 0


if __name__ == "__main__":
    sys.exit(main())
