$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_assemble_run.log" -Force
$APY = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$torchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$nvidiaBins = Get-ChildItem "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\nvidia" -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName "bin" } | Where-Object { Test-Path $_ }
$env:PATH = ($torchLib + ";" + ($nvidiaBins -join ";") + ";" + $env:PATH)
Write-Host "=== Assemble V014 voice (atempo 0.69, b3a = giau take2) ==="
& $APY C:\Users\w\v014_assemble.py
if ($LASTEXITCODE -ne 0) { Write-Host "ASSEMBLE FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
Write-Host "V014_ASSEMBLE_RUN_DONE"
Stop-Transcript
