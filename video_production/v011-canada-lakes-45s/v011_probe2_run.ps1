$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\v011_probe2.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== V011 PROBE2: fallback words bang tuyet khong lo + ho sau ==="
& $VenvPy "$Root\v011\v011_probe2.py"
Write-Host "=== DONE ==="
Stop-Transcript
