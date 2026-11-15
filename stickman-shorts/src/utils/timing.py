"""Timing helpers: convert between script words, seconds and frames.

Project standard (measured from real reference videos): speech at
150-165 wpm, videos 40-55 s. A 45 s video therefore carries 112-124 words.
"""

from __future__ import annotations

from config import FPS, SCRIPT_WORDS_45S, WORDS_PER_MINUTE


def seconds_to_frames(seconds: float, fps: int = FPS) -> int:
    return int(round(seconds * fps))


def frames_to_seconds(frames: int, fps: int = FPS) -> float:
    return frames / fps


def words_for_duration(seconds: float, wpm: float = 157.5) -> int:
    """Word budget for ``seconds`` of speech at ``wpm`` (default: midpoint
    of the 150-165 safe zone)."""
    return int(round(seconds * wpm / 60))


def check_script_length(words: int, duration_s: float = 45.0) -> tuple[bool, str]:
    """Check a script's word count against the safe zone for its duration."""
    lo = int(duration_s * WORDS_PER_MINUTE[0] / 60)
    hi = int(duration_s * WORDS_PER_MINUTE[1] / 60)
    if lo <= words <= hi:
        return True, f"{words} words in safe zone {lo}-{hi} for {duration_s:g}s"
    return False, f"{words} words OUTSIDE safe zone {lo}-{hi} for {duration_s:g}s"


def scene_word_budget(duration_s: float = 45.0) -> tuple[int, int]:
    if duration_s == 45.0:
        return SCRIPT_WORDS_45S
    lo = int(duration_s * WORDS_PER_MINUTE[0] / 60)
    hi = int(duration_s * WORDS_PER_MINUTE[1] / 60)
    return lo, hi
