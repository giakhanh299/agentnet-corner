#!/usr/bin/env bash
# Render one scene:  tools/render.sh stickman_demo.py StickmanScene
# Uses the repo venv (.venv) if present, else the system `manim`.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -x ".venv/bin/manim" ]; then
    MANIM=".venv/bin/manim"
else
    MANIM="manim"
fi

exec "$MANIM" render -qm --format=mp4 "$@"
