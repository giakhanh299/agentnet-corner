$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Start-Transcript -Path "C:\Users\w\voice_kokoro_probe.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-kokoro\Scripts\python.exe"
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\voice_kokoro_probe.py
Stop-Transcript
Write-Output "KOKORO_PROBE_DONE"
