# V014 video encode on the PC (user order 2026-11-15 ~21:53: render on my PC).
# 9 segments, HARD CUTS via concat (v006/v011 pattern). Total 1562 frames = 52.07s.
# Screen segments are REAL PrintWindow snapshots of the PC terminal
# (2 fps, 99 shots captured 2026-11-16 21:16:32-21:17:22 by a child process
# of the interactive console - no focus steal, browser untouched).
# Shot ranges (child started 21:16:32.2, 0.5s/shot):
#  hook  shots 69-82 (render), b1a 13-24 (TTS), b1b 31-42 (Whisper),
#  step1 5-16 (script), step2 23-28 (TTS), step3 52-58 (Manim),
#  step4 81-90 (render). Each input gets 1 extra shot; trim cuts exact.
# Cards: calendar (b3) + payoff, zoompan 1.0->1.04, NO -loop 1 (v003 lesson).
# Run in the foreground; transcript logs everything. Do NOT run detached.
$ErrorActionPreference = "Continue"
Set-Location C:\Users\w\v014_render
if (Test-Path captions_pc.ass) { Copy-Item -Force captions_pc.ass captions.ass }
Start-Transcript -Path "C:\Users\w\v014_render\render.log" -Force
Write-Host "=== v014 render start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Write-Host "ffmpeg: $(ffmpeg -version 2>&1 | Select-Object -First 1)"
ffmpeg -y -v warning -framerate 2 -start_number 69 -t 7.0 -i ..\v014_shots\shot_%04d.png -framerate 2 -start_number 13 -t 6.0 -i ..\v014_shots\shot_%04d.png -framerate 2 -start_number 31 -t 6.0 -i ..\v014_shots\shot_%04d.png -framerate 2 -start_number 5 -t 6.0 -i ..\v014_shots\shot_%04d.png -framerate 2 -start_number 23 -t 3.0 -i ..\v014_shots\shot_%04d.png -framerate 2 -start_number 52 -t 3.5 -i ..\v014_shots\shot_%04d.png -framerate 2 -start_number 81 -t 5.0 -i ..\v014_shots\shot_%04d.png -i card_calendar.png -i card_payoff.png -filter_complex_script assemble_filter_pc.txt -map "[vout]" -frames:v 1562 -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 -an v014_video.mp4
Write-Host "=== FFMPEG_EXIT=$LASTEXITCODE ==="
if ($LASTEXITCODE -ne 0) { Write-Host "VIDEO ENCODE FAILED - skipping mux"; Stop-Transcript; exit 1 }
Get-Item v014_video.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate,width,height,codec_name -of default=noprint_wrappers=1 v014_video.mp4
Write-Host "=== mux video + audio_final.m4a -> v014.mp4 ==="
ffmpeg -y -v warning -i v014_video.mp4 -i audio_final.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest v014.mp4
Write-Host "=== MUX_EXIT=$LASTEXITCODE ==="
Get-Item v014.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of default=noprint_wrappers=1 v014.mp4
Write-Host "=== v014 render end: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Stop-Transcript
