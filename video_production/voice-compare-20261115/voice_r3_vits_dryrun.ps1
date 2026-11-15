$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\python.exe"
Start-Transcript -Path "C:\Users\w\voice_r3_vits_dryrun.log" -Append
& $VenvPy -m pip install --dry-run TTS 2>&1 | Select-String -Pattern "Would install|torch|TTS|ERROR|error" | Select-Object -First 40
Stop-Transcript
