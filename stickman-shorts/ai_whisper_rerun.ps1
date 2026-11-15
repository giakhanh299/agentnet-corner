$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\ai_whisper_rerun.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
Write-Host "=== torch lib CUDA DLLs ==="
Get-ChildItem $TorchLib -Filter "*.dll" | Where-Object { $_.Name -match "cublas|cudart|cudnn|cufft|cusparse|cusolver|curand|cupti" } | Select-Object Name
Write-Host "=== Prepend torch lib to PATH (plain LoadLibrary searches PATH, not AddDllDirectory dirs) ==="
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== Transcribe Ep001 voice.wav with large-v3 (PATH fix) ==="
& $VenvPy "$Root\ai_whisper_test.py" large-v3
Write-Host "=== DONE ==="
Stop-Transcript
