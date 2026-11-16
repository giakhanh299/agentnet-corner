# V014 snapshotter - runs as its own interactive task (schtasks /IT).
# Finds the V014_SCREEN console BY TITLE and PrintWindow-snapshots it
# every 0.5s (true screenshots of the real terminal, even while the user's
# browser covers it). Minimizes its OWN window immediately; never touches
# focus. Stops when C:\Users\w\v014_screen2_stop.txt appears.
$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_snap.log" -Force
Add-Type -AssemblyName System.Drawing
$host.UI.RawUI.WindowTitle = "V014_SNAP"
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class SnapUtil {
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
[void][SnapUtil]::ShowWindow([SnapUtil]::GetConsoleWindow(), 6)
$shotsDir = "C:\Users\w\v014_shots"
$n = 0
$misses = 0
while (-not (Test-Path "C:\Users\w\v014_screen2_stop.txt")) {
  try {
    $hwnd = [SnapUtil]::FindWindow($null, "V014_SCREEN")
    if ($hwnd -ne [IntPtr]::Zero) {
      $rect = New-Object SnapUtil+RECT
      [void][SnapUtil]::GetWindowRect($hwnd, [ref]$rect)
      $w = $rect.Right - $rect.Left
      $h = $rect.Bottom - $rect.Top
      if ($w -gt 100 -and $h -gt 100) {
        $n++
        $bmp = New-Object System.Drawing.Bitmap($w, $h)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $hdc = $g.GetHdc()
        $ok = [SnapUtil]::PrintWindow($hwnd, $hdc, 0)
        $g.ReleaseHdc($hdc)
        $g.Dispose()
        $bmp.Save("$shotsDir\shot_$($n.ToString('0000')).png", [System.Drawing.Imaging.ImageFormat]::Png)
        $bmp.Dispose()
        if ($n -eq 1) { Write-Host "SNAP_OK first shot ${w}x${h} ok=$ok" }
      } else {
        Write-Host "SNAP_BAD_RECT ${w}x${h}"
      }
    } else {
      $misses++
      if ($misses -le 3) { Write-Host "SNAP_NO_WINDOW yet (miss $misses)" }
    }
  } catch {
    Write-Host "SNAP_ERROR: $($_.Exception.Message)"
  }
  Start-Sleep -Milliseconds 500
  if ($n -ge 400) { break }
}
Write-Host "SNAP_DONE total=$n"
Stop-Transcript
