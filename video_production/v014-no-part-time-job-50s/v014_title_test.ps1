# Title-capture test: opens a console titled V014_TEST, prints markers, waits.
# Used to test whether ffmpeg gdigrab -i title=... can capture this console
# while it sits BEHIND the user's browser (no focus steal, no disruption).
$ErrorActionPreference = "Continue"
$host.UI.RawUI.WindowTitle = "V014_TEST"
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ConUtil2 {
  [DllImport("kernel32.dll")]
  public static extern IntPtr GetConsoleWindow();
  [DllImport("user32.dll")]
  public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@
[void][ConUtil2]::ShowWindow([ConUtil2]::GetConsoleWindow(), 3)
Write-Host "V014_TEST_MARKER_12345"
Write-Host "Line two of the test console - the quick brown fox"
Write-Host "Line three - 0123456789"
Start-Sleep -Seconds 20
Write-Host "V014_TEST_DONE"
