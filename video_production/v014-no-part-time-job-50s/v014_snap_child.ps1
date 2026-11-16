# V014 child snapshotter - spawned FROM the V014_SCREEN console itself
# (Start-Process), so it shares the parent's window station. Takes the
# parent console hwnd as a plain string argument (no job serialization).
# PrintWindow-snapshots the parent every 0.5s until the stop file appears.
param([string]$HwndStr, [string]$ShotsDir)
$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_snap_child.log" -Force
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ChildSnap {
  [DllImport("user32.dll", SetLastError = true)]
  public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll", SetLastError = true)]
  public static extern bool GetWindowRect(IntPtr hwnd, out RECT lpRect);
  [StructLayout(LayoutKind.Sequential)]
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
$hwnd = [IntPtr]::new([int64]$HwndStr)
Write-Host "CHILD_SNAP hwnd=$HwndStr shots=$ShotsDir"
$n = 0
while (-not (Test-Path "C:\Users\w\v014_screen2_stop.txt")) {
  try {
    $rect = New-Object ChildSnap+RECT
    [void][ChildSnap]::GetWindowRect($hwnd, [ref]$rect)
    $w = $rect.Right - $rect.Left
    $h = $rect.Bottom - $rect.Top
    if ($w -gt 100 -and $h -gt 100) {
      $n++
      $bmp = New-Object System.Drawing.Bitmap($w, $h)
      $g = [System.Drawing.Graphics]::FromImage($bmp)
      $hdc = $g.GetHdc()
      $ok = [ChildSnap]::PrintWindow($hwnd, $hdc, 0)
      $g.ReleaseHdc($hdc)
      $g.Dispose()
      $bmp.Save("$ShotsDir\shot_$($n.ToString('0000')).png", [System.Drawing.Imaging.ImageFormat]::Png)
      $bmp.Dispose()
      if ($n -eq 1) { Write-Host "CHILD_SNAP_OK first shot ${w}x${h} ok=$ok" }
    } else {
      Write-Host "CHILD_SNAP_BAD_RECT ${w}x${h}"
    }
  } catch {
    Write-Host "CHILD_SNAP_ERROR: $($_.Exception.Message)"
  }
  Start-Sleep -Milliseconds 500
  if ($n -ge 400) { break }
}
Write-Host "CHILD_SNAP_DONE total=$n"
Stop-Transcript
