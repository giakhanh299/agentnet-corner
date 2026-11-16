$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v009_probe.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== V009 PROBE: MMS-TTS risky words at speaking_rate 0.92 + Whisper check ==="
& $VenvPy "$Root\v009_probe.py"
Write-Host "=== DONE ==="
Stop-Transcript
