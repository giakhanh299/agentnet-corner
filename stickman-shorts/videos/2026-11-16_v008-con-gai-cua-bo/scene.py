"""v008 — "Con gai cua bo" (F7, 50s): emotional stickman story.

Fully ORIGINAL story (the #47 original is a 3D animation with an "NVV"
watermark on every frame): little Na breaks mom's favourite vase, mom
scolds her, Na sulks in the corner, dad comes home tired, does NOT
scold — he just sits down beside her, hugs her, and says "con gai cua
bo day roi". Only the emotional mechanism is kept (scold -> sulk ->
tired dad -> hug -> smile). NO lecturing line for dad, ever — his only
line is the payoff line. No image from #47 is reused.

Timeline follows the MEASURED MMS voice (voice.wav, 48.72s; timing.json
— run 3, the file of record) — beat boundaries are the measured
segment starts:

    HOOK    0.00 -  4.80   Na alone, sad, broken vase, card 1
    BEAT 1  4.80 - 14.59   Mom points/scolds; Na head down; wall clock
    BEAT 2 14.59 - 24.70   Mom gone; Na sits sulking in the corner, pillow
    BEAT 3 24.70 - 35.50   Dad walks in from the left door, sits down
                           beside Na (card changes at 30.12: he just sits)
    PAYOFF 35.50 - 45.19   Warm glow; dad hugs Na, both smile, card 5
    CTA    45.19 - 49.50   End card

Video is rendered ~0.8s longer than the voice; assemble uses
-shortest so the final mp4 ends with the voice (48.72s).

Run (on the PC, venv-win):
    python -m manim render -qm --format=mp4 videos/2026-11-16_v008-con-gai-cua-bo/scene.py StickmanScene
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from manim import (
    UP, Circle, Dot, FadeIn, FadeOut, Line, Polygon, Rectangle, RoundedRectangle,
    ValueTracker, VGroup, always_redraw, config, linear,
)

from config import GROUND_Y, SPEC
from src.rig.character import Stickman, joint_positions
from src.rig.poses import POSE_SAD, PoseAngles, lerp_pose
from src.rig.props import clock_wall, ground_line
from src.rig.walk import walk_bob, walk_phase_for_distance, walk_pose
from src.scenes.base_scene import StickmanScene
from src.scenes.text_card import TextCard
from src.utils.export import apply_video_config

apply_video_config()
config.background_color = SPEC["BG"]

INK = SPEC["INK"]
GREY = SPEC["GREY"]
ACCENT = SPEC["ACCENT"]
WHITE = SPEC["WHITE"]
WARM = "#F2C94C"

# ------------------------------------------------------------ beat boundaries (seconds, measured voice)
HOOK_END = 4.796
BEAT1_END = 14.594
BEAT2_END = 24.702
CLAUSE2_AT = 30.116    # "Bo khong mang, bo chi lang im..." — dad sits down
BEAT3_END = 35.5
PAYOFF_END = 45.186
TOTAL = 49.5

CARD_Y = 4.6
HIP_Y = GROUND_Y + SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]  # -1.5
# Sitting hip: feet must rest on the ground. Foot is 1.268 units below the
# hip in POSE_SIT (thigh 1.05 @ 1.35 rad + shin 1.05 @ -0.15 rad).
SIT_HIP_Y = GROUND_Y + 1.268                              # -2.33
NA_SCALE = 0.62
NA_SIT_HIP_Y = GROUND_Y + 1.268 * NA_SCALE                # -2.81

MOM_X = 1.2            # mom stands left of Na, pointing right at her
NA_X = 3.0             # Na's corner (right side)
DAD_X = 1.6            # dad sits beside Na (left of her)
DOOR_X = -3.9          # door frame on the left wall
CLOCK_X = -3.5
CLOCK_Y = 3.0

# Na sulking: seated, head bowed, arms hugging her knees/pillow.
POSE_SULK = PoseAngles(
    torso_lean=0.18, head_tilt=0.30,
    shoulder_l=0.45, elbow_l=0.55,
    shoulder_r=0.45, elbow_r=0.55,
    hip_l=1.35, knee_l=-1.5,
    hip_r=1.35, knee_r=-1.5,
    expression="sad",
)
# Mom scolding: right arm straight out, pointing; determined face.
POSE_MOM = PoseAngles(
    shoulder_r=math.pi / 2 - 0.15, elbow_r=0.05,
    hip_l=0.12, hip_r=-0.12,
    expression="focused",
)
# Dad sitting neutral (he just sits down, says nothing yet).
POSE_DAD_SIT = PoseAngles(
    hip_l=1.35, knee_l=-1.5,
    hip_r=1.35, knee_r=-1.5,
    expression="neutral",
)
# Dad hugging: seated, leaning slightly right toward Na, right arm resting
# toward her shoulder (NOT wrapped around her — the first version stacked
# the two figures into one blob; side-by-side + warm glow carries it).
POSE_DAD_HUG = PoseAngles(
    torso_lean=0.12, head_tilt=0.08,
    shoulder_r=0.5, elbow_r=1.0,
    shoulder_l=0.35, elbow_l=0.6,
    hip_l=1.35, knee_l=-1.5,
    hip_r=1.35, knee_r=-1.5,
    expression="happy",
)
# Na happy, leaning slightly left toward dad, left arm reaching for him.
POSE_NA_HUG = PoseAngles(
    torso_lean=-0.10, head_tilt=-0.08,
    shoulder_l=-0.5, elbow_l=0.8,
    shoulder_r=0.3, elbow_r=0.6,
    hip_l=1.35, knee_l=-1.5,
    hip_r=1.35, knee_r=-1.5,
    expression="happy",
)


def card(title, subtitle=None):
    c = TextCard(title, subtitle=subtitle)
    c.move_to([0, CARD_Y, 0])
    return c


def hair_tie_for(pose: PoseAngles, hip_x: float, hip_y: float, scale: float) -> Dot:
    """Na's tied hair: small accent dot at the back of her head."""
    j = joint_positions(pose)
    hc = j["head_center"] * scale + np.array([hip_x, hip_y, 0.0])
    return Dot(point=hc + np.array([-0.26 * scale, 0.05, 0]), radius=0.10, color=ACCENT)


