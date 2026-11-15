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
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

TARGET_LUFS = -16.0
TRUE_PEAK = -1.5
LRA = 11
FONT = Path(__file__).resolve().parents[1] / "src/assets/fonts/BeVietnamPro-Regular.ttf"


def assemble(video: str, voice: str, out: str, srt: str | None, music: str | None) -> None:
    inputs = ["-i", str(Path(video).resolve()), "-i", str(Path(voice).resolve())]
    mix = "[1:a]"
    filters = []
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(Path(music).resolve())]
        filters.extend([
            "[2:a]volume=0.12[bgm]",
            "[1:a][bgm]amix=inputs=2:duration=first:normalize=0[mix]",
        ])
        mix = "[mix]"
    filters.append(f"{mix}loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA={LRA},apad[aout]")

    with TemporaryDirectory(prefix="stickman-assemble-") as temp:
        vf = []
        if srt:
            # FFmpeg parses filter filenames separately from command-line paths.
            # Stage a fixed name so drive letters and punctuation need no escaping.
            shutil.copyfile(srt, Path(temp) / "captions.srt")
            shutil.copyfile(FONT, Path(temp) / FONT.name)
            style = (
                "FontName=Be Vietnam Pro,FontSize=28,"
                "PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,"
                "BorderStyle=1,Outline=2,Alignment=2,MarginV=140"
            )
            vf = ["-vf", f"subtitles=captions.srt:fontsdir=.:force_style='{style}'"]

        cmd = (
            ["ffmpeg", "-y"]
            + inputs
            + ["-filter_complex", ";".join(filters)]
            + vf
            + [
                "-map", "0:v:0", "-map", "[aout]",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-shortest", str(Path(out).resolve()),
            ]
        )
        subprocess.run(cmd, cwd=temp, check=True)
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
