Start-Transcript -Path 'C:\Users\w\render_demo.log' -Force
Set-Location 'C:\Users\w\agentnet-corner\stickman-shorts'
$sw = [System.Diagnostics.Stopwatch]::StartNew()
.\.venv-win\Scripts\python.exe -m manim render -qm --format=mp4 stickman_demo.py StickmanScene
$renderExit = $LASTEXITCODE
$sw.Stop()
Write-Output "render exit: $renderExit"
Write-Output "render wall time: $($sw.Elapsed.TotalSeconds) seconds"
$mp4 = Get-ChildItem -Recurse -Filter 'StickmanScene.mp4' -Path 'media\videos' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($mp4) {
  Write-Output "mp4 found: $($mp4.FullName) ($($mp4.Length) bytes)"
  ffmpeg -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,duration,codec_name -of default=noprint_wrappers=1 "$($mp4.FullName)"
  New-Item -ItemType Directory -Force -Path 'test_frames\pc' | Out-Null
  ffmpeg -y -v error -i "$($mp4.FullName)" -vf "select=eq(n\,0)" -vframes 1 test_frames\pc\frame_0s.png
  ffmpeg -y -v error -i "$($mp4.FullName)" -vf "select=eq(n\,30)" -vframes 1 test_frames\pc\frame_1s.png
  ffmpeg -y -v error -i "$($mp4.FullName)" -vf "select=eq(n\,60)" -vframes 1 test_frames\pc\frame_2s.png
  ffmpeg -y -v error -i "$($mp4.FullName)" -vf "select=eq(n\,120)" -vframes 1 test_frames\pc\frame_4s.png
  Get-ChildItem test_frames\pc | Select-Object Name, Length
} else {
  Write-Output 'mp4 NOT FOUND under media\videos'
  Get-ChildItem -Recurse -Filter '*.mp4' -Path 'media' | Select-Object FullName, Length
}
Write-Output 'RENDER_DONE'
Stop-Transcript
