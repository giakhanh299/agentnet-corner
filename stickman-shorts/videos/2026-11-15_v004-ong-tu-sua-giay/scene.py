"""v004 — "Ong Tu sua giay" (F7, 50s): emotional stickman story.

Fully ORIGINAL story (the #50 original carries "© 2026 Christopher
Thomas. All Rights Reserved." on every frame): old shoe repairman +
little girl, street-corner stall at dusk, unclaimed small shoes + a
child's drawing, payoff "Chi can mot nguoi dung lai." Only the
mechanism is kept (stickman + text cards + music-driven emotion).
NO rain (the original's rainy park bench is deliberately avoided).

Timeline follows the MEASURED MMS voice (voice.wav, 52.36s;
timing.json) — beat boundaries are the measured segment starts:

    HOOK    0.00 -  3.58   Tu alone, sad, card 1
    BEAT 1  3.58 - 17.22   Tu sad at the stall, one passerby walks by
    BEAT 2 17.22 - 30.69   Tu polishes the small shoe (in hand, then
                           on the stall from 25.94), card 3
    BEAT 3 30.69 - 46.03   Girl walks in, points at the shoe (card 4a);
                           returns with the drawing at 37.91 (card 4b)
    PAYOFF 46.03 - 53.11   Lamp lights up (warm), Tu smiles + nods,
                           girl happy beside him, card 5

Video is rendered ~0.75s longer than the voice; assemble uses
-shortest so the final mp4 ends with the voice (52.36s).

Run (on the PC, venv-win):
    python -m manim render -qm --format=mp4 videos/2026-11-15_v004-ong-tu-sua-giay/scene.py StickmanScene
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from manim import (
    UP, Arc, Circle, Dot, FadeIn, FadeOut, Line, Rectangle, RoundedRectangle,
    ValueTracker, VGroup, always_redraw, config, linear,
)

from config import GROUND_Y, SPEC
from src.rig.character import Stickman, joint_positions
from src.rig.gestures import nod_pose, point_pose
from src.rig.poses import POSE_HAPPY, POSE_SAD, PoseAngles, lerp_pose
from src.rig.props import ground_line
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
LAMP_WARM = "#F2C94C"

# ------------------------------------------------------------ beat boundaries (seconds, measured voice)
HOOK_END = 3.58
BEAT1_END = 17.22
BEAT2_END = 30.69
CARD4B_AT = 37.91      # "Hom sau, be quay lai" — drawing appears
BEAT3_END = 46.03
TOTAL = 53.11

CARD_Y = 4.6
HIP_Y = GROUND_Y + SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]  # -1.5
TU_X = -0.9            # ong Tu's hip x (behind the stall)
GIRL_X = -3.1          # be gai's hip x (left of the stall)
GIRL_SCALE = 0.62
GIRL_HIP_Y = GROUND_Y + (SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]) * GIRL_SCALE
STALL_TOP = -2.0       # stall surface y
LAMP_X = 3.4

# Polishing poses: right arm reaches down-forward toward the shoe,
# head tilted down at it. Only the arm angles oscillate.
POLISH_A = PoseAngles(
    torso_lean=0.10, head_tilt=0.18,
    shoulder_r=0.55, elbow_r=0.35,
    shoulder_l=0.25, elbow_l=0.6,
    hip_l=0.12, hip_r=-0.12, expression="focused",
)
POLISH_B = PoseAngles(
    torso_lean=0.10, head_tilt=0.18,
    shoulder_r=0.35, elbow_r=0.60,
    shoulder_l=0.25, elbow_l=0.6,
    hip_l=0.12, hip_r=-0.12, expression="focused",
)
# Watching the girl (she is to his left): head turned left.
POSE_WATCH = PoseAngles(
    torso_lean=-0.05, head_tilt=-0.18,
    hip_l=0.12, hip_r=-0.12, expression="neutral",
)


def card(title, subtitle=None):
    c = TextCard(title, subtitle=subtitle)
    c.move_to([0, CARD_Y, 0])
    return c


def hat_for(pose: PoseAngles, hip_x: float, hip_y: float) -> VGroup:
    """Ong Tu's hat: brim + dome, following the head angle."""
    j = joint_positions(pose)
    hc = j["head_center"] + np.array([hip_x, hip_y, 0.0])
    ang = j["head_angle"]
    brim = Line(
        hc + np.array([-0.45, 0.42, 0]), hc + np.array([0.45, 0.42, 0]),
        color=INK, stroke_width=6,
    )
    dome = Arc(
        radius=0.32, start_angle=0, angle=math.pi,
        arc_center=hc + np.array([0, 0.42, 0]), color=INK, stroke_width=6,
    )
    hat = VGroup(brim, dome)
    hat.rotate(ang, about_point=hc)
    return hat


