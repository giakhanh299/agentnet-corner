$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_fw_run.log" -Force
$APY = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
# cuBLAS fix (v007 lesson): prepend torch\lib + nvidia bins to PATH
$torchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$nvidiaBins = Get-ChildItem "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\nvidia" -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName "bin" } | Where-Object { Test-Path $_ }
$env:PATH = ($torchLib + ";" + ($nvidiaBins -join ";") + ";" + $env:PATH)
Write-Host "PATH prepended torch lib + nvidia bins."
& $APY C:\Users\w\v014_fw_check.py
if ($LASTEXITCODE -ne 0) { Write-Host "FW CHECK FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
Write-Host "V014_FW_RUN_DONE"
Stop-Transcript
