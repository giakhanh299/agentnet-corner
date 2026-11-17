# Start AgentNet V2.0 GPU Worker Daemon on PC Windows (RTX 5060 Ti 16GB)
# Pre-configures PyTorch cuBLAS DLL PATH and UTF-8 console automatically.
param(
    [string]$Master = "http://100.67.236.124:8110",
    [string]$Role = "engineer",
    [int]$PollSeconds = 8
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPy = Join-Path $RepoRoot "ai-stack\.venv-ai\Scripts\python.exe"
$TorchLib = Join-Path $RepoRoot "ai-stack\.venv-ai\Lib\site-packages\torch\lib"

if (-not (Test-Path $VenvPy)) {
    throw "AI virtualenv Python not found at $VenvPy"
}
if (Test-Path $TorchLib) {
    $env:PATH = "$TorchLib;$env:PATH"
}
$env:PYTHONIOENCODING = "utf-8"

Set-Location $RepoRoot
Write-Host "[AgentNet Auto-99%] Starting PC GPU Worker ($Role) -> $Master ..." -ForegroundColor Cyan
& $VenvPy -m auto99.worker_daemon $Role --master $Master --poll-seconds $PollSeconds
