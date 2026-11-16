$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_probe_giau_run.log" -Force
$env:HF_HOME = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
$VPY = "C:\Users\w\agentnet-corner\ai-stack\.venv-vieneu\Scripts\python.exe"
$APY = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
& $VPY C:\Users\w\v014_probe_giau.py
if ($LASTEXITCODE -ne 0) { Write-Host "PROBE SYNTH FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
$torchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$nvidiaBins = Get-ChildItem "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\nvidia" -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName "bin" } | Where-Object { Test-Path $_ }
$env:PATH = ($torchLib + ";" + ($nvidiaBins -join ";") + ";" + $env:PATH)
& $APY C:\Users\w\v014_probe_giau_check.py
if ($LASTEXITCODE -ne 0) { Write-Host "PROBE CHECK FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
Write-Host "V014_PROBE_GIAU_RUN_DONE"
Stop-Transcript