def bun_for(pose: PoseAngles, hip_x: float, hip_y: float) -> Dot:
    """Mom's hair bun: small ink dot on top of her head."""
    j = joint_positions(pose)
    hc = j["head_center"] + np.array([hip_x, hip_y, 0.0])
    return Dot(point=hc + np.array([0.0, 0.55, 0]), radius=0.12, color=INK)


def skirt_for(pose: PoseAngles, hip_x: float, hip_y: float) -> Polygon:
    """Mom's skirt: grey trapezoid from hip to mid-shin."""
    hip = np.array([hip_x, hip_y, 0.0])
    pts = [
        hip + np.array([-0.50, 0.05, 0]),
        hip + np.array([0.50, 0.05, 0]),
        hip + np.array([0.32, -1.30, 0]),
        hip + np.array([-0.32, -1.30, 0]),
    ]
    skirt = Polygon(*pts, color=GREY, stroke_width=5)
    skirt.set_fill(SPEC["BG"], opacity=1)
    return skirt


def tie_for(pose: PoseAngles, hip_x: float, hip_y: float) -> Line:
    """Dad's tie: short accent line down his chest."""
    j = joint_positions(pose)
    shoulder = j["shoulder"] + np.array([hip_x, hip_y, 0.0])
    return Line(
        shoulder + np.array([0, -0.15, 0]),
        shoulder + np.array([0, -1.0, 0]),
        color=ACCENT, stroke_width=5,
    )


def build_na(pose: PoseAngles, hip_x: float, hip_y: float) -> VGroup:
    """Na: smaller stickman + red hair tie, hip at (hip_x, hip_y)."""
    g = Stickman(pose=pose).scale(NA_SCALE, about_point=np.array([0.0, 0.0, 0.0]))
    g.place(hip_x, hip_y)
    return VGroup(g, hair_tie_for(pose, hip_x, hip_y, NA_SCALE))


