# v006 video encode on the PC (user order 2026-11-15 ~21:53: render on my PC).
# 7 image segments, HARD CUTS via concat (no xfade - the script demands
# hard cuts every ~10s; v003's xfade fades are NOT used here). Total 1594
# frames = 53.13s. Run in the foreground; transcript logs everything.
# Do NOT run detached.
#
# LESSON (v003, 2026-11-15 ~22:15): do NOT use "-loop 1" on the image
# inputs. zoompan outputs d frames PER input frame; with -loop 1 the input
# is infinite, so the chain never sees EOF and ffmpeg encodes forever.
# A single image input gives exactly 1 frame -> zoompan outputs exactly d
# frames then EOFs. "-frames:v 1595" is a hard safety cap.
$ErrorActionPreference = "Continue"
Set-Location C:\Users\w\v006_render
if (Test-Path captions_pc.ass) { Copy-Item -Force captions_pc.ass captions.ass }
Start-Transcript -Path C:\Users\w\v006_render\render.log -Force
Write-Host "=== v006 render start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Write-Host "ffmpeg: $(ffmpeg -version 2>&1 | Select-Object -First 1)"
ffmpeg -y -v warning -i images\hook2_1.jpg -i images\beat1_pressure_2.jpg -i images\beat2b_1.jpg -i images\beat2b_4.jpg -i images\beat3b_1.jpg -i images\beat3_lab_1.jpg -i images\payoff_water_2.jpg -filter_complex_script assemble_filter_pc.txt -map "[vout]" -frames:v 1595 -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 -an v006_video.mp4
Write-Host "=== FFMPEG_EXIT=$LASTEXITCODE ==="
if ($LASTEXITCODE -ne 0) { Write-Host "VIDEO ENCODE FAILED - skipping mux"; Stop-Transcript; exit 1 }
Get-Item v006_video.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate,width,height,codec_name -of default=noprint_wrappers=1 v006_video.mp4
Write-Host "=== mux video + audio_final.m4a -> v006.mp4 ==="
ffmpeg -y -v warning -i v006_video.mp4 -i audio_final.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest v006.mp4
Write-Host "=== MUX_EXIT=$LASTEXITCODE ==="
Get-Item v006.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of default=noprint_wrappers=1 v006.mp4
Write-Host "=== v006 render end: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Stop-Transcript
