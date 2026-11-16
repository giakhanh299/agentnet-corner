$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_fw_final_run.log" -Force
$APY = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$torchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$nvidiaBins = Get-ChildItem "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\nvidia" -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName "bin" } | Where-Object { Test-Path $_ }
$env:PATH = ($torchLib + ";" + ($nvidiaBins -join ";") + ";" + $env:PATH)
& $APY C:\Users\w\v014_fw_final.py
if ($LASTEXITCODE -ne 0) { Write-Host "FW FINAL FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
Write-Host "V014_FW_FINAL_RUN_DONE"
Stop-Transcript
