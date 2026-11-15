$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\voice_r2_synth.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\voice_compare\voice_r2_synth.py
Stop-Transcript
Write-Output "VOICE_R2_SYNTH_DONE"
