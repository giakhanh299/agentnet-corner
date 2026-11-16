# v014 QC — "Đừng làm thêm kiểu cũ" (T07 #99, 74 pts)

- File: `v014.mp4` — sha256 `938568d1c31b7fc8e10276bba603f4f8b372760fe403a4bec24dc03bf89b8d65`
- Size: 5,396,303 bytes (5.15 MB)
- Duration: 52.07 s (1562 frames @ 30 fps) — audio 52.10 s
- Video: H.264, 1080x1920, 30 fps, yuv420p, crf 20
- Audio: AAC 192k, 48 kHz, stereo
- Loudness (final muxed file, loudnorm measure): **-16.05 LUFS**, true peak **-3.09 dBTP**, LRA 2.30 — on target (~-16 LUFS, TP ≤ -1 dBTP)
- Voice: VieNeu-TTS v3 Turbo, preset **"Mai Anh"** (female), synthesized **on the PC** (C:\Users\w\agentnet-corner\ai-stack\.venv-vieneu), native 224 wpm, slowed with ffmpeg atempo **0.66** → **156.4 wpm speech-only** (0.65 gave 146 wpm, below the 150–165 zone). 129 words, voice.wav 52.09 s, voice onset 0.000 s. Pauses 0.3 s after hook / 0.4 s micro / 0.6 s before payoff, per the production brief.
- Whisper check (faster-whisper large-v3, on the PC, on the slowed voice): **111/129 = 86.0%** (≥75% target passed). "Không hứa bạn giàu nhanh" heard correctly. Remaining misses are number-word normalisation (bốn/mười/trăm/hai/ba/bảy → digits) + one "bạn"→"đã" artifact.
- Probes: all risky words PASS with VieNeu — "trí tuệ nhân tạo", "video", "bốn mươi lăm giây", "mười hai giây", "kịch bản" all heard. **"giàu" needed a fix**: take 1 heard "sầu nhanh"; take 2 heard "giàu" correctly → b3a uses the passing take-2 audio (`v014_giau_take2_48k.wav`). No other probe swaps.
- Captions: 36 events, 129 words (SRT + ASS, Be Vietnam Pro Bold, PlayRes 1080x1920, MarginV 300). Sidecar files, not muxed (v011 convention).
- Mix: voice + bgm_upbeat (vol 0.12, fade out last 2 s) + whoosh @ 6.20 s + dings @ 17.70 / 22.30 / 23.90 / 27.60 s + pop @ 43.48 s; amix duration=longest; loudnorm 2-pass (measured I -20.00, TP -4.51, LRA 2.40, dynamic) + alimiter limit=0.7 level=false.
- SFX audibility (sample-level RMS, mix vs voice-only, same windows): ding1 +3.6 dB, ding2 +1.4 dB, ding3 +39.8 dB (rings alone in a micro-pause), ding4 +1.7 dB, whoosh +0.6 dB, pop +0.9 dB — all 6 present. BGM audible in the 0.6 s pre-payoff gap (mix -32.6 dB vs voice silent).
- Segments (9, hard cuts, concat): hook 0.00–6.20 (186f), b1a 6.20–11.27 (152f), b1b 11.27–16.74 (164f), step1 16.74–22.15 (162f), step2 22.15–24.65 (75f), step3 24.65–27.45 (84f), step4 27.45–31.49 (121f), b3 31.49–43.48 (359f, calendar card), payoff 43.48–52.09 (259f, payoff card). Total 1562f.
- Screen footage: REAL terminal, not stills. 99 PrintWindow snapshots (2 fps, 1936x1048, 36 px Consolas) of the PC console running the actual pipeline — script, MMS-TTS demo, faster-whisper final check, Manim StickmanScene render, v011 ffmpeg re-render — captured 2026-11-16 21:16:32–21:17:22 by a child process of the interactive console. No focus steal, no browser content, no other person's content. Two earlier fullscreen gdigrab runs captured the user's live Facebook browser by mistake — that footage was deleted from the PC and the VPS (privacy). See "Screen-recording method" below.
- Frames viewed (10): 1 s hook "ĐỪNG LÀM THÊM GIỜ NỮA" + render screen; 8 s "ĐỌC GIỌNG: 0,9 GIÂY" + TTS screen; 13 s "KIỂM GIỌNG: 4,7 GIÂY" + Whisper screen; 19 s "BƯỚC 1 — VIẾT KỊCH BẢN" + script screen; 23 s "BƯỚC 2 — CHO MÁY ĐỌC GIỌNG" + TTS results; 26 s "BƯỚC 3 — VẼ HÌNH BẰNG AI" + Whisper 86.0% + Manim start; 29 s "BƯỚC 4 — DỰNG: 12 GIÂY" + render screen; 37 s calendar card (7 VIDEO / TUẦN, 7 day boxes, no overlap); 48 s + 51.5 s payoff card (zoompan 1.0→1.04 visible). All labels correct in their windows; drawtext expansion=none on every instance (v011 "%" lesson).
- Numbers on screen are the real recorded measurements (kept exactly as written in the script): MMS-TTS on PC 55 words / 19.6 s audio in 0.9 s; faster-whisper large-v3 48.8 s audio in 4.7 s; v003 PC render 12 s for 1504 frames. No income promises; "Không hứa bạn giàu nhanh" kept at beat 3.
- Render + mix + encode entirely on the PC (user order 2026-11-15 21:53). No VPS render fallback. NOT posted/uploaded anywhere.

