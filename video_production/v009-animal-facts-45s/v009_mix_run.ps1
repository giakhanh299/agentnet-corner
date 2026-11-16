$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v009_mix.log" -Force
$Py = "C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe"
$Root = "C:\Users\w\v009_render"
if (-not (Test-Path $Root)) { New-Item -ItemType Directory -Path $Root | Out-Null }
$Need = @(
  "C:\Users\w\agentnet-corner\ai-stack\v009_voice.wav",
  "C:\Users\w\agentnet-corner\stickman-shorts\src\assets\audio\music\bgm_comedy.ogg",
  "C:\Users\w\agentnet-corner\stickman-shorts\src\assets\audio\sfx\whoosh.ogg",
  "C:\Users\w\agentnet-corner\stickman-shorts\src\assets\audio\sfx\pop.ogg",
  "C:\Users\w\agentnet-corner\stickman-shorts\src\assets\audio\sfx\ding.ogg"
)
foreach ($f in $Need) { if (-not (Test-Path $f)) { Write-Host "MISSING: $f"; exit 1 } }
Write-Host "=== V009 MIX: voice + bgm_comedy + SFX, two-pass loudnorm -16 LUFS ==="
& $Py "C:\Users\w\v009_mix.py"
Write-Host "=== DONE ==="
Stop-Transcript
