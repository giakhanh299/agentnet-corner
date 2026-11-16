$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_vieneu_install.log" -Force
$PY = "C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe"
$VENV = "C:\Users\w\agentnet-corner\ai-stack\.venv-vieneu"
$env:HF_HOME = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
Write-Host "Python: $PY"
& $PY --version
if (-not (Test-Path "$VENV\Scripts\python.exe")) {
  Write-Host "Creating venv $VENV ..."
  & $PY -m venv $VENV
  if ($LASTEXITCODE -ne 0) { Write-Host "VENV CREATE FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
} else {
  Write-Host "Venv already exists, reusing."
}
$VPY = "$VENV\Scripts\python.exe"
Write-Host "Upgrading pip ..."
& $VPY -m pip install --upgrade pip 2>&1 | Select-Object -Last 2
Write-Host "Installing vieneu + soundfile + numpy ..."
& $VPY -m pip install vieneu soundfile numpy 2>&1 | Select-Object -Last 5
if ($LASTEXITCODE -ne 0) { Write-Host "PIP INSTALL FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
Write-Host "Import test + tiny synthesis (downloads ~500MB model on first run) ..."
$env:HF_HOME = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
& $VPY -c "from vieneu import Vieneu; t=Vieneu(); print('preset voices:', len(t.list_preset_voices())); a=t.infer('Xin chao, day la giong Mai Anh.', voice='Mai Anh'); print('synth samples:', len(a)); print('VIENEU_PC_OK')"
if ($LASTEXITCODE -ne 0) { Write-Host "VIENEU TEST FAILED exit=$LASTEXITCODE"; Stop-Transcript; exit 1 }
Write-Host "VIENEU_PC_INSTALL_DONE"
Stop-Transcript
