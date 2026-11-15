"""Rig smoke test — no rendering, just geometry + text rules.

Run from the repo root:  python tests/test_rig.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from config import SPEC
from src.rig.character import Stickman, joint_positions
from src.rig.poses import POSE_NEUTRAL, lerp_pose
from src.rig.walk import walk_bob, walk_pose
from src.utils.text import VIETNAMESE_TEST, normalize_text, split_text

failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not cond:
        failures.append(name)


# 1. SPEC is frozen: nobody can mutate the character mid-project.
try:
    SPEC["HEAD_R"] = 1.0
    check("SPEC frozen", False, "assignment did not raise")
except TypeError:
    check("SPEC frozen", True)

# 2. Proportions derive from HEAD_R; total height is fixed by the spec.
s = Stickman()
h = s.height()
expected = 2 * SPEC["HEAD_R"] + SPEC["NECK"] + SPEC["TORSO"] \
    + SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]
check("height derives from SPEC", abs(h - expected) < 1e-6, f"height={h:.3f}")

# 3. set_pose really moves the joints (no pass bodies).
j0 = joint_positions(POSE_NEUTRAL)
j1 = joint_positions(walk_pose(1.0))
moved = not np.allclose(j0["foot_l"], j1["foot_l"])
check("walk pose moves the feet", moved)

# 4. walk bob is positive and bounded.
bobs = [walk_bob(p) for p in np.linspace(0, 6.28, 25)]
check("walk bob in [0, 0.12]", 0.0 <= min(bobs) and max(bobs) <= 0.1201,
      f"min={min(bobs):.3f} max={max(bobs):.3f}")

# 5. place() puts the HIP at the requested point.
s.place(1.5, -1.5)
check("place() sets hip", np.allclose(s.get_hip_point(), [1.5, -1.5, 0.0]))

# 6. walk()/wave() return self and change the pose.
s2 = Stickman()
before = s2.pose
s2.walk(0.7)
check("walk() changes pose", s2.pose != before)
s2.wave(1.0)
check("wave() raises right arm", s2.pose.shoulder_r > 2.0,
      f"shoulder_r={s2.pose.shoulder_r:.2f} rad")

# 7. lerp_pose midpoint is the average of the two poses.
a, b = POSE_NEUTRAL, walk_pose(1.0)
mid = lerp_pose(a, b, 0.5)
check("lerp_pose midpoint", abs(mid.hip_l - (a.hip_l + b.hip_l) / 2) < 1e-9)

# 8. Vietnamese text: NFC normalize + line split.
# Build a true NFD string the honest way (unicodedata), not by hand:
# e.g. "ự" is u + horn (U+031B) + dot below, NOT u + circumflex.
import unicodedata

nfd = unicodedata.normalize("NFD", "Tâm sự người que")
check("NFC normalize", normalize_text(nfd) == "Tâm sự người que")
check("NFD input really differs", nfd != "Tâm sự người que")
lines = split_text(VIETNAMESE_TEST, max_chars=30)
check("split_text wraps", all(len(line) <= 30 for line in lines)
      and len(lines) >= 2, f"{len(lines)} lines")

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("ALL RIG TESTS PASSED")
