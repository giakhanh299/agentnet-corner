$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\v008_render.log" -Append
# Sync stickman source from the VPS tarball (excludes .venv/media/pycache,
# so the PC venv-win and old renders survive the extract).
tar -xzf C:\Users\w\v008_stickman.tar.gz -C C:\Users\w\agentnet-corner
Set-Location C:\Users\w\agentnet-corner\stickman-shorts
$VenvPy = "C:\Users\w\agentnet-corner\stickman-shorts\.venv-win\Scripts\python.exe"
$env:PYTHONIOENCODING = "utf-8"
& $VenvPy -m manim render -qm --format=mp4 videos/2026-11-16_v008-con-gai-cua-bo/scene.py StickmanScene
Copy-Item media\videos\scene\1920p30\StickmanScene.mp4 C:\Users\w\v008_raw.mp4 -Force
Stop-Transcript
Write-Output "V008_RENDER_DONE"
