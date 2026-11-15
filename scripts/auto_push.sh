#!/bin/bash
# Auto-push AgentNet repo every 30 min (cron agentnet-git-autopush-30min).
# Only safe text paths are added. NEVER media, tokens, credentials or logs.
# Usage: ~/workspace/agentnet-corner/auto_push.sh
set -u
REPO="$HOME/workspace/agentnet-corner-github"
cd "$REPO" || exit 1
git add video-pipeline docs HANDOFF.md README.md .gitignore stickman-shorts STATUS.md scripts/auto_push.sh 2>/dev/null || true
if git diff --cached --quiet; then
  echo "nothing to push"
  exit 0
fi
git -c user.name="Torque" -c user.email="torque@agentnet.local" \
  commit -m "Auto-save: $(date '+%Y-%m-%d %H:%M %Z')" >/dev/null 2>&1
git push origin main 2>&1 | tail -3
