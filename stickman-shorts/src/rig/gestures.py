"""Gestures: poses as functions of phase (radians).

Every gesture is a pose generator, not a set of coordinates. ``phase``
advances with time in the scene; the rig turns the pose into geometry.
"""

import math

from .poses import PoseAngles


def wave_pose(phase: float) -> PoseAngles:
    """Standing wave: right arm raised, forearm oscillating.

    One full wave (hand left-right-left) = 2*pi of phase. The upper arm
    points up-OUTWARD (shoulder angle pi - 0.85) so the elbow clears the
    head circle; the forearm swings side to side above head height.
    """
    return PoseAngles(
        torso_lean=0.0,
        head_tilt=-0.08,
        shoulder_l=0.35,
        elbow_l=0.25,
        shoulder_r=math.pi - 0.85,  # upper arm up and out, clear of the head
        elbow_r=0.9 + 0.5 * math.sin(phase),  # forearm oscillates -> real wave
        hip_l=0.12,
        knee_l=0.0,
        hip_r=-0.12,
        knee_r=0.0,
        expression="happy",
    )


def nod_pose(phase: float) -> PoseAngles:
    """Nodding: head tilts down and back up, once per 2*pi of phase."""
    return PoseAngles(
        torso_lean=0.05,
        head_tilt=0.10 + 0.22 * math.sin(phase),
        expression="happy",
    )


def point_pose() -> PoseAngles:
    """Point forward with the right arm, body square to the viewer."""
    return PoseAngles(
        shoulder_r=math.pi / 2 - 0.15,
        elbow_r=0.05,
        shoulder_l=0.15,
        elbow_l=0.4,
        expression="happy",
    )


def shrug_pose() -> PoseAngles:
    """Both shoulders up, palms out (approximated with raised bent arms)."""
    return PoseAngles(
        shoulder_l=0.9,
        elbow_l=1.2,
        shoulder_r=0.9,
        elbow_r=1.2,
        head_tilt=0.12,
        expression="confused",
    )


def think_pose() -> PoseAngles:
    """Right hand to chin, head tilted, looking aside."""
    return PoseAngles(
        torso_lean=0.08,
        head_tilt=0.18,
        shoulder_r=0.9,
        elbow_r=1.9,
        expression="focused",
    )
