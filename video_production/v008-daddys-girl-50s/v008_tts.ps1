$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\v008_tts.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\v008_tts\v008_tts.py
Stop-Transcript
Write-Output "V008_TTS_DONE"
