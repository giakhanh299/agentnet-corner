"""Walk cycle: pose as a function of phase (radians).

Legs swing in opposite phase, arms counter-swing, knees bend only
backward (heel toward the back). The scene advances ``phase`` over time;
this module never touches coordinates or Manim objects.
"""

import math

from .poses import PoseAngles

# One full step cycle = 2*pi of phase. At 30 fps, PHASE_RATE gives about
# 2 steps per second (a relaxed walk).
PHASE_RATE = 2 * math.pi * 1.0  # radians per second of walking


def walk_pose(phase: float) -> PoseAngles:
    """Pose at a given point of the walk cycle."""
    swing = math.sin(phase)
    counter = math.sin(phase + math.pi)
    return PoseAngles(
        torso_lean=0.10,  # slight forward lean while walking
        head_tilt=math.sin(phase * 2) * 0.05,
        shoulder_l=counter * 0.50,
        elbow_l=0.35 + max(0.0, counter) * 0.25,
        shoulder_r=swing * 0.50,
        elbow_r=0.35 + max(0.0, swing) * 0.25,
        hip_l=swing * 0.55,
        knee_l=-max(0.0, -swing) * 0.75,
        hip_r=counter * 0.55,
        knee_r=-max(0.0, -counter) * 0.75,
        expression="neutral",
    )


def walk_bob(phase: float) -> float:
    """Vertical hip bounce (Manim units) — the body rises on each step."""
    return abs(math.sin(phase)) * 0.12


def walk_phase_for_distance(distance: float, step_length: float = 0.55) -> float:
    """Phase needed to walk ``distance`` Manim units at ``step_length``/step."""
    steps = distance / step_length
    return steps * math.pi  # one step (one leg) = half a cycle
