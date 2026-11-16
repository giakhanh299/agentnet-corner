# V014 screen recording v2 — PrintWindow snapshots (no focus steal).
# The user's browser stays on top; this script snapshots ITS OWN console
# window via PrintWindow every 0.5s (true screenshots of the real terminal,
# even while another window covers it), while the real pipeline commands
# run in the foreground of that console. No gdigrab, no focus change.
$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_screen2.log" -Force
Add-Type -AssemblyName System.Drawing
$host.UI.RawUI.WindowTitle = "V014_SCREEN"
$timesFile = "C:\Users\w\v014_screen2_times.txt"
$shotsDir = "C:\Users\w\v014_shots"
New-Item -ItemType Directory -Force -Path $shotsDir | Out-Null
Remove-Item "$shotsDir\*.png" -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Users\w\v014_screen2_stop.txt" -Force -ErrorAction SilentlyContinue
if (Test-Path $timesFile) { Remove-Item $timesFile -Force }
function Mark-Time($name) {
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
  "$ts $name" | Out-File -FilePath $timesFile -Append -Encoding utf8
  Write-Host "### $ts $name ###"
}
# --- console font 36px Consolas + maximize (this window only) ---
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
$hwnd = [ConUtil3]::GetConsoleWindow()
Write-Host "Console hwnd=$hwnd, font 36px Consolas, maximized."
# --- PATH fix for .venv-ai (cuBLAS) ---
$APY = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$torchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$nvidiaBins = Get-ChildItem "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\nvidia" -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName "bin" } | Where-Object { Test-Path $_ }
$env:PATH = ($torchLib + ";" + ($nvidiaBins -join ";") + ";" + $env:PATH)
$env:HF_HOME = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
Mark-Time "SCREEN2_START"
# --- snapshot job: PrintWindow this console every 0.5s until stop file ---
$job = Start-Job -ArgumentList $hwnd, $shotsDir -ScriptBlock {
  param($hwnd, $shotsDir)
  Add-Type -AssemblyName System.Drawing
  Add-Type @"
using System;
using System.Runtime.InteropServices;
public class PWJob {
  [DllImport("user32.dll", SetLastError = true)]
  public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll", SetLastError = true)]
  public static extern bool GetWindowRect(IntPtr hwnd, out RECT lpRect);
  [StructLayout(LayoutKind.Sequential)]
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
  $n = 0
  while (-not (Test-Path "C:\Users\w\v014_screen2_stop.txt")) {
    $n++
    try {
      $rect = New-Object PWJob+RECT
      [void][PWJob]::GetWindowRect($hwnd, [ref]$rect)
      $w = $rect.Right - $rect.Left
      $h = $rect.Bottom - $rect.Top
      if ($w -gt 100 -and $h -gt 100) {
        $bmp = New-Object System.Drawing.Bitmap($w, $h)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $hdc = $g.GetHdc()
        [void][PWJob]::PrintWindow($hwnd, $hdc, 0)
        $g.ReleaseHdc($hdc)
        $g.Dispose()
        $bmp.Save("$shotsDir\shot_$($n.ToString('0000')).png", [System.Drawing.Imaging.ImageFormat]::Png)
        $bmp.Dispose()
      }
    } catch { }
    Start-Sleep -Milliseconds 500
    if ($n -ge 400) { break }
  }
}
Mark-Time "SNAP_STARTED"
Start-Sleep -Seconds 2
# --- 1. script file ---
Mark-Time "STEP1_SCRIPT_BEGIN"
Get-Content C:\Users\w\v014_script.md -TotalCount 32
Mark-Time "STEP1_SCRIPT_END"
Start-Sleep -Seconds 4
# --- 2. MMS-TTS synthesis demo ---
Mark-Time "STEP2_TTS_BEGIN"
& $APY C:\Users\w\v014_screen_tts_demo.py
Mark-Time "STEP2_TTS_END"
Start-Sleep -Seconds 3
# --- 3. faster-whisper final check on the assembled V014 voice ---
Mark-Time "STEP3_WHISPER_BEGIN"
& $APY C:\Users\w\v014_fw_final.py
Mark-Time "STEP3_WHISPER_END"
Start-Sleep -Seconds 3
# --- 4. Manim stickman render ---
Mark-Time "STEP4_MANIM_BEGIN"
Set-Location C:\Users\w\agentnet-corner\stickman-shorts
.\.venv-win\Scripts\python.exe -m manim render -qm --format=mp4 stickman_demo.py StickmanScene
Mark-Time "STEP4_MANIM_END"
Start-Sleep -Seconds 3
# --- 5. ffmpeg video encode (v011 re-render, real command) ---
Mark-Time "STEP5_RENDER_BEGIN"
Set-Location C:\Users\w
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\w\v011_render_run.ps1
Mark-Time "STEP5_RENDER_END"
Start-Sleep -Seconds 3
# --- stop snapshots ---
Mark-Time "SNAP_STOP"
New-Item -ItemType File -Force -Path "C:\Users\w\v014_screen2_stop.txt" | Out-Null
Wait-Job $job -Timeout 20 | Out-Null
Stop-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -Force -ErrorAction SilentlyContinue
Mark-Time "SCREEN2_DONE"
New-Item -ItemType File -Force -Path "C:\Users\w\v014_screen2_done.txt" | Out-Null
Stop-Transcript