def build_mom(pose: PoseAngles) -> VGroup:
    """Mom: stickman + bun + skirt, hip at (MOM_X, HIP_Y)."""
    m = Stickman(pose=pose).place(MOM_X, HIP_Y)
    return VGroup(m, bun_for(pose, MOM_X, HIP_Y), skirt_for(pose, MOM_X, HIP_Y))


def build_dad(pose: PoseAngles, hip_x: float, hip_y: float) -> VGroup:
    """Dad: stickman + tie, hip at (hip_x, hip_y)."""
    d = Stickman(pose=pose).place(hip_x, hip_y)
    return VGroup(d, tie_for(pose, hip_x, hip_y))


def vase_prop() -> VGroup:
    """The broken vase: overturned body + shards + a fallen flower."""
    body = RoundedRectangle(
        corner_radius=0.08, width=0.55, height=0.85, color=INK, stroke_width=5,
    )
    body.set_fill(opacity=0)
    body.rotate(math.radians(75), about_point=body.get_center())
    body.move_to([0, 0.15, 0])
    shard1 = Polygon([0.35, 0, 0], [0.55, 0, 0], [0.45, 0.16, 0],
                     color=INK, stroke_width=4)
    shard2 = Polygon([-0.55, 0, 0], [-0.35, 0, 0], [-0.45, 0.13, 0],
                     color=INK, stroke_width=4)
    stem = Line([-0.9, 0.05, 0], [-0.35, 0.05, 0], color=INK, stroke_width=4)
    bloom = Circle(radius=0.11, color=ACCENT, stroke_width=4)
    bloom.set_fill(ACCENT, opacity=1)
    bloom.move_to([-1.0, 0.05, 0])
    return VGroup(body, shard1, shard2, stem, bloom)


def pillow_prop() -> RoundedRectangle:
    """Na's pillow: soft rounded rectangle she hugs."""
    p = RoundedRectangle(
        corner_radius=0.15, width=0.95, height=0.55, color=INK, stroke_width=5,
    )
    p.set_fill(WHITE, opacity=1)
    return p


def door_prop() -> VGroup:
    """The front door: frame + slightly open panel, on the left wall."""
    frame = Rectangle(width=1.3, height=4.6, color=INK, stroke_width=6)
    frame.set_fill(opacity=0)
    frame.move_to([DOOR_X, GROUND_Y + 2.3, 0])
    panel = Rectangle(width=1.0, height=4.3, color=INK, stroke_width=4)
    panel.set_fill(SPEC["BG"], opacity=1)
    panel.move_to([DOOR_X - 0.12, GROUND_Y + 2.15, 0])
    knob = Dot(point=[DOOR_X + 0.25, GROUND_Y + 2.3, 0], radius=0.06, color=INK)
    return VGroup(frame, panel, knob)


