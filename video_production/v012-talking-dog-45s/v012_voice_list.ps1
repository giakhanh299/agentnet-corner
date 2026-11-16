$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v012_voice_list.log" -Force | Out-Null
& "C:\Users\w\agentnet-corner\ai-stack\.venv-vieneu\Scripts\python.exe" -c "import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace'); from vieneu import Vieneu; t=Vieneu(); v=t.list_preset_voices(); print('COUNT', len(v)); [print(repr(x)) for x in v]" 2>&1
Write-Output "V012_VOICE_LIST_DONE"
Stop-Transcript | Out-Null
