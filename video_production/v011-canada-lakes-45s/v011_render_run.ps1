# v011 video encode on the PC (user order 2026-11-15 ~21:53: render on my PC).
# 7 image segments, HARD CUTS via concat (no xfade - the script demands
# hard cuts every ~10s; v006 pattern). Total 1489 frames = 49.58s.
# Run in the foreground; transcript logs everything. Do NOT run detached.
#
# LESSON (v003, 2026-11-15 ~22:15): do NOT use "-loop 1" on the image
# inputs. zoompan outputs d frames PER input frame; with -loop 1 the input
# is infinite, so the chain never sees EOF and ffmpeg encodes forever.
# A single image input gives exactly 1 frame -> zoompan outputs exactly d
# frames then EOFs. "-frames:v 1490" is a hard safety cap.
# LESSON (v006): concat needs identical SAR - every zoompan ends with
# setsar=1.
$ErrorActionPreference = "Continue"
Set-Location C:\Users\w\v011_render
if (Test-Path captions_pc.ass) { Copy-Item -Force captions_pc.ass captions.ass }
Copy-Item -Force C:\Windows\Fonts\BeVietnamPro-Bold.ttf .\BeVietnamPro-Bold.ttf
Start-Transcript -Path C:\Users\w\v011_render\render.log -Force
Write-Host "=== v011 render start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Write-Host "ffmpeg: $(ffmpeg -version 2>&1 | Select-Object -First 1)"
ffmpeg -y -v warning -i images\hook_earth1.jpg -i images\canada_map.png -i images\beat2_glacier1.jpg -i images\beat2_glacier2.jpg -i images\beat3_superior.jpg -i images\beat1_nunavut.jpg -i images\payoff_moraine3.jpg -filter_complex_script assemble_filter_pc.txt -map "[vout]" -frames:v 1490 -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 -an v011_video.mp4
Write-Host "=== FFMPEG_EXIT=$LASTEXITCODE ==="
if ($LASTEXITCODE -ne 0) { Write-Host "VIDEO ENCODE FAILED - skipping mux"; Stop-Transcript; exit 1 }
Get-Item v011_video.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate,width,height,codec_name -of default=noprint_wrappers=1 v011_video.mp4
Write-Host "=== mux video + audio_final.m4a -> v011.mp4 ==="
ffmpeg -y -v warning -i v011_video.mp4 -i audio_final.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest v011.mp4
Write-Host "=== MUX_EXIT=$LASTEXITCODE ==="
Get-Item v011.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of default=noprint_wrappers=1 v011.mp4
Write-Host "=== v011 render end: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Stop-Transcript
