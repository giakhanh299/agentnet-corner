$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_tts_run.log" -Force
$env:HF_HOME = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
$VPY = "C:\Users\w\agentnet-corner\ai-stack\.venv-vieneu\Scripts\python.exe"
$APY = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
Write-Host "=== Step 1: VieNeu TTS units (Mai Anh) ==="
& $VPY C:\Users\w\v014_tts.py
if ($LASTEXITCODE -ne 0) { Write-Host "TTS FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
Write-Host "=== Step 2: faster-whisper large-v3 check ==="
& $APY C:\Users\w\v014_fw_check.py
if ($LASTEXITCODE -ne 0) { Write-Host "FW CHECK FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
Write-Host "V014_TTS_RUN_DONE"
Stop-Transcript
