"""The stickman rig: ONE class, built once, reused by every video.

Geometry is pure forward kinematics. The character's local origin is the
HIP; every joint position is computed from the pose angles in
``poses.py`` — no coordinates are ever hardcoded in a scene.

Parts (all in Manim frame units, from config.SPEC):
    head    Circle radius HEAD_R, filled with the background colour
    neck    Line shoulder -> head base
    torso   Line hip -> shoulder
    arms    two segments each: shoulder -> elbow -> hand
    legs    two segments each: hip -> knee -> foot
    face    eyes + mouth, rotated with the head (see expressions.py)

Usage:
    stick = Stickman()                 # neutral pose, hip at (0, 0)
    stick.place(x, y)                  # put the HIP at (x, y)
    stick.set_pose(walk_pose(phase))   # real pose change, no pass bodies
    stick.walk(phase)                  # shorthand for set_pose(walk_pose)
    stick.wave(phase)                  # shorthand for set_pose(wave_pose)
"""

from __future__ import annotations

import math

import numpy as np
from manim import Circle, Line, VGroup

from config import SPEC
from .expressions import build_face
from .gestures import wave_pose
from .poses import PoseAngles
from .walk import walk_pose

INK = SPEC["INK"]
BG = SPEC["BG"]
STROKE = SPEC["STROKE"]


def _dir_up(angle: float) -> np.ndarray:
    """Unit vector at ``angle`` from straight up; +angle = toward +x."""
    return np.array([math.sin(angle), math.cos(angle), 0.0])


def _dir_down(angle: float) -> np.ndarray:
    """Unit vector at ``angle`` from straight down; +angle = toward +x."""
    return np.array([math.sin(angle), -math.cos(angle), 0.0])


def joint_positions(pose: PoseAngles) -> dict[str, np.ndarray]:
    """Forward kinematics: every joint position from the pose angles."""
    hip = np.array([0.0, 0.0, 0.0])
    shoulder = hip + SPEC["TORSO"] * _dir_up(pose.torso_lean)
    head_dir = _dir_up(pose.torso_lean + pose.head_tilt)
    neck_top = shoulder + SPEC["NECK"] * head_dir
    head_center = neck_top + SPEC["HEAD_R"] * head_dir

    def arm(side: str):
        sh = getattr(pose, f"shoulder_{side}")
        el = getattr(pose, f"elbow_{side}")
        elbow = shoulder + SPEC["UPPER_ARM"] * _dir_down(sh)
        hand = elbow + SPEC["LOWER_ARM"] * _dir_down(sh + el)
        return elbow, hand

    def leg(side: str):
        hp = getattr(pose, f"hip_{side}")
        kn = getattr(pose, f"knee_{side}")
        knee = hip + SPEC["UPPER_LEG"] * _dir_down(hp)
        foot = knee + SPEC["LOWER_LEG"] * _dir_down(hp + kn)
        return knee, foot

    elbow_l, hand_l = arm("l")
    elbow_r, hand_r = arm("r")
    knee_l, foot_l = leg("l")
    knee_r, foot_r = leg("r")
    return {
        "hip": hip,
        "shoulder": shoulder,
        "neck_top": neck_top,
        "head_center": head_center,
        "head_angle": pose.torso_lean + pose.head_tilt,
        "elbow_l": elbow_l, "hand_l": hand_l,
        "elbow_r": elbow_r, "hand_r": hand_r,
        "knee_l": knee_l, "foot_l": foot_l,
        "knee_r": knee_r, "foot_r": foot_r,
    }


class Stickman(VGroup):
    """A stickman whose shape is fully determined by a PoseAngles."""

    def __init__(self, pose: PoseAngles | None = None, **kwargs):
        super().__init__(**kwargs)
        self.pose = pose or PoseAngles()
        self._hip = np.array([0.0, 0.0, 0.0])

        kw = {"color": INK, "stroke_width": STROKE}
        self.torso = Line(**kw)
        self.neck = Line(**kw)
        self.head = Circle(radius=SPEC["HEAD_R"], **kw)
        self.head.set_fill(BG, opacity=1)
        self.arm_l_u = Line(**kw)
        self.arm_l_f = Line(**kw)
        self.arm_r_u = Line(**kw)
        self.arm_r_f = Line(**kw)
        self.leg_l_u = Line(**kw)
        self.leg_l_f = Line(**kw)
        self.leg_r_u = Line(**kw)
        self.leg_r_f = Line(**kw)
        self.face = VGroup()

        self.add(
            self.leg_l_u, self.leg_l_f,  # legs first: drawn behind the torso
            self.leg_r_u, self.leg_r_f,
            self.torso, self.neck,
            self.arm_l_u, self.arm_l_f,
            self.arm_r_u, self.arm_r_f,
            self.head, self.face,
        )
        self.set_pose(self.pose)

    # ------------------------------------------------------------- posing
    def set_pose(self, pose: PoseAngles) -> "Stickman":
        """Move every part to match ``pose``. Returns self (chainable)."""
        self.pose = pose
        j = joint_positions(pose)
        self.torso.put_start_and_end_on(j["hip"], j["shoulder"])
        self.neck.put_start_and_end_on(j["shoulder"], j["neck_top"])
        self.head.move_to(j["head_center"])
        self.arm_l_u.put_start_and_end_on(j["shoulder"], j["elbow_l"])
        self.arm_l_f.put_start_and_end_on(j["elbow_l"], j["hand_l"])
        self.arm_r_u.put_start_and_end_on(j["shoulder"], j["elbow_r"])
        self.arm_r_f.put_start_and_end_on(j["elbow_r"], j["hand_r"])
        self.leg_l_u.put_start_and_end_on(j["hip"], j["knee_l"])
        self.leg_l_f.put_start_and_end_on(j["knee_l"], j["foot_l"])
        self.leg_r_u.put_start_and_end_on(j["hip"], j["knee_r"])
        self.leg_r_f.put_start_and_end_on(j["knee_r"], j["foot_r"])
        face = build_face(pose.expression, SPEC["HEAD_R"])
        face.rotate(j["head_angle"], about_point=np.array([0.0, 0.0, 0.0]))
        face.move_to(j["head_center"])
        self.face.become(face)
        return self

    def walk(self, phase: float) -> "Stickman":
        """Set the walk-cycle pose for ``phase`` (radians)."""
        return self.set_pose(walk_pose(phase))

    def wave(self, phase: float) -> "Stickman":
        """Set the waving pose for ``phase`` (radians)."""
        return self.set_pose(wave_pose(phase))

    # ---------------------------------------------------------- placement
    def get_hip_point(self) -> np.ndarray:
        """Current hip position in scene coordinates."""
        return self._hip.copy()

    def place(self, x: float, y: float) -> "Stickman":
        """Move the whole character so the HIP sits at (x, y)."""
        target = np.array([x, y, 0.0])
        self.shift(target - self._hip)
        self._hip = target
        return self

    def height(self) -> float:
        """Total height in Manim units (head top to lowest foot)."""
        j = joint_positions(self.pose)
        top = j["head_center"][1] + SPEC["HEAD_R"]
        bottom = min(j["foot_l"][1], j["foot_r"][1])
        return top - bottom
