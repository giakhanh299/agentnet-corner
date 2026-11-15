$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\v002_probe2.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== V002 probe round 2: beat-1 verb, counting verb, hai ly ==="
& $VenvPy "$Root\v002_probe2.py"
Write-Host "=== DONE ==="
Stop-Transcript
