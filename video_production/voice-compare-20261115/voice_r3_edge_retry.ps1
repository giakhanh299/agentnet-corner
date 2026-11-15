$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Start-Transcript -Path "C:\Users\w\voice_r3_edge.log" -Append
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\voice_compare\voice_r3_edge_retry.py
Stop-Transcript
