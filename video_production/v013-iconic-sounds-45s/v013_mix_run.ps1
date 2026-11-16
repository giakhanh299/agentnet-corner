$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v013_mix.log" -Force
Set-Location "C:\Users\w"
Write-Host "=== V013 MIX: VieNeu voice + bgm_upbeat + 5 samples + SFX ==="
C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe C:\Users\w\v013_mix.py
Write-Host "MIX_EXIT=$LASTEXITCODE"
Write-Host "=== DONE ==="
Stop-Transcript
