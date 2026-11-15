"""Demo: 5 s, 1080x1920, 30 fps.
0-2 s:   stickman walks in from the left.
2-3.5 s: stops, waves; the title card pops in.
3.5-5 s: hold.

Run:  tools/render.sh stickman_demo.py StickmanScene
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manim import UP, FadeIn, ValueTracker, always_redraw, config, linear

from config import GROUND_Y, SPEC
from src.rig.character import Stickman
from src.rig.gestures import wave_pose
from src.rig.poses import lerp_pose
from src.rig.props import ground_line
from src.rig.walk import walk_bob, walk_pose
from src.scenes.base_scene import StickmanScene
from src.scenes.text_card import TextCard
from src.utils.export import apply_video_config

apply_video_config()
config.background_color = SPEC["BG"]

HIP_REST_Y = GROUND_Y + SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]
WALK_FROM_X = -5.5
WALK_TO_X = 0.0
WALK_CYCLES = 2.5   # full walk cycles while crossing the frame
WAVE_CYCLES = 3.0   # full hand waves


class StickmanScene(StickmanScene):
    def construct(self):
        walk = ValueTracker(0.0)
        wave = ValueTracker(0.0)

        def build_stickman():
            wt = walk.get_value()
            if wt < 1.0:
                phase = wt * 2 * math.pi * WALK_CYCLES
                pose = walk_pose(phase)
                x = WALK_FROM_X + (WALK_TO_X - WALK_FROM_X) * wt
                y = HIP_REST_Y + walk_bob(phase)
            else:
                # Blend from the last walk pose into the wave so the
                # transition does not snap.
                wv = wave.get_value()
                base = walk_pose(2 * math.pi * WALK_CYCLES)
                blend = min(1.0, wv * 4.0)
                pose = lerp_pose(base, wave_pose(wv * 2 * math.pi * WAVE_CYCLES), blend)
                x, y = WALK_TO_X, HIP_REST_Y
            return Stickman(pose=pose).place(x, y)

        stick = always_redraw(build_stickman)
        ground = ground_line(GROUND_Y)
        card = TextCard("TÂM SỰ NGƯỜI QUE")
        card.move_to([0, 4.6, 0])

        self.add(ground, stick)
        self.play(walk.animate.set_value(1.0), run_time=2.0, rate_func=linear)
        self.play(
            wave.animate.set_value(1.0),
            FadeIn(card, shift=UP * 0.3),
            run_time=1.5,
        )
        self.wait(1.5)
