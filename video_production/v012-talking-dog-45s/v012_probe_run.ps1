$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v012_probe_run.log" -Force | Out-Null
if ($env:HF_HOME) { Write-Output "HF_HOME: $env:HF_HOME" } else {
  $CACHE = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
  if (Test-Path $CACHE) { $env:HF_HOME = $CACHE; Write-Output "HF_HOME set to shared cache" }
}
& "C:\Users\w\agentnet-corner\ai-stack\.venv-vieneu\Scripts\python.exe" "C:\Users\w\v012_probe.py" 2>&1
Write-Output "V012_PROBE_RUN_DONE"
Stop-Transcript | Out-Null
