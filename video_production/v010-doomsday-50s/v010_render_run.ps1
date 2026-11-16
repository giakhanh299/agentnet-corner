# v010 video encode on the PC (user order 2026-11-15 ~21:53: render on my PC).
# 8 image segments, HARD CUTS via concat (no xfade - the script demands
# hard cuts every ~10s; v003's xfade fades are NOT used here). Total 1636
# frames = 54.53s. Run in the foreground; transcript logs everything.
# Do NOT run detached.
#
# LESSON (v003, 2026-11-15 ~22:15): do NOT use "-loop 1" on the image
# inputs. zoompan outputs d frames PER input frame; with -loop 1 the input
# is infinite, so the chain never sees EOF and ffmpeg encodes forever.
# A single image input gives exactly 1 frame -> zoompan outputs exactly d
# frames then EOFs. "-frames:v 1637" is a hard safety cap.
$ErrorActionPreference = "Continue"
Set-Location C:\Users\w\v010_render
if (Test-Path captions_pc.ass) { Copy-Item -Force captions_pc.ass captions.ass }
Start-Transcript -Path C:\Users\w\v010_render\render.log -Force
Write-Host "=== v010 render start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Write-Host "ffmpeg: $(ffmpeg -version 2>&1 | Select-Object -First 1)"
ffmpeg -y -v warning -i images\hook_calendar.png -i images\beat1_science_invention_1928.jpg -i images\beat1b_popular_science_1940.jpg -i images\graph_forecast.png -i images\graph_forecast_zoom.png -i images\graph_growth_rate.png -i images\graph_bars.png -i images\payoff_night_sky.jpg -filter_complex_script assemble_filter_pc.txt -map "[vout]" -frames:v 1637 -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 -an v010_video.mp4
Write-Host "=== FFMPEG_EXIT=$LASTEXITCODE ==="
if ($LASTEXITCODE -ne 0) { Write-Host "VIDEO ENCODE FAILED - skipping mux"; Stop-Transcript; exit 1 }
Get-Item v010_video.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate,width,height,codec_name -of default=noprint_wrappers=1 v010_video.mp4
Write-Host "=== mux video + audio_final.m4a -> v010.mp4 ==="
ffmpeg -y -v warning -i v010_video.mp4 -i audio_final.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest v010.mp4
Write-Host "=== MUX_EXIT=$LASTEXITCODE ==="
Get-Item v010.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of default=noprint_wrappers=1 v010.mp4
Write-Host "=== v010 render end: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Stop-Transcript