def apron_for(pose: PoseAngles, hip_x: float, hip_y: float) -> Rectangle:
    """Ong Tu's apron: grey rectangle over the lower torso."""
    j = joint_positions(pose)
    hip = np.array([hip_x, hip_y, 0.0])
    shoulder = j["shoulder"] + hip
    top = shoulder + np.array([0, -0.25, 0])
    bottom = hip + np.array([0, 0.35, 0])
    cx = (top[0] + bottom[0]) / 2
    cy = (top[1] + bottom[1]) / 2
    rect = Rectangle(width=0.7, height=top[1] - bottom[1], color=GREY, stroke_width=4)
    rect.move_to([cx, cy, 0])
    return rect


def build_tu(pose: PoseAngles) -> VGroup:
    """Ong Tu: stickman + hat + apron, hip at (TU_X, HIP_Y)."""
    man = Stickman(pose=pose).place(TU_X, HIP_Y)
    return VGroup(man, hat_for(pose, TU_X, HIP_Y), apron_for(pose, TU_X, HIP_Y))


def hair_tie_for(pose: PoseAngles, hip_x: float, hip_y: float, scale: float) -> Dot:
    """Be gai's tied hair: small accent dot at the back of her head."""
    j = joint_positions(pose)
    hc = j["head_center"] * scale + np.array([hip_x, hip_y, 0.0])
    return Dot(point=hc + np.array([-0.26 * scale, 0.05, 0]), radius=0.10, color=ACCENT)


def build_girl(pose: PoseAngles) -> VGroup:
    """Be gai: smaller stickman + hair tie, hip at (GIRL_X, GIRL_HIP_Y)."""
    g = Stickman(pose=pose).scale(GIRL_SCALE, about_point=np.array([0.0, 0.0, 0.0]))
    g.place(GIRL_X, GIRL_HIP_Y)
    return VGroup(g, hair_tie_for(pose, GIRL_X, GIRL_HIP_Y, GIRL_SCALE))


def shoe_prop() -> VGroup:
    """The small shoe: sole + upper, origin at the sole's bottom centre."""
    sole = RoundedRectangle(
        corner_radius=0.05, width=0.55, height=0.12, color=INK, stroke_width=5,
    )
    sole.set_fill(opacity=0)
    sole.move_to([0, 0.06, 0])
    upper = Rectangle(width=0.34, height=0.22, color=INK, stroke_width=5)
    upper.set_fill(opacity=0)
    upper.move_to([-0.06, 0.23, 0])
    return VGroup(sole, upper)


def stall_prop() -> VGroup:
    """The repair stall: a workbench the man stands behind."""
    table = Rectangle(width=2.4, height=1.5, color=INK, stroke_width=8)
    table.set_fill(SPEC["BG"], opacity=1)
    table.move_to([TU_X, STALL_TOP - 0.75, 0])
    return VGroup(table)


