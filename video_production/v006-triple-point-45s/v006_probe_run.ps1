$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\v006_probe.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== V006 PROBE: 4 risky MMS words, speaking_rate 0.92 + Whisper check ==="
& $VenvPy "$Root\v006\v006_probe.py"
Write-Host "=== DONE ==="
Stop-Transcript
