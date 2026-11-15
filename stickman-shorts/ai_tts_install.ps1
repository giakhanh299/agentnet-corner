$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\ai_tts_install.log" -Force
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"
Write-Host "=== Install transformers (for MMS-TTS) ==="
& $VenvPy -m pip install transformers
& $VenvPy -c "import transformers; print('transformers', transformers.__version__)"
Write-Host "=== MMS-TTS test: synthesize 3 sentences + Whisper tone check ==="
& $VenvPy "$Root\ai_tts_test.py"
Write-Host "=== DONE ==="
Stop-Transcript
