$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Start-Transcript -Path "C:\Users\w\voice_torchcodec_fix2.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\python.exe"
$VenvPip = "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\pip.exe"
$TestWav = "C:\Users\w\agentnet-corner\ai-stack\voice_compare\mms_varied.wav"

Write-Output "=== 1. reinstall/upgrade torchcodec ==="
& $VenvPip install --upgrade torchcodec

Write-Output "=== 2. torchaudio.load test ==="
& $VenvPy -c "import torchaudio; w,sr=torchaudio.load(r'$TestWav'); print('LOAD_OK', tuple(w.shape), sr); torchaudio.save(r'C:\Users\w\agentnet-corner\ai-stack\voice_compare\tc_test.wav', w, sr); print('SAVE_OK')"
if ($LASTEXITCODE -eq 0) { Write-Output "TORCHCODEC_WORKS" } else { Write-Output "TORCHCODEC_STILL_BROKEN" }

Stop-Transcript
Write-Output "TORCHCODEC_FIX2_DONE"
