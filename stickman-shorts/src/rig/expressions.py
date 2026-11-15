"""Faces: the only part of the rig that draws eyes and mouths.

``build_face(expression, head_r)`` returns a VGroup centred on (0, 0, 0)
— the head centre. The rig rotates it by the head angle and moves it onto
the head. Expressions: neutral, happy, sad, surprised, focused, confused.
"""

from __future__ import annotations

import math

from manim import Arc, Dot, Line, VGroup

from config import SPEC

INK = SPEC["INK"]
THIN = SPEC["STROKE_THIN"]


def _eyes(head_r: float) -> tuple[Dot, Dot]:
    eye_r = 0.075 * head_r / 0.6  # dot radius in Manim units
    left = Dot(point=[-0.22 * head_r, 0.12 * head_r, 0], radius=eye_r, color=INK)
    right = Dot(point=[0.22 * head_r, 0.12 * head_r, 0], radius=eye_r, color=INK)
    return left, right


def _mouth(expression: str, head_r: float):
    """Mouth centred on (0, -0.18*head_r, 0)."""
    cy = -0.18 * head_r
    w = 0.20 * head_r
    if expression == "happy":
        # smile: lower arc
        return Arc(
            radius=0.24 * head_r,
            start_angle=math.radians(200),
            angle=math.radians(140),
            arc_center=[0, cy + 0.10 * head_r, 0],
            color=INK,
            stroke_width=THIN,
        )
    if expression == "sad":
        # frown: upper arc
        return Arc(
            radius=0.24 * head_r,
            start_angle=math.radians(20),
            angle=math.radians(140),
            arc_center=[0, cy - 0.10 * head_r, 0],
            color=INK,
            stroke_width=THIN,
        )
    if expression == "surprised":
        return Dot(point=[0, cy, 0], radius=0.09 * head_r, color=INK)
    if expression == "focused":
        return Line(
            [-w, cy + 0.05 * head_r, 0],
            [w, cy - 0.05 * head_r, 0],
            color=INK,
            stroke_width=THIN,
        )
    if expression == "confused":
        return Line(
            [-w, cy - 0.05 * head_r, 0],
            [w, cy + 0.05 * head_r, 0],
            color=INK,
            stroke_width=THIN,
        )
    # neutral: straight line
    return Line(
        [-w, cy, 0],
        [w, cy, 0],
        color=INK,
        stroke_width=THIN,
    )


def build_face(expression: str, head_r: float) -> VGroup:
    """Face centred on the head centre (0, 0, 0)."""
    left, right = _eyes(head_r)
    return VGroup(left, right, _mouth(expression, head_r))


EXPRESSIONS = ("neutral", "happy", "sad", "surprised", "focused", "confused")
