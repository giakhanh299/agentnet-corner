"""Base scene: 9:16 config + helpers shared by every video scene.

Importing this module applies the 9:16 config (module level, so it runs
before Manim builds the camera).
"""

from __future__ import annotations

from manim import Scene

from config import GROUND_Y, SPEC
from src.rig.character import Stickman
from src.rig.poses import PoseAngles
from src.rig.props import ground_line
from src.utils.export import apply_video_config

apply_video_config()


class StickmanScene(Scene):
    """Scene with the 9:16 config applied and a ground line ready."""

    def hip_rest_y(self) -> float:
        """Hip height when standing with feet on the ground line."""
        return GROUND_Y + SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]

    def ground(self):
        """The ground line the stickman stands on."""
        return ground_line(GROUND_Y)

    def stickman_at(self, x: float = 0.0, pose: PoseAngles | None = None) -> Stickman:
        """A Stickman with its hip at (x, hip_rest_y)."""
        stick = Stickman(pose=pose)
        stick.place(x, self.hip_rest_y())
        return stick
