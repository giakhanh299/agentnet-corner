$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\voice_edge_install.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
Write-Output "=== ffmpeg check ==="
Get-Command ffmpeg | Select-Object -ExpandProperty Source
ffmpeg -version | Select-Object -First 1
Write-Output "=== install edge-tts ==="
& $VenvPy -m pip install --upgrade edge-tts
Write-Output "=== vi-VN voices ==="
& $VenvPy -m edge_tts --list-voices | Select-String "vi-VN"
Stop-Transcript
Write-Output "EDGE_INSTALL_DONE"
