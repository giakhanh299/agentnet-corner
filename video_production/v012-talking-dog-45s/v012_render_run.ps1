# v012 video encode on the PC (user order 2026-11-15 ~21:53: render on my PC).
# 7 image segments, HARD CUTS via concat (no xfade; v006/v011 pattern).
# Total 1664 frames = 55.47s. Run in the foreground; transcript logs
# everything. Do NOT run detached.
#
# LESSON (v003): do NOT use "-loop 1" on the image inputs. zoompan outputs
# d frames PER input frame; with -loop 1 the input is infinite, so the
# chain never sees EOF and ffmpeg encodes forever. A single image input
# gives exactly 1 frame -> zoompan outputs exactly d frames then EOFs.
# "-frames:v 1665" is a hard safety cap.
# LESSON (v006): concat needs identical SAR - every zoompan ends with setsar=1.
# LESSON (v011): drawtext needs expansion=none on EVERY instance ("%" text
# is silently dropped otherwise); view a frame inside every label window.
$ErrorActionPreference = "Continue"
Set-Location C:\Users\w\v012_render
if (Test-Path captions_pc.ass) { Copy-Item -Force captions_pc.ass captions.ass }
Copy-Item -Force C:\Windows\Fonts\BeVietnamPro-Bold.ttf .\BeVietnamPro-Bold.ttf
Start-Transcript -Path C:\Users\w\v012_render\render.log -Force
Write-Host "=== v012 render start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Write-Host "ffmpeg: $(ffmpeg -version 2>&1 | Select-Object -First 1)"
ffmpeg -y -v warning -i images\hook.jpg -i images\hook.jpg -i images\b2a.jpg -i images\b2b.jpg -i images\b2c.jpg -i images\b3.jpg -i images\b3.jpg -filter_complex_script assemble_filter_pc.txt -map "[vout]" -frames:v 1665 -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 -an v012_video.mp4
Write-Host "=== FFMPEG_EXIT=$LASTEXITCODE ==="
if ($LASTEXITCODE -ne 0) { Write-Host "VIDEO ENCODE FAILED - skipping mux"; Stop-Transcript; exit 1 }
Get-Item v012_video.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate,width,height,codec_name -of default=noprint_wrappers=1 v012_video.mp4
Write-Host "=== mux video + audio_final.m4a -> v012.mp4 ==="
ffmpeg -y -v warning -i v012_video.mp4 -i audio_final.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest v012.mp4
Write-Host "=== MUX_EXIT=$LASTEXITCODE ==="
Get-Item v012.mp4 -ErrorAction SilentlyContinue | Select-Object Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 120 | Write-Host
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of default=noprint_wrappers=1 v012.mp4
Write-Host "=== extract QC frames (inside every label window) ==="
ffmpeg -y -v error -ss 1 -i v012.mp4 -frames:v 1 qc_f01.png
ffmpeg -y -v error -ss 10 -i v012.mp4 -frames:v 1 qc_f10.png
ffmpeg -y -v error -ss 21 -i v012.mp4 -frames:v 1 qc_f21.png
ffmpeg -y -v error -ss 25.5 -i v012.mp4 -frames:v 1 qc_f25.png
ffmpeg -y -v error -ss 32 -i v012.mp4 -frames:v 1 qc_f32.png
ffmpeg -y -v error -ss 42 -i v012.mp4 -frames:v 1 qc_f42.png
ffmpeg -y -v error -ss 51 -i v012.mp4 -frames:v 1 qc_f51.png
Write-Host "=== v012 render end: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Stop-Transcript
