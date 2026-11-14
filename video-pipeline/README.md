# Video pipeline (AgentNet research, V1.0 mission)

Tools the Controller-as-Engineer uses to prepare short videos for deep
analysis. Research workers (web/browser only) cannot run these; the Engineer
runs them on the controller VPS and shares the outputs.

## What it does

- `download_candidates.py` — downloads the 100 verified candidate videos
  (73 YouTube Shorts, 27 TikTok) from `verify_research_payload_20261114.txt`.
  Priority: the 6 directly verified TikTok pages first, then
  humor/surprise/curiosity Shorts. Skips files already downloaded and logs
  one JSON line per video to `video_downloads/download_log.jsonl`.
- `analyze_video.py` — for one video file: ffprobe (duration, size,
  resolution, codec), scene-change keyframes, keyframe images, 30s mono
  16kHz audio, and a `timeline.md` + `summary.json` report.

## Requirements

- Python 3.12, system ffmpeg/ffprobe 8.x.
- `yt-dlp` in a venv (`python3 -m venv venv && venv/bin/pip install yt-dlp`).
  System pip is blocked by PEP 668; use the venv.

## Download notes (verified 2026-11-15)

- YouTube's default yt-dlp client is bot-blocked
  ("Sign in to confirm you're not a bot"). The android player client
  (`--extractor-args youtube:player_client=android`) bypasses it.
- TikTok downloads work with plain yt-dlp (slow start, retries, completes).
- Test downloads verified as real vertical video:
  TikTok Avrecap 11.0 MB, HEVC 576x1024, 210.8s;
  YouTube Short 12.7 MB, h264 360x640, 179.2s.

## Limits

- No ASR/OCR/OpenCV in this pipeline: no transcript. The lightest transcript
  option is faster-whisper CPU (tiny model). Full openai-whisper + torch is
  not recommended on a low-RAM box.
- First-3s hook is judged from frames at 0/1/2s.
- Downloaded media is NOT committed to git; only code and docs live here.
