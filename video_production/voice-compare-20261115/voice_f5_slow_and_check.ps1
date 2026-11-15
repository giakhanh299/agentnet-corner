$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
# torchcodec needs FFmpeg 8.1 shared DLLs on PATH (see voice_ffmpeg_shared.ps1)
$env:PATH = "C:\Users\w\agentnet-corner\ai-stack\ffmpeg-shared\ffmpeg-n8.1-latest-win64-gpl-shared-8.1\bin;$env:PATH"
Start-Transcript -Path "C:\Users\w\voice_f5_slow_and_check.log" -Append
$VenvF5 = "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\python.exe"
$VenvAI = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$VC = "C:\Users\w\agentnet-corner\ai-stack\voice_compare"

Write-Output "=== F5 slow variant (speed 0.75) ==="
$env:F5_SPEED = "0.75"
$env:F5_OUTNAME = "f5tts_slow.wav"
& $VenvF5 C:\Users\w\agentnet-corner\ai-stack\voice_f5_synth.py

Write-Output "=== Whisper check: mms_varied, f5tts, f5tts_slow ==="
& $VenvAI C:\Users\w\agentnet-corner\ai-stack\voice_whisper_check.py "$VC\mms_varied.wav" "$VC\f5tts.wav" "$VC\f5tts_slow.wav"

Stop-Transcript
Write-Output "F5_SLOW_AND_CHECK_DONE"
