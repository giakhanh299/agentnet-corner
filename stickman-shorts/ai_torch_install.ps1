$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\ai_torch_install.log" -Force
$Py = "C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe"
$Root = "C:\Users\w\agentnet-corner\ai-stack"
$Venv = "$Root\.venv-ai"
Write-Host "=== Disk free (C:) ==="
Get-PSDrive C | Select-Object Name, @{N='FreeGB';E={[math]::Round($_.Free/1GB,1)}}
Write-Host "=== Python ==="
& $Py --version
if (-not (Test-Path "$Venv\Scripts\python.exe")) {
  Write-Host "=== Creating venv $Venv ==="
  New-Item -ItemType Directory -Force -Path $Root | Out-Null
  & $Py -m venv $Venv
} else {
  Write-Host "=== venv already exists, reusing ==="
}
Write-Host "=== Upgrade pip ==="
& "$Venv\Scripts\python.exe" -m pip install --upgrade pip
Write-Host "=== Install torch (cu128) ==="
& "$Venv\Scripts\python.exe" -m pip install torch --index-url https://download.pytorch.org/whl/cu128
Write-Host "=== Verify torch / CUDA ==="
& "$Venv\Scripts\python.exe" -c "import torch; print('torch', torch.__version__); print('cuda', torch.version.cuda); print('cuda_available', torch.cuda.is_available()); print('device', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none'); print('cap', torch.cuda.get_device_capability(0) if torch.cuda.is_available() else 'none')"
Write-Host "=== Matmul on CUDA ==="
& "$Venv\Scripts\python.exe" -c "import torch; a=torch.randn(512,512,device='cuda'); b=torch.randn(512,512,device='cuda'); c=a@b; print('matmul ok', tuple(c.shape), float(c.abs().mean()))"
Write-Host "=== DONE ==="
Stop-Transcript