class StickmanScene(StickmanScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.t_now = 0.0

    def seg(self, dur: float):
        if dur > 0:
            self.wait(dur)
            self.t_now += dur

    def wait_until(self, t: float):
        self.seg(t - self.t_now)

    # ------------------------------------------------------------ construct
    def construct(self):
        ground = ground_line(GROUND_Y)
        door = door_prop()
        clock = clock_wall(1.0)
        clock.move_to([CLOCK_X, CLOCK_Y, 0])
        vase = vase_prop()
        vase.move_to([2.0, GROUND_Y + 0.1, 0])
        pillow = pillow_prop()
        pillow.move_to([NA_X + 0.42, GROUND_Y + 0.55, 0])

        warm = Rectangle(width=9, height=16, color=WARM, stroke_width=0)
        warm.set_fill(WARM, opacity=0.05)
        warm.move_to([0, 0, 0])
        glow = Circle(radius=2.2, color=WARM, stroke_width=0)
        glow.set_fill(WARM, opacity=0.18)
        glow.move_to([2.2, -1.0, 0])

        self.add(ground, door, clock, vase)

        # ---- HOOK (0 - 4.796): Na alone, sad, broken vase, card 1
        hook_card = card("LÀM VỠ LỌ HOA RỒI.")
        na_sad = build_na(POSE_SAD, NA_X, HIP_Y)
        self.add(na_sad)
        self.play(FadeIn(hook_card, shift=UP * 0.3), run_time=0.5)
        self.t_now += 0.5
        self.wait_until(HOOK_END)

        # ---- BEAT 1 (4.796 - 14.594): Mom points/scolds; Na head down
        card1 = card("MẸ MẮNG MỘT CÂU.")
        mom = build_mom(POSE_MOM)
        self.play(
            FadeOut(hook_card),
            FadeIn(card1, shift=UP * 0.3),
            FadeIn(mom),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.wait_until(BEAT1_END)

        # ---- BEAT 2 (14.594 - 24.702): Mom gone; Na sits sulking, pillow
        card2 = card("KHÔNG THÈM NÓI VỚI AI.")
        na_sulk = build_na(POSE_SULK, NA_X, NA_SIT_HIP_Y)
        self.remove(na_sad)
        self.add(na_sulk)
        self.play(
            FadeOut(card1),
            FadeOut(mom),
            FadeIn(card2, shift=UP * 0.3),
            FadeIn(pillow),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.wait_until(BEAT2_END)

        # ---- BEAT 3 (24.702 - 35.5): Dad walks in, sits down beside Na
        card3 = card("BỐ VỀ RỒI.")
        card4 = card("BỐ CHỈ NGỒI XUỐNG.")
        walk_t = ValueTracker(0.0)

        def build_dad_walk():
            w = walk_t.get_value()
            phase = w * walk_phase_for_distance(6.2)
            x = -4.6 + 6.2 * w
            hip_y = (GROUND_Y + (SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"])
                     + walk_bob(phase))
            d = Stickman(pose=walk_pose(phase))
            d.place(x, hip_y)
            return VGroup(d, tie_for(walk_pose(phase), x, hip_y))

        dad_walk = always_redraw(build_dad_walk)
        dad_sit = build_dad(POSE_DAD_SIT, DAD_X, SIT_HIP_Y)
        self.play(
            FadeOut(card2),
            FadeIn(card3, shift=UP * 0.3),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.add(dad_walk)
        # Walk must finish exactly at CLAUSE2_AT (30.116): 30.116 - 25.202.
        self.play(walk_t.animate.set_value(1.0), run_time=4.914, rate_func=linear)
        self.t_now += 4.914
        self.remove(dad_walk)
        self.add(dad_sit)
        self.play(
            FadeOut(card3),
            FadeIn(card4, shift=UP * 0.3),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.wait_until(BEAT3_END)

        # ---- PAYOFF (35.5 - 45.186): warm glow; dad hugs Na, both smile
        # The 2-line payoff card is taller than the others — raise it so
        # its bottom clears the wall clock (v1 overlapped the clock).
        card5 = card("CON GÁI CỦA BỐ ĐÂY RỒI.")
        card5.move_to([0, 5.0, 0])
        dad_hug = build_dad(POSE_DAD_HUG, DAD_X, SIT_HIP_Y)
        na_hug = build_na(POSE_NA_HUG, NA_X, NA_SIT_HIP_Y)
        self.remove(dad_sit)
        self.remove(na_sulk)
        self.add(dad_hug)
        self.add(na_hug)
        self.play(
            FadeOut(card4),
            FadeOut(pillow),
            FadeIn(card5, shift=UP * 0.3),
            FadeIn(glow),
            FadeIn(warm),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.wait_until(PAYOFF_END)

        # ---- CTA (45.186 - 49.5): end card, hug held
        card6 = card("AI LÀ CON GÁI CỦA BỐ?")
        self.play(
            FadeOut(card5),
            FadeIn(card6, shift=UP * 0.3),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.wait_until(TOTAL)
