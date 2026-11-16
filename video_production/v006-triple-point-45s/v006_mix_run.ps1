# V006 audio mix on the PC — voice + bgm_calm + SFX, loudnorm 2-pass to -16 LUFS.
# Runs in C:\Users\w\v006_render. Voice is v006_voice.wav (run 3, accepted
# take: 53.14s). BGM + SFX copied from the VPS Core_SFX library.
# Lessons applied: NO apad (infinite), amix duration=longest; alimiter
# level=false (level=true is auto-gain); output forced -ac 2 -ar 48000
# (v003's first mix came out AAC 96 kHz mono).
# NOTE: $ErrorActionPreference must be "Continue" here, NOT "Stop":
# ffmpeg prints its banner + progress to stderr, and PowerShell treats
# native-command stderr as an error stream that "Stop" turns into a
# terminating NativeCommandError (killed the loudnorm pass-1 step once).
$ErrorActionPreference = "Continue"
Set-Location C:\Users\w\v006_render
Start-Transcript -Path "C:\Users\w\v006_mix.log" -Force
Write-Host "=== V006 MIX start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Copy-Item -Force "C:\Users\w\agentnet-corner\ai-stack\v006\v006_voice.wav" ".\v006_voice.wav"

Write-Host "--- step 1: mix voice + bgm + sfx -> mix_raw.wav ---"
ffmpeg -y -v warning -i v006_voice.wav -i bgm_calm.ogg -i ding.ogg -i whoosh.ogg -i pop.ogg -filter_complex "[0:a]aresample=48000[voice];[1:a]atrim=0:53.14,asetpts=PTS-STARTPTS,volume=0.12,afade=t=out:st=51.14:d=2[bgm];[2:a]adelay=4330,volume=0.5[ding1];[2:a]adelay=27820,volume=0.5[ding2];[3:a]adelay=14350,volume=0.5[whoosh];[4:a]adelay=44760,volume=0.5[pop];[voice][bgm][ding1][ding2][whoosh][pop]amix=inputs=6:duration=longest:normalize=0[mix]" -map "[mix]" -ac 2 -ar 48000 mix_raw.wav
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
Write-Host "measured_I=$($json.input_i) measured_TP=$($json.input_tp) measured_LRA=$($json.input_lra) measured_thresh=$($json.input_thresh) target_offset=$($json.target_offset) linear=$($json.linear)"

Write-Host "--- step 3: loudnorm pass 2 + alimiter -> audio_final.m4a ---"
$ln2 = "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=$($json.input_i):measured_TP=$($json.input_tp):measured_LRA=$($json.input_lra):measured_thresh=$($json.input_thresh):offset=$($json.target_offset):linear=$($json.linear):print_format=json,alimiter=limit=0.7:level=false"
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
Write-Host "=== V006 MIX end: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
Stop-Transcript
