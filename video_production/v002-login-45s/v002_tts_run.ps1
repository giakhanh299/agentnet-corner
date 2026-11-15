$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\v002_tts.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== V002 TTS: MMS-TTS 5 sentences + faster-whisper large-v3 check ==="
& $VenvPy "$Root\v002_tts.py"
Write-Host "=== DONE ==="
Stop-Transcript