def drawing_prop() -> VGroup:
    """The girl's drawing: paper + tiny stickman + little sun."""
    paper = Rectangle(width=0.9, height=1.2, color=INK, stroke_width=5)
    paper.set_fill(WHITE, opacity=1)
    tiny = Stickman().scale(0.12, about_point=np.array([0.0, 0.0, 0.0]))
    tiny.place(-0.08, -0.35)
    sun = Circle(radius=0.09, color=ACCENT, stroke_width=4)
    sun.set_fill(ACCENT, opacity=1)
    sun.move_to([0.28, 0.42, 0])
    return VGroup(paper, tiny, sun)


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
        stall = stall_prop()
        lamp_pole = Line(
            [LAMP_X, GROUND_Y, 0], [LAMP_X, 2.2, 0], color=INK, stroke_width=6,
        )
        lamp_head = Circle(radius=0.28, color=INK, stroke_width=6)
        lamp_head.move_to([LAMP_X, 2.45, 0])
        lamp_head.set_fill(opacity=0)
        glow = Circle(radius=1.3, color=LAMP_WARM, stroke_width=0)
        glow.set_fill(LAMP_WARM, opacity=0.18)
        glow.move_to([LAMP_X, 2.45, 0])
        warm = Rectangle(width=9, height=16, color=LAMP_WARM, stroke_width=0)
        warm.set_fill(LAMP_WARM, opacity=0.05)
        warm.move_to([0, 0, 0])

        self.add(ground)

        # ---- HOOK (0 - 3.58): Tu alone, sad, card 1
        hook_card = card("KHÔNG AI NHÌN ÔNG MỘT LẦN.")
        tu_sad = build_tu(POSE_SAD)
        self.add(tu_sad)
        self.add(stall, lamp_pole, lamp_head)
        self.play(FadeIn(hook_card, shift=UP * 0.3), run_time=0.5)
        self.t_now += 0.5
        self.wait_until(HOOK_END)

        # ---- BEAT 1 (3.58 - 17.22): Tu sad; one passerby walks by
        card1 = card("BA MƯƠI NĂM Ở GÓC PHỐ NÀY.")
        walk_t = ValueTracker(0.0)

        def build_walker():
            w = walk_t.get_value()
            phase = w * walk_phase_for_distance(9.2)
            x = -4.6 + 9.2 * w
            m = Stickman(pose=walk_pose(phase))
            m.scale(0.8, about_point=np.array([0.0, 0.0, 0.0]))
            m.place(x, GROUND_Y + (SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]) * 0.8
                    + walk_bob(phase) * 0.8)
            return m

        walker = always_redraw(build_walker)
        self.play(
            FadeOut(hook_card),
            FadeIn(card1, shift=UP * 0.3),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.wait_until(5.0)
        self.add(walker)
        self.play(walk_t.animate.set_value(1.0), run_time=8.0, rate_func=linear)
        self.t_now += 8.0
        self.remove(walker)
        self.wait_until(BEAT1_END)

        # ---- BEAT 2 (17.22 - 30.69): Tu polishes the small shoe
        card2 = card("ĐÔI GIÀY KHÔNG AI LẤY.")
        shoe_hand = shoe_prop()
        shoe_hand.move_to([0.15, -0.31, 0])  # at his right hand, chest height
        shoe_stall = shoe_prop()
        shoe_stall.move_to([TU_X, STALL_TOP + 0.14, 0])
        rub = ValueTracker(0.0)

        def build_tu_polish():
            k = 0.5 + 0.5 * math.sin(rub.get_value() * 2 * math.pi * 6.0)
            return build_tu(lerp_pose(POLISH_A, POLISH_B, k))

        tu_polish = always_redraw(build_tu_polish)
        self.remove(tu_sad)
        self.add(tu_polish)
        self.bring_to_front(stall)  # the man stands BEHIND the stall
        self.play(
            FadeOut(card1),
            FadeIn(card2, shift=UP * 0.3),
            FadeIn(shoe_hand),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.play(rub.animate.set_value(0.65), run_time=7.8, rate_func=linear)
        self.t_now += 7.8
        # "Ong de doi giay tren quay nho" (25.94): shoe goes onto the stall
        self.play(
            FadeOut(shoe_hand),
            FadeIn(shoe_stall),
            run_time=0.4,
        )
        self.t_now += 0.4
        self.bring_to_front(stall, shoe_stall)  # shoe sits ON the stall
        self.play(rub.animate.set_value(1.0), run_time=3.9, rate_func=linear)
        self.t_now += 3.9
        self.wait_until(BEAT2_END)

        # ---- BEAT 3 (30.69 - 46.03): the girl walks in, points, returns
        card3 = card("CỦA AI VẬY ÔNG?")
        card4 = card("BỨC VẼ CỦA BÉ.")
        tu_watch = build_tu(POSE_WATCH)
        girl_in = ValueTracker(0.0)

        def build_girl_in():
            w = girl_in.get_value()
            phase = w * walk_phase_for_distance(1.5)
            x = -4.6 + 1.5 * w
            g = Stickman(pose=walk_pose(phase))
            g.scale(GIRL_SCALE, about_point=np.array([0.0, 0.0, 0.0]))
            g.place(x, GIRL_HIP_Y + walk_bob(phase) * GIRL_SCALE)
            return VGroup(g, hair_tie_for(walk_pose(phase), x, GIRL_HIP_Y, GIRL_SCALE))

        girl_walk = always_redraw(build_girl_in)
        girl_point = build_girl(point_pose())
        drawing = drawing_prop()
        drawing.move_to([-1.95, -0.85, 0])  # at her pointing hand

        self.remove(tu_polish)
        self.add(tu_watch)
        self.bring_to_front(stall, shoe_stall)
        self.play(
            FadeOut(card2),
            FadeIn(card3, shift=UP * 0.3),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.add(girl_walk)
        self.play(girl_in.animate.set_value(1.0), run_time=2.31, rate_func=linear)
        self.t_now += 2.31
        self.remove(girl_walk)
        self.add(girl_point)
        self.wait_until(CARD4B_AT)
        self.play(
            FadeOut(card3),
            FadeIn(card4, shift=UP * 0.3),
            FadeIn(drawing),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.wait_until(BEAT3_END)

        # ---- PAYOFF (46.03 - 53.11): lamp lights up, Tu smiles + nods
        card5 = card("CHỈ CẦN MỘT NGƯỜI DỪNG LẠI.")
        girl_happy = build_girl(POSE_HAPPY)
        nod = ValueTracker(0.0)

        def build_tu_nod():
            return build_tu(nod_pose(nod.get_value() * 2 * math.pi * 2.0))

        tu_nod = always_redraw(build_tu_nod)
        self.remove(tu_watch)
        self.remove(girl_point)
        self.add(tu_nod)
        self.add(girl_happy)
        self.bring_to_front(stall, shoe_stall)
        self.play(
            FadeOut(card4),
            FadeIn(card5, shift=UP * 0.3),
            FadeIn(glow),
            FadeIn(warm),
            lamp_head.animate.set_fill(LAMP_WARM, opacity=1),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.play(nod.animate.set_value(1.0), run_time=6.0, rate_func=linear)
        self.t_now += 6.0
        self.wait_until(TOTAL)
