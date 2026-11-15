$ErrorActionPreference = "Stop"
Start-Transcript -Path "C:\Users\w\voice_edge_diag2.log" -Append
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\voice_edge_diag2.py
Stop-Transcript
Write-Output "EDGE_DIAG2_DONE"
