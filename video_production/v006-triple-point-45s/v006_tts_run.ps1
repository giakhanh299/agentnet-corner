$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\v006_tts.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== V006 TTS: MMS-TTS 5 beats, speaking_rate 0.92 + Whisper check ==="
& $VenvPy "$Root\v006\v006_tts.py"
Write-Host "=== DONE ==="
Stop-Transcript
