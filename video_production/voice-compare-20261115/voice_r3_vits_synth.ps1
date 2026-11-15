$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-vits\Scripts\python.exe"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-vits\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Start-Transcript -Path "C:\Users\w\voice_r3_vits_synth.log" -Append
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\voice_compare\voice_r3_vits_synth.py
Stop-Transcript
