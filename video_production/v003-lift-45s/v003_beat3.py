"""V003 beat 3 — stickman lying flat, hands over head (15 s, 1080x1920, 30 fps).

Beat 3 (25-38s in the script): "cách khoa học nhất là nằm dài xuống sàn,
tay ôm đầu" — the scientific advice is to lie flat so the impact spreads.
0-2 s:   stickman rotates from standing to lying (about the hip point).
2-15 s:  hold lying, arms over head.
No text in this clip — the label "NẰM DÀI — TRẢI ĐỀU LỰC" is drawn by
ffmpeg in the assembly step (same as v002 labels).

Run from the stickman-shorts repo:
  .venv/bin/manim render -qm --format=mp4 \
    ../video_production/v003-lift-45s/v003_beat3.py LyingScene
Output: media/videos/v003_beat3/1080p30/LyingScene.mp4 (copy to v003 dir).
"""

import math
import os
import sys

sys.path.insert(0, "/home/hatch/workspace/agentnet-corner/stickman-shorts")

from manim import DOWN, ValueTracker, always_redraw, config, linear
import numpy as np

from config import GROUND_Y, SPEC
from src.rig.character import Stickman
from src.rig.poses import PoseAngles
from src.rig.props import ground_line
from src.scenes.base_scene import StickmanScene
from src.utils.export import apply_video_config

apply_video_config()
config.background_color = SPEC["BG"]

HIP_REST_Y = GROUND_Y + SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]  # -1.5
HIP_X = -0.3
# Arms: rest UP-LEFT along the body, hands folded over the chest/stomach.
# (Verified from the rig's FK + two failed renders: the shoulder sits
# directly under the head, so any arm pointing right (toward the head)
# disappears behind the head circle, which is filled and drawn after the
# arms. Arms pointing left-up — sh negative — clear the head entirely and
# stay above the ground line. This is the natural "lying with hands
# folded" pose; the label + narration carry "tay ôm đầu".)
POSE_LYING = PoseAngles(
    shoulder_l=-0.35, elbow_l=-0.35,
    shoulder_r=-0.15, elbow_r=-0.6,
    hip_l=0.12, hip_r=-0.12,
    knee_l=0.15, knee_r=0.1,
    expression="neutral",
)
# At -90 deg the torso line must sit one head-radius above the ground line.
DROP = (HIP_REST_Y - GROUND_Y) - SPEC["HEAD_R"]  # 1.5


class LyingScene(StickmanScene):
    def construct(self):
        angle = ValueTracker(0.0)  # radians; 0 = standing, -pi/2 = lying

        def build_stickman():
            a = angle.get_value()
            stick = Stickman(pose=POSE_LYING).place(HIP_X, HIP_REST_Y)
            stick.rotate(a, about_point=np.array([HIP_X, HIP_REST_Y, 0]))
            stick.shift(DOWN * DROP * math.sin(abs(a)))
            return stick

        stick = always_redraw(build_stickman)
        ground = ground_line(GROUND_Y)

        self.add(ground, stick)
        self.play(angle.animate.set_value(-math.pi / 2), run_time=2.0, rate_func=linear)
        self.wait(13.0)