## Screen-recording method (for the next video)

- gdigrab fullscreen from the interactive session captured the user's live browser (the console never came to the front; the user was actively posting on Facebook). Do NOT re-run a fullscreen capture while the user is active.
- `ffmpeg -f gdigrab -i title=...` from SSH fails with "I/O error" — SSH runs in a different window station and cannot see interactive windows by title.
- PrintWindow works: it renders a window's true content even when another window covers it. But a separate schtasks /IT task cannot FindWindow another task's console (window-station isolation between tasks) — the snapshotter saw 0 windows. The working pattern: spawn the snapshotter as a CHILD process of the screen console itself (Start-Process, hidden window), passing the console hwnd as a plain string argument (IntPtr does not survive Start-Job serialisation). The child then PrintWindow-snapshots the parent every 0.5 s. Proven: 99/99 shots, 1936x1048, ok=True.
- Scripts: `v014_snap_child.ps1` (child snapshotter), `v014_screen4.ps1` (steps + spawns the child). Earlier dead ends kept for reference: `v014_screen.ps1` (gdigrab), `v014_screen2.ps1` (Start-Job snapshotter, 0 shots), `v014_snap.ps1` (separate-task FindWindow snapshotter, 0 shots), `v014_title_test.ps1`, `v014_pw_test.ps1` (PrintWindow proof).

## Honest limits

- No human listened to the video — Whisper % only (86.0% on the slowed voice).
- Screen footage is 2 fps snapshots (0.5 s per frame), so terminal motion is steppy, not smooth video. Content is 100% real (true screenshots of the actual terminal), but it reads as a timelapse of the terminal, not a live recording.
- The script text on screen is mojibake (the console displayed the UTF-8 script as cp1252) — Vietnamese diacritics garbled in the Get-Content output. The key numbers are still legible ("55 từ / 19,6s audio trong 0,9 giây", "48,8s audio trong 4,7 giây", "12 giây cho 1.504 khung hình"). Fix for next time: `chcp 65001` before Get-Content, or print the numbers as ASCII lines.
- Whoosh (+0.6 dB) and pop (+0.9 dB) are subtle under the voice — present but easy to miss. Ding3 is the clearest SFX (+39.8 dB in a pause).
- Bottom ~780 px of every screen segment is empty black (captions zone; captions are sidecar ASS, not burned in). Without captions enabled the lower half is blank.
- The hook and step-4 segments both show the render step; b1a and step-2 both show the TTS step (different shot ranges of the same run).
- Voice onset 0.000 s (leading silence trimmed before captions were built — v010 lesson applied).
- VieNeu "Mai Anh" cannot say "log" (known limit; not needed in this script).
