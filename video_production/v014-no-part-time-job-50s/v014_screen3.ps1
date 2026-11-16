# V014 screen recording v3 — steps only (snapshotter is a separate task).
# Same 5 real steps as v014_screen2; the v014_snap task captures this
# console by title every 0.5s. Creates the stop file at the end.
$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_screen3.log" -Force
$host.UI.RawUI.WindowTitle = "V014_SCREEN"
$timesFile = "C:\Users\w\v014_screen3_times.txt"
if (Test-Path $timesFile) { Remove-Item $timesFile -Force }
function Mark-Time($name) {
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
  "$ts $name" | Out-File -FilePath $timesFile -Append -Encoding utf8
  Write-Host "### $ts $name ###"
}
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ConUtil3 {
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct CONSOLE_FONT_INFOEX {
    public uint cbSize; public uint nFont; public short dwFontSizeX; public short dwFontSizeY;
    public int FontFamily; public int FontWeight;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string FaceName;
  }
  [DllImport("kernel32.dll", SetLastError = true)]
  public static extern IntPtr GetStdHandle(int nStdHandle);
  [DllImport("kernel32.dll", SetLastError = true)]
  public static extern bool SetCurrentConsoleFontEx(IntPtr h, bool max, ref CONSOLE_FONT_INFOEX f);
  [DllImport("kernel32.dll")]
  public static extern IntPtr GetConsoleWindow();
  [DllImport("user32.dll")]
  public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@
$hOut = [ConUtil3]::GetStdHandle(-11)
$font = New-Object ConUtil3+CONSOLE_FONT_INFOEX
$font.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($font)
$font.nFont = 0
$font.dwFontSizeX = 0
$font.dwFontSizeY = 36
$font.FontFamily = 54
$font.FontWeight = 400
$font.FaceName = "Consolas"
[void][ConUtil3]::SetCurrentConsoleFontEx($hOut, $false, [ref]$font)
[void][ConUtil3]::ShowWindow([ConUtil3]::GetConsoleWindow(), 3)
Write-Host "Console font 36px Consolas, maximized."
$APY = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$torchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$nvidiaBins = Get-ChildItem "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\nvidia" -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName "bin" } | Where-Object { Test-Path $_ }
$env:PATH = ($torchLib + ";" + ($nvidiaBins -join ";") + ";" + $env:PATH)
$env:HF_HOME = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
Mark-Time "SCREEN3_START"
Start-Sleep -Seconds 2
Mark-Time "STEP1_SCRIPT_BEGIN"
Get-Content C:\Users\w\v014_script.md -TotalCount 32
Mark-Time "STEP1_SCRIPT_END"
Start-Sleep -Seconds 4
Mark-Time "STEP2_TTS_BEGIN"
& $APY C:\Users\w\v014_screen_tts_demo.py
Mark-Time "STEP2_TTS_END"
Start-Sleep -Seconds 3
Mark-Time "STEP3_WHISPER_BEGIN"
& $APY C:\Users\w\v014_fw_final.py
Mark-Time "STEP3_WHISPER_END"
Start-Sleep -Seconds 3
Mark-Time "STEP4_MANIM_BEGIN"
Set-Location C:\Users\w\agentnet-corner\stickman-shorts
.\.venv-win\Scripts\python.exe -m manim render -qm --format=mp4 stickman_demo.py StickmanScene
Mark-Time "STEP4_MANIM_END"
Start-Sleep -Seconds 3
Mark-Time "STEP5_RENDER_BEGIN"
Set-Location C:\Users\w
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\w\v011_render_run.ps1
Mark-Time "STEP5_RENDER_END"
Start-Sleep -Seconds 3
Mark-Time "SCREEN3_DONE"
New-Item -ItemType File -Force -Path "C:\Users\w\v014_screen2_stop.txt" | Out-Null
New-Item -ItemType File -Force -Path "C:\Users\w\v014_screen3_done.txt" | Out-Null
Stop-Transcript
