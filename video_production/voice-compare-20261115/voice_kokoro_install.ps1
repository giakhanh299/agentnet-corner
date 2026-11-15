$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Start-Transcript -Path "C:\Users\w\voice_kokoro_install.log" -Append
$VenvDir = "C:\Users\w\agentnet-corner\ai-stack\.venv-kokoro"
$VenvPy = "$VenvDir\Scripts\python.exe"
$VenvPip = "$VenvDir\Scripts\pip.exe"
$Py312 = "C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe"

if (-not (Test-Path $VenvPy)) {
    Write-Output "=== creating venv ==="
    & $Py312 -m venv $VenvDir
}
Write-Output "=== pip upgrade ==="
& $VenvPy -m pip install -q --upgrade pip
Write-Output "=== torch cu128 (from pip cache if present) ==="
& $VenvPy -m pip install -q torch --index-url https://download.pytorch.org/whl/cu128
Write-Output "=== kokoro ==="
& $VenvPy -m pip install -q kokoro soundfile numpy
Write-Output "=== versions ==="
& $VenvPy -c "import torch, kokoro; print('torch', torch.__version__, 'cuda', torch.cuda.is_available()); print('kokoro', kokoro.__version__ if hasattr(kokoro,'__version__') else 'n/a')"
Stop-Transcript
Write-Output "KOKORO_INSTALL_DONE"
