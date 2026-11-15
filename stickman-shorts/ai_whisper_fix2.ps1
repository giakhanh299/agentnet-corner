$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\ai_whisper_fix2.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
Write-Host "=== Try pinning av to a version with metadata_errors + cp312 wheel ==="
$avOk = $false
foreach ($ver in @("14.0.0","13.1.0","12.3.0")) {
  Write-Host "Trying av==$ver ..."
  $out = & $VenvPy -m pip install "av==$ver" 2>&1
  $out | Select-Object -Last 2
  if ($LASTEXITCODE -eq 0) { $avOk = $true; Write-Host "av==$ver installed"; break }
}
& $VenvPy -c "import av; print('av', av.__version__)"
Write-Host "av pin ok: $avOk"
Write-Host "=== Install soundfile + make 16k mono wav ==="
& $VenvPy -m pip install soundfile
ffmpeg -y -v error -i "$Root\ep001_voice.wav" -ar 16000 -ac 1 "$Root\ep001_voice_16k.wav"
Get-Item "$Root\ep001_voice_16k.wav" | Select-Object Name, Length
Write-Host "=== Transcribe with large-v3 (numpy path, bypasses av) ==="
& $VenvPy "$Root\ai_whisper_test.py" large-v3
Write-Host "=== DONE ==="
Stop-Transcript
