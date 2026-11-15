$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\ai_whisper_fix.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
if (Test-Path "$Root\voice.wav") {
  Write-Host "=== Renaming voice.wav -> ep001_voice.wav ==="
  Move-Item "$Root\voice.wav" "$Root\ep001_voice.wav" -Force
}
Write-Host "=== Downgrade av to 14.4.0 (faster-whisper 1.2.1 incompatible with av 19) ==="
& $VenvPy -m pip install "av==14.4.0"
& $VenvPy -c "import av; print('av', av.__version__)"
Write-Host "=== Transcribe Ep001 voice.wav with large-v3 ==="
& $VenvPy "$Root\ai_whisper_test.py" large-v3
Write-Host "=== DONE ==="
Stop-Transcript
