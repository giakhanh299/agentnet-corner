"""Ep001 — "Cung lam 10 tieng, sao nguoi giau, nguoi ngheo?" (F7, 50s).

Timeline follows the MEASURED MMS voice (voice.wav, 48.75s after trimming
0.28s of leading silence). Beat boundaries are the nominal segment
boundaries shifted by the trim; fine-tune BEAT_END_* after reading
captions.srt if a beat's audible speech starts/ends clearly off them.

    HOOK   0.00 -  4.48   1 stickman centre, surprised, hook card
    BEAT 1 4.48 - 17.07   An walks in from the left, clock, sad at the end
    BEAT 2 17.07 - 31.17  Binh: think -> point, money bag + coins appear
    BEAT 3 31.17 - 42.32  An (sad, left) + Binh (happy, right) side by side
    PAYOFF 42.32 - 49.50  Binh centre, waving, payoff card + end question

Video is rendered ~0.75s longer than the voice; assemble.py uses
-shortest so the final mp4 ends with the voice (48.75s).

Run:  tools/render.sh videos/2026-11-15_ep001-cam-dau-lam-viec/scene.py StickmanScene
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from manim import UP, FadeIn, FadeOut, ValueTracker, always_redraw, config, linear

from config import GROUND_Y, SPEC
from src.rig.character import Stickman
from src.rig.gestures import point_pose, think_pose, wave_pose
from src.rig.poses import POSE_HAPPY, POSE_SAD, POSE_SURPRISED, lerp_pose
from src.rig.props import clock_wall, coin_stack, ground_line, money_bag
from src.rig.walk import walk_bob, walk_pose
from src.scenes.base_scene import StickmanScene
from src.scenes.text_card import TextCard
from src.utils.export import apply_video_config

apply_video_config()
config.background_color = SPEC["BG"]

# ------------------------------------------------------------ beat boundaries (seconds)
# From captions.srt (audible speech): hook ends 4.06, beat1 4.80-17.06,
# beat2 17.70-31.60, beat3 31.60-42.36, payoff 43.08-48.75. Cuts land in
# the silence gaps between beats.
HOOK_END = 4.20
BEAT1_END = 17.07
BEAT2_END = 31.60
BEAT3_END = 42.32
TOTAL = 49.50

CARD_Y = 4.6
HIP_Y = GROUND_Y + SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]


def card(title, subtitle=None):
    c = TextCard(title, subtitle=subtitle)
    c.move_to([0, CARD_Y, 0])
    return c


class StickmanScene(StickmanScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.t_now = 0.0

    def seg(self, dur: float):
        """Wait out a timed segment, tracking elapsed scene time."""
        if dur > 0:
            self.wait(dur)
            self.t_now += dur

    def wait_until(self, t: float):
        """Wait until absolute time ``t``."""
        self.seg(t - self.t_now)

    # ------------------------------------------------------------ construct
    def construct(self):
        ground = ground_line(GROUND_Y)
        self.add(ground)

        # ---- HOOK (0 - 4.48): one stickman centre, surprised + hook card
        hook_card = card("CÙNG LÀM 10 TIẾNG", "Sao người giàu, người nghèo?")
        hook_man = Stickman(pose=POSE_SURPRISED).place(0, HIP_Y)
        self.add(hook_man)
        self.play(FadeIn(hook_card, shift=UP * 0.3), run_time=0.5)
        self.t_now += 0.5
        self.wait_until(HOOK_END)

        # ---- BEAT 1 (4.48 - 17.07): An walks in, clock, ends sad
        card1 = card("AN ĐỔI GIỜ LẤY TIỀN", "10 tiếng một ngày, lương theo giờ")
        clock = clock_wall(1.0)
        clock.move_to([2.9, 1.2, 0])

        walk_in = ValueTracker(0.0)   # 0 -> 1: walk in from the left
        tread = ValueTracker(0.0)     # keeps advancing: walk-in-place phase
        sad_blend = ValueTracker(0.0)  # 0 -> 1: blend walk pose into sad

        def build_an():
            w = walk_in.get_value()
            phase = (w * 2 * math.pi * 3.0) + tread.get_value()
            pose = walk_pose(phase)
            if sad_blend.get_value() > 0:
                pose = lerp_pose(pose, POSE_SAD, sad_blend.get_value())
            x = -5.5 + (2.3) * min(1.0, w)  # -5.5 -> -3.2
            y = HIP_Y + walk_bob(phase) * (1.0 - sad_blend.get_value())
            return Stickman(pose=pose).place(x, y)

        an = always_redraw(build_an)
        self.play(
            FadeOut(hook_card),
            FadeOut(hook_man),
            FadeIn(card1, shift=UP * 0.3),
            FadeIn(clock),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.add(an)
        self.play(walk_in.animate.set_value(1.0), run_time=3.0, rate_func=linear)
        self.t_now += 3.0
        # walk in place until 1.2s before the beat ends, then go sad
        self.play(tread.animate.set_value(2 * math.pi * 3.0), run_time=6.5, rate_func=linear)
        self.t_now += 6.5
        self.play(sad_blend.animate.set_value(1.0), run_time=0.8)
        self.t_now += 0.8
        self.wait_until(BEAT1_END)

        # ---- BEAT 2 (17.07 - 31.17): Binh thinks, points, money appears
        card2 = card("BÌNH XÂY CÂY CẦU", "5 tiếng làm thuê, 5 tiếng học cách khác")
        think = ValueTracker(0.0)  # 0 -> 1: neutral -> think
        point = ValueTracker(0.0)  # 0 -> 1: think -> point

        def build_binh():
            base = lerp_pose(POSE_HAPPY, think_pose(), think.get_value())
            pose = lerp_pose(base, point_pose(), point.get_value())
            return Stickman(pose=pose).place(0.9, HIP_Y)

        binh = always_redraw(build_binh)
        bag = money_bag(1.0)
        bag.move_to([-2.4, -3.0, 0])
        coins = coin_stack(1.0)
        coins.move_to([2.6, -3.25, 0])

        # always_redraw stickmen must be added/removed, never faded
        # (a fade is undone by the updater on the next frame).
        self.remove(an)
        self.add(binh)
        self.play(
            FadeOut(card1),
            FadeOut(clock),
            FadeIn(card2, shift=UP * 0.3),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.play(think.animate.set_value(1.0), run_time=1.0)
        self.t_now += 1.0
        self.play(FadeIn(bag), FadeIn(coins), run_time=0.6)
        self.t_now += 0.6
        # hold the think pose while the "5 tieng hoc" lines play
        self.seg(4.0)
        self.play(point.animate.set_value(1.0), run_time=0.8)
        self.t_now += 0.8
        self.wait_until(BEAT2_END)

        # ---- BEAT 3 (31.17 - 42.32): An (sad, left) + Binh (happy, right)
        card3 = card("MỘT NĂM SAU", "Cùng một sức, khác nhau ở cách nghĩ")
        binh3 = Stickman(pose=POSE_HAPPY).place(2.2, HIP_Y)
        bag3 = money_bag(1.0)
        bag3.move_to([3.2, -3.0, 0])  # beside Binh, not under his feet
        # An keeps walking in place (treadmill), Binh stands still.
        tread3 = ValueTracker(0.0)

        def build_an3():
            phase = tread3.get_value()
            pose = walk_pose(phase)
            return Stickman(pose=pose).place(-2.2, HIP_Y + walk_bob(phase))

        an3_walk = always_redraw(build_an3)

        self.remove(binh)
        self.add(an3_walk)
        self.play(
            FadeOut(bag),
            FadeOut(coins),
            FadeOut(card2),
            FadeIn(card3, shift=UP * 0.3),
            FadeIn(binh3),
            FadeIn(bag3),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.play(tread3.animate.set_value(2 * math.pi * 4.0), run_time=8.0, rate_func=linear)
        self.t_now += 8.0
        self.wait_until(BEAT3_END)

        # ---- PAYOFF (42.32 - 49.50): Binh centre, waving, payoff card
        card4 = card("GIÀU LÀ LÀM KHÁC ĐI", "Bạn chọn bên nào?")
        wave = ValueTracker(0.0)

        def build_binh_wave():
            return Stickman(pose=wave_pose(wave.get_value() * 2 * math.pi * 2.0)).place(0, HIP_Y)

        binh_wave = always_redraw(build_binh_wave)
        self.remove(an3_walk)
        self.add(binh_wave)
        self.play(
            FadeOut(binh3),
            FadeOut(bag3),
            FadeOut(card3),
            FadeIn(card4, shift=UP * 0.3),
            run_time=0.5,
        )
        self.t_now += 0.5
        self.add(binh_wave)
        self.play(wave.animate.set_value(1.0), run_time=2.0, rate_func=linear)
        self.t_now += 2.0
        self.wait_until(TOTAL)
