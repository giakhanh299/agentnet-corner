$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\voice_f5_install.log" -Append
$Py312 = "C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe"
Write-Output "=== create venv-f5 ==="
& $Py312 -m venv C:\Users\w\agentnet-corner\ai-stack\.venv-f5
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\python.exe"
& $VenvPy -m pip install --upgrade pip
Write-Output "=== install torch cu128 ==="
& $VenvPy -m pip install torch --index-url https://download.pytorch.org/whl/cu128
Write-Output "=== install f5-tts ==="
& $VenvPy -m pip install f5-tts
Write-Output "=== versions ==="
& $VenvPy -m pip show f5-tts torch torchaudio | Select-String "Name|Version"
Write-Output "=== f5-tts CLI help ==="
& "C:\Users\w\agentnet-corner\ai-stack\.venv-f5\Scripts\f5-tts_infer-cli.exe" --help
Stop-Transcript
Write-Output "F5_INSTALL_DONE"
