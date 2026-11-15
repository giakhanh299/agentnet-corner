$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\v003_probe2.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== V003 PROBE 2: fallbacks (day cap / duong ray / nam dai) ==="
& $VenvPy "$Root\v003\v003_probe2.py"
Write-Host "=== DONE ==="
Stop-Transcript
