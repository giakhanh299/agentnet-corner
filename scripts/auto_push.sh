#!/bin/bash
# Auto-push AgentNet repo every 30 min (cron agentnet-git-autopush-30min).
# Only safe text paths are added. NEVER media, tokens, credentials or logs.
# Usage: ~/workspace/agentnet-corner/auto_push.sh
set -u
REPO="$HOME/workspace/agentnet-corner-github"
cd "$REPO" || exit 1
# Sync subagent work from the work dir into the repo copy (subagents write
# to ~/workspace/agentnet-corner/, the git repo is a separate copy — without
# this step their files never reach git). Only safe text paths; media,
# tokens, credentials, venvs and render outputs are never copied.
# No --delete: a missing work dir must never wipe the repo copy.
WORK="$HOME/workspace/agentnet-corner"
if [ -d "$WORK/stickman-shorts" ]; then
  rsync -a --exclude=.venv --exclude=media --exclude=__pycache__ \
    --exclude=test_frames --exclude='videos/*/output' --exclude='*.mp4' \
    --exclude='*.wav' --exclude='*.srt' --exclude='*.ass' --exclude='*.png' \
    --exclude='*.jpg' --exclude='*.pyc' \
    "$WORK/stickman-shorts/" "$REPO/stickman-shorts/" 2>/dev/null || true
fi
# Same for video_production (scripts/QC/captions only — media stays out).
if [ -d "$WORK/video_production" ]; then
  rsync -a --exclude='*.mp4' --exclude='*.wav' --exclude='*.jpg' \
    --exclude='*.png' --exclude='*.part' --exclude='*.m4a' \
    "$WORK/video_production/" "$REPO/video_production/" 2>/dev/null || true
fi
git add video-pipeline video_production docs HANDOFF.md README.md .gitignore stickman-shorts STATUS.md scripts/auto_push.sh 2>/dev/null || true
if git diff --cached --quiet; then
  echo "nothing to push"
  exit 0
fi
git -c user.name="Torque" -c user.email="torque@agentnet.local" \
  commit -m "Auto-save: $(date '+%Y-%m-%d %H:%M %Z')" >/dev/null 2>&1
git push origin main 2>&1 | tail -3
