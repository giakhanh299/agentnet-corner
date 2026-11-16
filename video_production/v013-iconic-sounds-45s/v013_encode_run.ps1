$ErrorActionPreference = "Continue"
Start-Transcript -Path "C:\Users\w\v013_render.log" -Force
Set-Location "C:\Users\w\v013_render"
$Start = Get-Date
Write-Host "=== V013 ENCODE: 7 cards + zoompan/xfade + captions.ass + audio mux ==="
Write-Host "Hard cap: -frames:v 1373 (45.75s x 30fps). NO -loop 1 (runaway lesson from v003)."
ffmpeg -y -i cards\stage_hook.png -i cards\stage_n5.png -i cards\stage_n4.png -i cards\stage_n3.png -i cards\stage_n2.png -i cards\stage_n1.png -i cards\stage_end.png -i audio_final.m4a -filter_complex_script assemble_filter_pc.txt -map "[vout]" -map 7:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 -frames:v 1373 -c:a copy -movflags +faststart v013.mp4
Write-Host "FFMPEG_EXIT=$LASTEXITCODE"
$End = Get-Date
Write-Host "encode took $([math]::Round(($End - $Start).TotalSeconds, 1)) s"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,bit_rate -show_entries format=duration,size -of default=noprint_wrappers=1 v013.mp4
Write-Host "=== DONE ==="
Stop-Transcript
