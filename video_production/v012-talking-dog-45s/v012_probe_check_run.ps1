$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v012_probe_check_run.log" -Force | Out-Null
if ($env:HF_HOME) { Write-Output "HF_HOME: $env:HF_HOME" } else {
  $CACHE = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
  if (Test-Path $CACHE) { $env:HF_HOME = $CACHE; Write-Output "HF_HOME set to shared cache" }
}
$TORCH_LIB = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TORCH_LIB;" + $env:PATH
Get-ChildItem "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\nvidia\*\bin" -Directory -ErrorAction SilentlyContinue | ForEach-Object { $env:PATH = "$($_.FullName);" + $env:PATH }
& "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe" "C:\Users\w\v012_probe_check.py" 2>&1
Write-Output "V012_PROBE_CHECK_RUN_DONE"
Stop-Transcript | Out-Null
