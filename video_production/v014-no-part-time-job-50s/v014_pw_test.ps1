# PrintWindow self-test: prints markers, then snapshots THIS console window
# via PrintWindow (renders the window even when another window covers it)
# to a PNG. Runs in the interactive session via schtasks /IT.
$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_pw_test.log" -Force
Add-Type -AssemblyName System.Drawing
$host.UI.RawUI.WindowTitle = "V014_PW"
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class PWUtil {
  [DllImport("user32.dll", SetLastError = true)]
  public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
  [DllImport("user32.dll", SetLastError = true)]
  public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll", SetLastError = true)]
  public static extern bool GetWindowRect(IntPtr hwnd, out RECT lpRect);
  [DllImport("kernel32.dll")]
  public static extern IntPtr GetConsoleWindow();
  [DllImport("user32.dll")]
  public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [StructLayout(LayoutKind.Sequential)]
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
[void][PWUtil]::ShowWindow([PWUtil]::GetConsoleWindow(), 3)
Write-Host "V014_PW_MARKER_67890"
Write-Host "PrintWindow test line two - the quick brown fox jumps"
Write-Host "PrintWindow test line three - 0123456789 ABCDEF"
Start-Sleep -Seconds 2
$hwnd = [PWUtil]::GetConsoleWindow()
$rect = New-Object PWUtil+RECT
[void][PWUtil]::GetWindowRect($hwnd, [ref]$rect)
$w = $rect.Right - $rect.Left
$h = $rect.Bottom - $rect.Top
Write-Host "Console window: ${w}x${h}"
$bmp = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
$ok = [PWUtil]::PrintWindow($hwnd, $hdc, 0)
$g.ReleaseHdc($hdc)
$g.Dispose()
Write-Host "PrintWindow ok=$ok"
$bmp.Save("C:\Users\w\v014_pw_frame.png", [System.Drawing.Imaging.ImageFormat]::Png)
Write-Host "Saved v014_pw_frame.png"
Start-Sleep -Seconds 5
Stop-Transcript
