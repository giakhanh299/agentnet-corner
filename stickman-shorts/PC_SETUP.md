# Stickman repo — Windows PC setup (verified 2026-11-15 ~17:01 +07)

PC: DESKTOP-01O3HNF, Windows 11 Pro, 32 GB RAM, user `w`, Tailscale 100.101.158.71.
Access: SSH key `~/.ssh/pc_torque` on VPS 1 via tunnel proxy port 3130 (see parent docs for the exact command). The SSH session runs with a full admin token (writes to `C:\Windows\Fonts` and HKLM succeeded without a UAC prompt).

## Result: WORKS. Demo renders on the PC in 4.6s.

- Repo: `C:\Users\w\agentnet-corner` (cloned 2026-11-15, HEAD `58b70a2`).
- Python: **3.12.10** at `C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe` (already installed; bare `python` on PATH is 3.10.11 — do NOT use it). `py -3.12` also works.
- ffmpeg **8.1.2** (Gyan build) and git **2.54.0** already present — nothing installed for these.
- venv: `stickman-shorts\.venv-win` (Python 3.12.10), pip 26.3, **manim 0.22.1** (`import manim` prints 0.22.1).
- Font: Be Vietnam Pro installed to `C:\Windows\Fonts` + per-user Fonts dir + HKCU entries. **manimpango saw it only after HKLM registry entries were added** (`HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts`); `manimpango.list_fonts()` then reported 388 fonts incl. `Be Vietnam Pro`. If the font disappears from Manim, re-add the HKLM entries first.
- Render: `python -m manim render -qm --format=mp4 stickman_demo.py StickmanScene` → exit 0, **4.58 s wall** (VPS: 17.2 s cold / 8.6 s warm). Output `media\videos\stickman_demo\1920p30\StickmanScene.mp4`, **263,107 bytes, h264, 1080x1920, 30 fps, 5.000 s** (ffprobe-verified).
- Frames viewed (copies in `test_frames/pc/` on VPS 1): 1 s mid-stride walk with counter-swinging arms, correct proportions; 4 s title card `TÂM SỰ NGƯỜI QUE` with all diacritics correct, stickman smiling and waving. Pixel-identical in content to the VPS render.

## How to run on the PC (reliable pattern — read before retrying anything)

- **Use .ps1 script files** (scp'd to `C:\Users\w\*.ps1`), run in the **foreground** over SSH as `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\w\<script>.ps1 < NUL`, with `Start-Transcript` logging to `C:\Users\w\<name>.log`. Helper scripts are in this repo: `setup_stickman_pc.ps1`, `pip_install_pc.ps1`, `font_install_pc.ps1`, `font_fix_pc.ps1`, `render_demo_pc.ps1`.
- **Do NOT** pass long commands via `powershell -Command "..."` with nested quoting — that hung once for 62 min (see below). **Do NOT** launch long work detached with `Start-Process` — it died silently once (see below).
- `render.bat` was NOT used; the direct `python -m manim render` command above is the tested path.

## Incidents during setup (all resolved except the noted orphan)

1. Nested `-Command` quoting: first clone attempt failed (trailing backslash ate the closing quote); first venv attempt had backslashes stripped (`C:Usersw...`). Fixed by switching to .ps1 files.
2. First venv+pip attempt hung **62 min** (ssh exit 255, zero output). Left an idle bare `python.exe` (PID 4368) + its parent `powershell.exe` (PID 38548), both started 15:49:19, ~0 CPU, no window. Ownership is ambiguous (may be my hung session's leftover, or the user's own REPL) — **left running, untouched**. It consumes nothing and blocks nothing.
3. Detached `Start-Process` setup script died silently right after creating the venv (empty log, no manim). Cause undiagnosed. Workaround: foreground run with `< NUL` stdin + transcript — pip install then completed in 68 s.
4. Render script called `ffmpeg` with ffprobe options by mistake (`Unrecognized option 'select_streams'`). Re-ran with `ffprobe` — specs confirmed.
5. Font initially invisible to manimpango (`list_fonts()` returned `[]` for Be Vietnam) despite files + HKCU entries. Fixed with HKLM registry entries (see above).

## Notes

- The user has their own Python ecosystem on this PC (Python 3.10, 3.14, `D:\02_CONG_CU\youtube-reup-pipeline\venv`, many python processes from 08:0x) — **do not touch it**. The stickman venv is isolated (`.venv-win`).
- Logs on the PC: `C:\Users\w\pip_install.log`, `font_install.log`, `font_fix.log`, `render_demo.log`, `setup_stickman.log` (empty — see incident 3).
- Next: `render_all.sh` / `assemble.py --srt` still untested on the PC; no real episode rendered there yet.
