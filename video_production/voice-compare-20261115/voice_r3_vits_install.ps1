$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Start-Transcript -Path "C:\Users\w\voice_r3_vits_install.log" -Append

Write-Host "=== Installed Pythons ==="
py -0p

$VenvDir = "C:\Users\w\agentnet-corner\ai-stack\.venv-vits"
$VenvPy = "$VenvDir\Scripts\python.exe"
if (-not (Test-Path $VenvPy)) {
    Write-Host "=== Creating venv with Python 3.10 (isolated, inside agentnet-corner) ==="
    py -3.10 -m venv $VenvDir
}
& $VenvPy -m pip install --upgrade pip
Write-Host "=== Installing torch cu128 (from PC pip cache if present) ==="
& $VenvPy -m pip install torch --index-url https://download.pytorch.org/whl/cu128
Write-Host "=== Installing Coqui TTS ==="
& $VenvPy -m pip install TTS
Write-Host "=== TTS version ==="
& $VenvPy -c "import TTS; print('TTS', TTS.__version__)"
& $VenvPy -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())"

Write-Host "=== Downloading VITS-OpenBible model files (998 MB) ==="
$ModelDir = "C:\Users\w\agentnet-corner\ai-stack\voice_compare\vits_openbible"
New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null
$Base = "https://huggingface.co/multilingual-tts/VITS-OpenBible-Vietnamese/resolve/main"
curl.exe -L -o "$ModelDir\model_last.pth" "$Base/model_last.pth"
curl.exe -L -o "$ModelDir\config.json" "$Base/config.json"
curl.exe -L -o "$ModelDir\speakers.pth" "$Base/speakers.pth"
Get-ChildItem $ModelDir | Select-Object Name, Length
Stop-Transcript
Write-Host "VITS_INSTALL_DONE"
