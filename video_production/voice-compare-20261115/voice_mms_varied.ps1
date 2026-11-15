$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\voice_mms_varied.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\voice_mms_varied.py
Stop-Transcript
Write-Output "MMS_VARIED_DONE"
