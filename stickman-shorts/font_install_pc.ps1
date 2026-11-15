Start-Transcript -Path 'C:\Users\w\font_install.log' -Force
$srcDir = 'C:\Users\w\agentnet-corner\stickman-shorts\src\assets\fonts'
$userFonts = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"
New-Item -ItemType Directory -Force -Path $userFonts | Out-Null
foreach ($f in @('BeVietnamPro-Regular.ttf','BeVietnamPro-Bold.ttf')) {
  $src = Join-Path $srcDir $f
  Write-Output "--- $f ---"
  try {
    Copy-Item $src 'C:\Windows\Fonts' -Force -ErrorAction Stop
    Write-Output 'C:\Windows\Fonts copy: OK'
  } catch {
    Write-Output "C:\Windows\Fonts copy: FAILED ($($_.Exception.Message))"
  }
  Copy-Item $src $userFonts -Force
  Write-Output "per-user Fonts copy: OK ($userFonts\$f)"
}
$regPath = 'HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
New-ItemProperty -Path $regPath -Name 'Be Vietnam Pro (TrueType)' -Value 'BeVietnamPro-Regular.ttf' -PropertyType String -Force | Out-Null
New-ItemProperty -Path $regPath -Name 'Be Vietnam Pro Bold (TrueType)' -Value 'BeVietnamPro-Bold.ttf' -PropertyType String -Force | Out-Null
Write-Output 'HKCU Fonts registry entries: OK'
Get-ItemProperty -Path $regPath | Select-Object -ExpandProperty 'Be Vietnam Pro (TrueType)' -ErrorAction SilentlyContinue
Get-ItemProperty -Path $regPath | Select-Object -ExpandProperty 'Be Vietnam Pro Bold (TrueType)' -ErrorAction SilentlyContinue
Write-Output '--- manimpango font check ---'
Set-Location 'C:\Users\w\agentnet-corner\stickman-shorts'
.\.venv-win\Scripts\python.exe -c "import manimpango; print([f for f in manimpango.list_fonts() if 'Be Vietnam' in f])"
Write-Output "font check exit: $LASTEXITCODE"
Write-Output 'FONT_INSTALL_DONE'
Stop-Transcript
