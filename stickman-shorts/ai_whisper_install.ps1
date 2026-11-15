$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\ai_whisper_install.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
Write-Host "=== Install faster-whisper ==="
& $VenvPy -m pip install faster-whisper
Write-Host "=== faster-whisper version ==="
& $VenvPy -c "import faster_whisper; print('faster-whisper', faster_whisper.__version__)"
Write-Host "=== Transcribe Ep001 voice.wav with large-v3 (first run downloads ~3GB model) ==="
& $VenvPy "$Root\ai_whisper_test.py" large-v3
Write-Host "=== DONE ==="
Stop-Transcript
