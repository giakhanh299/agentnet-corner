# V014 audio mix on the PC - voice (VieNeu Mai Anh, atempo 0.66, 52.09s) +
# bgm_upbeat + SFX, loudnorm 2-pass to -16 LUFS. Runs in C:\Users\w\v014_render.
# SFX times = actual voice boundaries (v014_voice_timing.json):
# whoosh at 6.20s (beat 1 start); ding at each step number word:
# 17.70s (step 1 "Mot"), 22.30s (step 2 "Hai"), 23.90s (step 3 "Ba"),
# 27.60s (step 4 "Bon"); pop at 43.48s (payoff card).
# Lessons applied: NO apad, amix duration=longest; alimiter level=false;
# output forced -ac 2 -ar 48000. ffmpeg 8.1 loudnorm JSON has NO "linear"
# key: map dynamic -> linear=false, linear -> true.
$ErrorActionPreference = "Continue"
Set-Location C:\Users\w\v014_render
Start-Transcript -Path "C:\Users\w\v014_mix.log" -Force
Write-Host "=== V014 MIX start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="

Write-Host "--- step 1: mix voice + bgm + sfx -> mix_raw.wav ---"
ffmpeg -y -v warning -i voice.wav -i bgm_upbeat.ogg -i ding.ogg -i whoosh.ogg -i pop.ogg -filter_complex "[0:a]aresample=48000[voice];[1:a]atrim=0:52.09,asetpts=PTS-STARTPTS,volume=0.12,afade=t=out:st=50.09:d=2[bgm];[2:a]adelay=17700,volume=0.5[ding1];[2:a]adelay=22300,volume=0.5[ding2];[2:a]adelay=23900,volume=0.5[ding3];[2:a]adelay=27600,volume=0.5[ding4];[3:a]adelay=6200,volume=0.5[whoosh];[4:a]adelay=43480,volume=0.5[pop];[voice][bgm][ding1][ding2][ding3][ding4][whoosh][pop]amix=inputs=8:duration=longest:normalize=0[mix]" -map "[mix]" -ac 2 -ar 48000 mix_raw.wav
Write-Host "MIX_EXIT=$LASTEXITCODE"
Get-Item mix_raw.wav | Select-Object Length | Format-Table -AutoSize | Out-String -Width 120 | Write-Host

Write-Host "--- step 2: loudnorm pass 1 (measure) ---"
ffmpeg -y -v info -i mix_raw.wav -vn -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null - 2> loudnorm1.log
Write-Host "LN1_EXIT=$LASTEXITCODE"
$log = Get-Content loudnorm1.log -Raw
$start = $log.IndexOf("{")
$end = $log.LastIndexOf("}")
if ($start -lt 0 -or $end -lt $start) { Write-Host "LOUDNORM JSON NOT FOUND"; Get-Content loudnorm1.log | Select-Object -Last 30 | Write-Host; throw "loudnorm pass 1 failed" }
$json = $log.Substring($start, $end - $start + 1) | ConvertFrom-Json
Write-Host "measured_I=$($json.input_i) measured_TP=$($json.input_tp) measured_LRA=$($json.input_lra) measured_thresh=$($json.input_thresh) target_offset=$($json.target_offset) norm_type=$($json.normalization_type)"
$linear = "false"
if ($json.normalization_type -eq "linear") { $linear = "true" }
Write-Host "linear=$linear"

Write-Host "--- step 3: loudnorm pass 2 + alimiter -> audio_final.m4a ---"
$ln2 = "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=$($json.input_i):measured_TP=$($json.input_tp):measured_LRA=$($json.input_lra):measured_thresh=$($json.input_thresh):offset=$($json.target_offset):linear=$($linear):print_format=json,alimiter=limit=0.7:level=false"
ffmpeg -y -v warning -i mix_raw.wav -af $ln2 -c:a aac -b:a 192k -ac 2 -ar 48000 audio_final.m4a 2> loudnorm2.log
Write-Host "LN2_EXIT=$LASTEXITCODE"

Write-Host "--- step 4: verify final loudness ---"
ffmpeg -y -v info -i audio_final.m4a -vn -af "loudnorm=print_format=json" -f null - 2> loudnorm_verify.log
$logv = Get-Content loudnorm_verify.log -Raw
$sv = $logv.IndexOf("{"); $ev = $logv.LastIndexOf("}")
if ($sv -ge 0 -and $ev -gt $sv) {
  $jv = $logv.Substring($sv, $ev - $sv + 1) | ConvertFrom-Json
  Write-Host "FINAL input_i=$($jv.input_i) input_tp=$($jv.input_tp) input_lra=$($jv.input_lra)"
}
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,sample_rate,channels -of default=noprint_wrappers=1 audio_final.m4a
Write-Host "=== V014 MIX end: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Stop-Transcript
