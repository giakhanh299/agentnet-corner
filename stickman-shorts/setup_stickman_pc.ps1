$ErrorActionPreference = 'Continue'
$py = 'C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe'
Set-Location 'C:\Users\w\agentnet-corner\stickman-shorts'
Write-Output "START $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
if (-not (Test-Path '.\.venv-win\Scripts\python.exe')) {
  Write-Output 'Creating venv .venv-win ...'
  & $py -m venv .venv-win
  Write-Output "venv exit code: $LASTEXITCODE"
} else {
  Write-Output 'venv already exists, skipping creation'
}
Write-Output '--- venv python version ---'
.\.venv-win\Scripts\python.exe --version
Write-Output '--- upgrading pip ---'
.\.venv-win\Scripts\python.exe -m pip install --upgrade pip
Write-Output "pip upgrade exit code: $LASTEXITCODE"
Write-Output '--- installing requirements (manim==0.22.1) ---'
.\.venv-win\Scripts\python.exe -m pip install -r requirements.txt
Write-Output "pip install exit code: $LASTEXITCODE"
Write-Output '--- manim check ---'
.\.venv-win\Scripts\python.exe -m pip show manim
.\.venv-win\Scripts\python.exe -c "import manim; print('manim', manim.__version__)"
Write-Output "END $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Output 'SETUP_DONE'
