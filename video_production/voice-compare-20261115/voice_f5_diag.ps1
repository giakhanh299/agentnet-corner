$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Start-Transcript -Path "C:\Users\w\voice_f5_diag.log" -Append
$VenvAI = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$VC = "C:\Users\w\agentnet-corner\ai-stack\voice_compare"

Write-Output "=== F5 synth log: model/checkpoint lines ==="
Select-String -Path "C:\Users\w\voice_f5_synth.log" -Pattern "model|checkpoint|F5TTS|Loading|cache" | ForEach-Object { $_.Line.Trim() } | Select-Object -First 30

Write-Output "=== HF cache: F5 model dirs ==="
Write-Output "HF_HOME=$env:HF_HOME"
Get-ChildItem "$env:HF_HOME\hub" -Directory -Filter "*F5*" | ForEach-Object { $_.FullName }
Get-ChildItem "$env:HF_HOME\hub" -Directory -Filter "*f5*" | ForEach-Object { $_.FullName }

Write-Output "=== Whisper: per-sentence F5 wavs ==="
& $VenvAI C:\Users\w\agentnet-corner\ai-stack\voice_whisper_check.py "$VC\f5_s1.wav" "$VC\f5_s2.wav" "$VC\f5_s3.wav" "$VC\f5tts_slow_s1.wav" "$VC\f5tts_slow_s2.wav" "$VC\f5tts_slow_s3.wav"

Stop-Transcript
Write-Output "F5_DIAG_DONE"
