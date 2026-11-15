"""Render/export helpers: Manim config + ffprobe checks.

No LaTeX is ever needed (Text/Pango only), so these helpers never touch
a TeX installation.
"""

from __future__ import annotations

import json
import subprocess

from manim import config

from config import FPS, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_HEIGHT, VIDEO_WIDTH


def apply_video_config() -> None:
    """9:16 vertical, 1080x1920, 30 fps — call at the top of a scene file."""
    config.pixel_width = VIDEO_WIDTH
    config.pixel_height = VIDEO_HEIGHT
    config.frame_width = FRAME_WIDTH
    config.frame_height = FRAME_HEIGHT
    config.frame_rate = FPS


def probe_video(path: str) -> dict:
    """ffprobe a rendered file; returns width/height/fps/duration/size."""
    out = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", "-show_format", path,
        ],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(out.stdout)
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    num, den = video["r_frame_rate"].split("/")
    return {
        "path": path,
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": float(num) / float(den),
        "duration": float(data["format"]["duration"]),
        "size_bytes": int(data["format"]["size"]),
        "codec": video["codec_name"],
    }
