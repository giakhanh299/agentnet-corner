$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v014_probe_pc.log" -Force
Write-Host "=== sessions ==="
query session
Write-Host "=== screen ==="
Add-Type -AssemblyName System.Windows.Forms
$s = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
Write-Host ("Primary: {0}x{1} at {2},{3}" -f $s.Width, $s.Height, $s.X, $s.Y)
foreach ($sc in [System.Windows.Forms.Screen]::AllScreens) {
  $b = $sc.Bounds
  Write-Host ("Screen primary={0}: {1}x{2} at {3},{4}" -f $sc.Primary, $b.Width, $b.Height, $b.X, $b.Y)
}
Write-Host "=== ffmpeg ==="
ffmpeg -version 2>&1 | Select-Object -First 1
Write-Host "=== gdigrab test (3s, 640x360) ==="
ffmpeg -y -f gdigrab -framerate 5 -video_size 640x360 -i desktop -t 3 C:\Users\w\v014_gdigrab_test.mp4 2>&1 | Select-Object -Last 5
ffmpeg -y -v error -ss 1 -i C:\Users\w\v014_gdigrab_test.mp4 -frames:v 1 C:\Users\w\v014_gdigrab_frame.png
Get-Item C:\Users\w\v014_gdigrab_test.mp4, C:\Users\w\v014_gdigrab_frame.png | Select-Object Name, Length
Stop-Transcript
