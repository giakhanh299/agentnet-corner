$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\v007_probe2.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== V007 PROBE: MMS-TTS risky words at speaking_rate 0.92 + Whisper check ==="
& $VenvPy "$Root\v007_probe2.py"
Write-Host "=== DONE ==="
Stop-Transcript
