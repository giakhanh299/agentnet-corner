Start-Transcript -Path 'C:\Users\w\font_fix.log' -Force
$regPath = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
try {
  New-ItemProperty -Path $regPath -Name 'Be Vietnam Pro (TrueType)' -Value 'BeVietnamPro-Regular.ttf' -PropertyType String -Force | Out-Null
  New-ItemProperty -Path $regPath -Name 'Be Vietnam Pro Bold (TrueType)' -Value 'BeVietnamPro-Bold.ttf' -PropertyType String -Force | Out-Null
  Write-Output 'HKLM Fonts registry entries: OK'
} catch {
  Write-Output "HKLM Fonts registry entries: FAILED ($($_.Exception.Message))"
}
Get-ItemProperty -Path $regPath | Select-Object -ExpandProperty 'Be Vietnam Pro (TrueType)' -ErrorAction SilentlyContinue
$fcCache = "$env:LOCALAPPDATA\fontconfig\cache"
if (Test-Path $fcCache) {
  Remove-Item "$fcCache\*" -Force -ErrorAction SilentlyContinue
  Write-Output 'fontconfig cache cleared'
} else {
  Write-Output 'no fontconfig cache dir found'
}
Write-Output '--- full manimpango font dump ---'
Set-Location 'C:\Users\w\agentnet-corner\stickman-shorts'
.\.venv-win\Scripts\python.exe -c "import manimpango; fs = manimpango.list_fonts(); print('total fonts:', len(fs)); print([f for f in fs if 'Be Vietnam' in f]); print('sample:', fs[:10])"
Write-Output "font check exit: $LASTEXITCODE"
Write-Output 'FONT_FIX_DONE'
Stop-Transcript
