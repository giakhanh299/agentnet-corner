"""Poses: joint angles only. Scenes never touch coordinates.

A pose is a frozen dataclass of joint angles in RADIANS, measured from
each limb's rest direction (arms/legs hang straight down, torso upright).
Positive angle = swing forward, toward +x (the direction the stickman
faces). The rig in character.py converts angles to positions with forward
kinematics; nothing else in the repo is allowed to move a limb.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class PoseAngles:
    """All angles in radians. ``expression`` picks the face (see expressions.py)."""

    torso_lean: float = 0.0
    head_tilt: float = 0.0
    shoulder_l: float = 0.0
    elbow_l: float = 0.35  # slight natural bend
    shoulder_r: float = 0.0
    elbow_r: float = 0.35
    hip_l: float = 0.0
    knee_l: float = 0.0  # negative = knee bends backward (heel toward back)
    hip_r: float = 0.0
    knee_r: float = 0.0
    expression: str = "neutral"


def lerp_pose(a: PoseAngles, b: PoseAngles, t: float) -> PoseAngles:
    """Linear interpolation between two poses (t in [0, 1]).

    The expression flips at the midpoint; everything else interpolates.
    """
    t = min(max(t, 0.0), 1.0)
    fields = {}
    for name in (
        "torso_lean", "head_tilt",
        "shoulder_l", "elbow_l", "shoulder_r", "elbow_r",
        "hip_l", "knee_l", "hip_r", "knee_r",
    ):
        fields[name] = getattr(a, name) + (getattr(b, name) - getattr(a, name)) * t
    fields["expression"] = b.expression if t >= 0.5 else a.expression
    return replace(a, **fields)


# ---------------------------------------------------------------- named poses
POSE_NEUTRAL = PoseAngles()

POSE_HAPPY = PoseAngles(expression="happy")

POSE_SAD = PoseAngles(
    torso_lean=0.12, head_tilt=0.25, expression="sad",
)

POSE_THINK = PoseAngles(
    torso_lean=0.08,
    head_tilt=0.15,
    shoulder_r=0.9, elbow_r=1.9,  # right hand up to chin
    expression="focused",
)

POSE_POINT = PoseAngles(
    shoulder_r=math.pi / 2 - 0.15,  # right arm straight out forward
    elbow_r=0.05,
    expression="happy",
)

POSE_HANDS_HIPS = PoseAngles(
    shoulder_l=0.7, elbow_l=1.9,
    shoulder_r=-0.7, elbow_r=1.9,
    expression="happy",
)

POSE_SURPRISED = PoseAngles(
    shoulder_l=1.4, elbow_l=0.3,
    shoulder_r=1.4, elbow_r=0.3,
    expression="surprised",
)

POSE_SIT = PoseAngles(
    torso_lean=0.15,
    hip_l=1.35, knee_l=-1.5,
    hip_r=1.35, knee_r=-1.5,
)

POSE_WAVE = PoseAngles(
    torso_lean=0.0,
    head_tilt=-0.08,
    shoulder_l=0.35,
    elbow_l=0.25,
    shoulder_r=math.pi - 0.85,  # right arm raised, clear of the head
    elbow_r=0.9,
    hip_l=0.12,
    hip_r=-0.12,
    expression="happy",
)
