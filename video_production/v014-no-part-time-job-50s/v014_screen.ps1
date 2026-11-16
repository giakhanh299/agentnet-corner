# V014 screen recording — runs in the INTERACTIVE console session (schtasks /IT).
# Maximizes the console, sets a large font, starts ffmpeg gdigrab as a
# background job capturing the real desktop, then runs the REAL pipeline
# commands so their terminal output is what the video shows:
#   1. script file (Get-Content)      2. MMS-TTS synthesis demo
#   3. faster-whisper check (final)   4. Manim stickman render
#   5. ffmpeg video encode (v011 re-render)
# Timestamps of every step are logged to v014_screen_times.txt so clips can
# be cut exactly. A done-marker file is written at the end.
$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_screen.log" -Force
$timesFile = "C:\Users\w\v014_screen_times.txt"
function Mark-Time($name) {
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
  "$ts $name" | Out-File -FilePath $timesFile -Append -Encoding utf8
  Write-Host "### $ts $name ###"
}
# --- console font 24px Consolas + maximize (this window only, no registry) ---
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ConUtil {
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
$hOut = [ConUtil]::GetStdHandle(-11)
$font = New-Object ConUtil+CONSOLE_FONT_INFOEX
$font.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($font)
$font.nFont = 0
$font.dwFontSizeX = 0
$font.dwFontSizeY = 24
$font.FontFamily = 54
$font.FontWeight = 400
$font.FaceName = "Consolas"
[void][ConUtil]::SetCurrentConsoleFontEx($hOut, $false, [ref]$font)
[void][ConUtil]::ShowWindow([ConUtil]::GetConsoleWindow(), 3)
Write-Host "Console: font 24px Consolas, maximized."
# --- PATH fix for .venv-ai (cuBLAS) ---
$APY = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$torchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$nvidiaBins = Get-ChildItem "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\nvidia" -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName "bin" } | Where-Object { Test-Path $_ }
$env:PATH = ($torchLib + ";" + ($nvidiaBins -join ";") + ";" + $env:PATH)
$env:HF_HOME = "D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE"
if (Test-Path $timesFile) { Remove-Item $timesFile -Force }
Mark-Time "SCREEN_START"
# --- start gdigrab capture (background job, same interactive session) ---
$job = Start-Job -ScriptBlock {
  Set-Location C:\Users\w
  ffmpeg -y -f gdigrab -framerate 30 -video_size 1024x768 -i desktop -t 180 -c:v libx264 -crf 23 -preset veryfast -pix_fmt yuv420p C:\Users\w\v014_screen_raw.mkv
}
Mark-Time "GRAB_STARTED"
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
# --- stop capture ---
Mark-Time "GRAB_STOP"
Stop-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -Force -ErrorAction SilentlyContinue
Mark-Time "SCREEN_DONE"
New-Item -ItemType File -Force -Path "C:\Users\w\v014_screen_done.txt" | Out-Null
Stop-Transcript
