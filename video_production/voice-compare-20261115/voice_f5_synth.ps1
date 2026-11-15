$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
# torchcodec needs FFmpeg 8.1 shared DLLs on PATH (see voice_ffmpeg_shared.ps1)
$env:PATH = "C:\Users\w\agentnet-corner\ai-stack\ffmpeg-shared\ffmpeg-n8.1-latest-win64-gpl-shared-8.1\bin;$env:PATH"
Start-Transcript -Path "C:\Users\w\voice_f5_synth.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\python.exe"
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\voice_f5_synth.py
Stop-Transcript
Write-Output "F5_SYNTH_DONE"
