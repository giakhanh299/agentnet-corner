@echo off
REM Render one scene on Windows:  tools\render.bat stickman_demo.py StickmanScene
REM Uses the repo venv (.venv) if present, else the system `manim`.
cd /d "%~dp0.."
if exist .venv\Scripts\manim.exe (
  .venv\Scripts\manim.exe render -qm --format=mp4 %*
) else (
  manim render -qm --format=mp4 %*
)
