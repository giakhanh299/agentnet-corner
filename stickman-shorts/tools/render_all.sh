#!/usr/bin/env bash
# Render every video in videos/<date>_<slug>/scene.py, one at a time.
# Usage: tools/render_all.sh
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -x ".venv/bin/manim" ]; then
    MANIM=".venv/bin/manim"
else
    MANIM="manim"
fi

for scene in videos/*/scene.py; do
    [ -f "$scene" ] || continue
    echo "=== rendering $scene"
    "$MANIM" render -qm --format=mp4 "$scene" StickmanScene
done
echo "=== all done"
