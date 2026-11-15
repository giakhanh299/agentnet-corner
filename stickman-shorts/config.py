"""Single source of truth for the stickman rig.

EVERY number that shapes the character lives in ``SPEC`` and nowhere else.
All proportions derive from one unit, ``HEAD_R`` (head radius), so the
stickman can never drift between scenes: scenes only ever pass joint
angles (poses) to the rig, never coordinates or lengths.

Adapted from the Gemini consistency design (frozen spec, joint-angles-only
control) to Manim units. Manim frame for this project: 9 units wide,
16 units tall == 1080x1920 px at 30 fps.
"""

from types import MappingProxyType

# ---------------------------------------------------------------- video
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FRAME_WIDTH = 9
FRAME_HEIGHT = 16
FPS = 30

# ---------------------------------------------------------------- stickman
# All lengths are in Manim frame units. Total height =
# 2*HEAD_R + NECK + TORSO + UPPER_LEG + LOWER_LEG = 6.05 units
# (~38% of the 16-unit frame height).
SPEC = MappingProxyType(
    {
        "HEAD_R": 0.6,        # head radius; the single unit everything derives from
        "NECK": 0.25,         # neck length
        "TORSO": 2.5,         # hip -> shoulder length
        "UPPER_ARM": 0.95,    # shoulder -> elbow
        "LOWER_ARM": 0.85,    # elbow -> hand
        "UPPER_LEG": 1.05,    # hip -> knee
        "LOWER_LEG": 1.05,    # knee -> foot
        "STROKE": 8,          # the ONE stroke width for body + props (Manim units)
        "STROKE_THIN": 4,     # face details (eyes, mouth)
        "INK": "#141414",     # soft black, never pure #000000
        "BG": "#F6F5F0",       # off-white paper background
        "ACCENT": "#D9381E",   # red-orange for keyword highlights / key props
        "WHITE": "#FFFFFF",
        "GREY": "#4A4A4A",
    }
)

# ---------------------------------------------------------------- text / audio
FONT_FAMILY = "Be Vietnam Pro"
FONT_SIZE_TITLE = 72
FONT_SIZE_BODY = 48
FONT_SIZE_MIN = 48  # never smaller on a 1080x1920 phone screen

# Project audio standard (measured from real reference videos):
# speech 150-165 wpm, normalize to -16 LUFS, true peak <= -1 dBTP.
WORDS_PER_MINUTE = (150, 165)
TARGET_LUFS = -16.0
TRUE_PEAK_DBTP = -1.5
SCRIPT_WORDS_45S = (112, 124)  # 45 s at 150-165 wpm

# Ground line (feet level) in Manim frame units. Hip rest height derives
# from it: hip sits UPPER_LEG + LOWER_LEG above the ground when standing.
GROUND_Y = -3.6
