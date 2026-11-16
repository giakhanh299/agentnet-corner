$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v012_vieneu_install.log" -Force | Out-Null
$PY = "C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe"
$VENV = "C:\Users\w\agentnet-corner\ai-stack\.venv-vieneu"
if ($env:HF_HOME) { Write-Output "HF_HOME already set: $env:HF_HOME" } else {
  $CACHE = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
  if (Test-Path $CACHE) { $env:HF_HOME = $CACHE; Write-Output "HF_HOME set to shared cache: $CACHE" }
  else { Write-Output "HF_HOME not set, shared cache not found, using default" }
}
if (-not (Test-Path "$VENV\Scripts\python.exe")) {
  Write-Output "Creating venv $VENV ..."
  & $PY -m venv $VENV
  if ($LASTEXITCODE -ne 0) { Write-Output "VENV_CREATE_FAILED"; Stop-Transcript | Out-Null; exit 1 }
} else { Write-Output "venv already exists, reusing" }
& "$VENV\Scripts\python.exe" -m pip install --upgrade pip 2>&1 | Select-Object -Last 2
Write-Output "Installing vieneu==3.8.4 ..."
& "$VENV\Scripts\python.exe" -m pip install vieneu==3.8.4 2>&1 | Select-Object -Last 5
& "$VENV\Scripts\python.exe" -m pip list 2>&1 | Select-String -Pattern "vieneu|onnxruntime|numpy|soundfile|scipy"
Write-Output "Smoke test: import + list preset voices (triggers model download + cold load) ..."
& "$VENV\Scripts\python.exe" -c "from vieneu import Vieneu; t=Vieneu(); v=t.list_preset_voices(); print('PRESET_VOICES:', len(v)); print([x for x in v if 'Mai' in str(x)][:5])" 2>&1 | Select-Object -Last 10
Write-Output "V012_VIENEU_INSTALL_DONE"
Stop-Transcript | Out-Null
