$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Start-Transcript -Path "C:\Users\w\voice_torchcodec_fix.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\python.exe"
$VenvPip = "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\pip.exe"
$TestWav = "C:\Users\w\agentnet-corner\ai-stack\voice_compare\mms_varied.wav"

Write-Output "=== 1. torchaudio.load WITH torchcodec installed ==="
& $VenvPy -c "import torchaudio; w,sr=torchaudio.load(r'$TestWav'); print('LOAD_OK', tuple(w.shape), sr)"
if ($LASTEXITCODE -ne 0) { Write-Output "LOAD_FAILED_WITH_TORCHCODEC (expected)" }

Write-Output "=== 2. uninstall torchcodec ==="
& $VenvPip uninstall -y torchcodec

Write-Output "=== 3. torchaudio.load WITHOUT torchcodec (soundfile fallback?) ==="
& $VenvPy -c "import torchaudio; w,sr=torchaudio.load(r'$TestWav'); print('LOAD_OK', tuple(w.shape), sr); torchaudio.save(r'C:\Users\w\agentnet-corner\ai-stack\voice_compare\tc_test.wav', w, sr); print('SAVE_OK')"
if ($LASTEXITCODE -ne 0) { Write-Output "LOAD_FAILED_WITHOUT_TORCHCODEC too" }

Stop-Transcript
Write-Output "TORCHCODEC_FIX_DONE"
