$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\ai_cublas_diag.log" -Force
$Venv = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai"
Write-Host "=== nvidia packages in site-packages ==="
Get-ChildItem "$Venv\Lib\site-packages\nvidia" -Directory | Select-Object Name
Write-Host "=== search cublas64_12.dll under venv ==="
Get-ChildItem "$Venv" -Recurse -Filter "cublas64_12.dll" -ErrorAction SilentlyContinue | Select-Object FullName
Write-Host "=== torch lib cublas dlls ==="
Get-ChildItem "$Venv\Lib\site-packages\torch\lib" -Filter "cublas*.dll" -ErrorAction SilentlyContinue | Select-Object Name
Write-Host "=== nvidia cublas bin contents ==="
Get-ChildItem "$Venv\Lib\site-packages\nvidia\cublas\bin" -ErrorAction SilentlyContinue | Select-Object Name
Write-Host "=== pip list nvidia ==="
& "$Venv\Scripts\python.exe" -m pip list 2>$null | Select-String -Pattern "nvidia|ctranslate|torch"
Write-Host "=== python glob check ==="
& "$Venv\Scripts\python.exe" -c "import glob, os, sys; s=os.path.normpath(os.path.join(os.path.dirname(sys.executable),'..','Lib','site-packages')); print(s); print(glob.glob(os.path.join(s,'nvidia','*','bin')))"
Write-Host "=== DONE ==="
Stop-Transcript
