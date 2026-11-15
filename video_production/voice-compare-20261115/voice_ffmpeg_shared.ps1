$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Start-Transcript -Path "C:\Users\w\voice_ffmpeg_shared.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\python.exe"
$Base = "C:\Users\w\agentnet-corner\ai-stack"
$Zip = "$Base\ffmpeg-shared.zip"
$Dir = "$Base\ffmpeg-shared"
$Url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n8.1-latest-win64-gpl-shared-8.1.zip"

if (-not (Test-Path "$Dir\bin\avcodec-62.dll")) {
    Write-Output "=== downloading FFmpeg 8.0 shared build ==="
    curl.exe -L --fail -o $Zip $Url
    Write-Output "downloaded: $((Get-Item $Zip).Length) bytes"
    Write-Output "=== extracting ==="
    Expand-Archive -Path $Zip -DestinationPath $Dir -Force
} else {
    Write-Output "FFmpeg shared build already present, skipping download"
}
Get-ChildItem "$Dir\*\bin\av*.dll" | ForEach-Object { $_.Name }
$BinDir = (Get-ChildItem "$Dir\*\bin" | Select-Object -First 1).FullName
Write-Output "BIN_DIR=$BinDir"
$env:PATH = "$BinDir;$env:PATH"

Write-Output "=== torchaudio.load test with FFmpeg DLLs on PATH ==="
& $VenvPy -c "import torchaudio; w,sr=torchaudio.load(r'C:\Users\w\agentnet-corner\ai-stack\voice_compare\mms_varied.wav'); print('LOAD_OK', tuple(w.shape), sr); torchaudio.save(r'C:\Users\w\agentnet-corner\ai-stack\voice_compare\tc_test.wav', w, sr); print('SAVE_OK')"
if ($LASTEXITCODE -eq 0) { Write-Output "TORCHCODEC_WORKS" } else { Write-Output "TORCHCODEC_STILL_BROKEN" }

Stop-Transcript
Write-Output "FFMPEG_SHARED_DONE"
