$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v012_pc_probe.log" -Force | Out-Null
Write-Output "HOST: $env:COMPUTERNAME"
Write-Output "--- ai-stack ---"
Get-ChildItem "C:\Users\w\agentnet-corner\ai-stack" -Name
Write-Output "--- python ---"
& "C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe" --version
Write-Output "--- venv-ai pip list (vieneu?) ---"
& "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe" -m pip list 2>&1 | Select-String -Pattern "vieneu|onnx|torch|faster|transformers|soundfile"
Write-Output "--- SD tooling search ---"
Get-ChildItem "C:\Users\w" -Directory -Name | Select-String -Pattern "comfy|stable|diffusion|sd-|webui" 
Get-ChildItem "C:\Users\w\agentnet-corner" -Directory -Name
Write-Output "--- disk C free GB ---"
(Get-PSDrive C).Free / 1GB
Write-Output "--- ffmpeg ---"
ffmpeg -version 2>&1 | Select-Object -First 1
Write-Output "V012_PC_PROBE_DONE"
Stop-Transcript | Out-Null
