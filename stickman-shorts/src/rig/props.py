"""Props: minimal objects drawn in the SAME stroke as the stickman.

Every prop uses SPEC["STROKE"] and SPEC["INK"] so props and character
always look like they belong to the same drawing. Props are plain VGroups
centred on (0, 0, 0); the scene positions them.
"""

from __future__ import annotations

from manim import Circle, Line, Rectangle, VGroup

from config import SPEC

INK = SPEC["INK"]
ACCENT = SPEC["ACCENT"]
STROKE = SPEC["STROKE"]
THIN = SPEC["STROKE_THIN"]


def ground_line(y: float = -3.6, x_min: float = -4.2, x_max: float = 4.2) -> Line:
    """The single horizontal line the stickman stands on."""
    return Line(
        [x_min, y, 0], [x_max, y, 0],
        color=INK, stroke_width=THIN,
    )


def money_bag(scale: float = 1.0) -> VGroup:
    """A sack of coins: round body + tied neck + $ mark (as a line cross)."""
    body = Circle(radius=0.55 * scale, color=INK, stroke_width=STROKE)
    body.set_fill(opacity=0)
    knot = Line(
        [-0.18 * scale, 0.55 * scale, 0],
        [0.18 * scale, 0.55 * scale, 0],
        color=INK, stroke_width=THIN,
    )
    tie_l = Line(
        [-0.18 * scale, 0.55 * scale, 0],
        [-0.05 * scale, 0.85 * scale, 0],
        color=INK, stroke_width=THIN,
    )
    tie_r = Line(
        [0.18 * scale, 0.55 * scale, 0],
        [0.05 * scale, 0.85 * scale, 0],
        color=INK, stroke_width=THIN,
    )
    coin = Circle(radius=0.22 * scale, color=ACCENT, stroke_width=THIN)
    coin.set_fill(opacity=0)
    return VGroup(body, knot, tie_l, tie_r, coin)


def laptop(scale: float = 1.0) -> VGroup:
    """A laptop seen from the side: screen + base line."""
    screen = Rectangle(
        width=1.1 * scale, height=0.75 * scale,
        color=INK, stroke_width=STROKE,
    )
    screen.set_fill(opacity=0)
    base = Line(
        [-0.75 * scale, -0.375 * scale, 0],
        [0.75 * scale, -0.375 * scale, 0],
        color=INK, stroke_width=STROKE,
    )
    return VGroup(screen, base)


def clock_wall(scale: float = 1.0) -> VGroup:
    """A wall clock: circle + two hands (10:10)."""
    face = Circle(radius=0.5 * scale, color=INK, stroke_width=STROKE)
    face.set_fill(opacity=0)
    hand_h = Line([0, 0, 0], [-0.18 * scale, 0.22 * scale, 0],
                  color=INK, stroke_width=THIN)
    hand_m = Line([0, 0, 0], [0.22 * scale, 0.18 * scale, 0],
                  color=INK, stroke_width=THIN)
    return VGroup(face, hand_h, hand_m)


def coin_stack(scale: float = 1.0) -> VGroup:
    """Three stacked coins (ellipses as flat circles)."""
    coins = VGroup()
    for i, dx in enumerate((-0.3, 0.0, 0.3)):
        c = Circle(radius=0.22 * scale, color=INK, stroke_width=THIN)
        c.set_fill(opacity=0)
        c.move_to([dx * scale, i * 0.10 * scale, 0])
        coins.add(c)
    return coins
