Start-Transcript -Path 'C:\Users\w\pip_install.log' -Force
Set-Location 'C:\Users\w\agentnet-corner\stickman-shorts'
$venvPy = '.\.venv-win\Scripts\python.exe'
& $venvPy --version
& $venvPy -m pip install --upgrade pip --disable-pip-version-check
Write-Output "pip upgrade exit: $LASTEXITCODE"
& $venvPy -m pip install -r requirements.txt --disable-pip-version-check
Write-Output "pip install exit: $LASTEXITCODE"
& $venvPy -m pip show manim
& $venvPy -c "import manim; print('manim', manim.__version__)"
Write-Output 'PIP_INSTALL_DONE'
Stop-Transcript
