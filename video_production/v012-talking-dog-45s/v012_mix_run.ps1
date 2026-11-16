$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v012_mix_run.log" -Force | Out-Null
if (-not (Test-Path "C:\Users\w\v012_render")) { New-Item -ItemType Directory -Path "C:\Users\w\v012_render" | Out-Null }
& "C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe" "C:\Users\w\v012_mix.py" 2>&1
Write-Output "V012_MIX_RUN_DONE"
Stop-Transcript | Out-Null
