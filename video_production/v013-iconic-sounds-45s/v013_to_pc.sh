#!/usr/bin/env bash
# V013 -> PC transfer + run. RUN BY THE PARENT AGENT (this subagent session
# cannot open raw TCP to the tunnel proxy: other_tcp=Deny).
# 1) Creates C:\Users\w\v013_render (+sounds, +cards) on the PC.
# 2) scp's every file ONE PER CALL (v009 lesson: 2 files to a file-path
#    destination creates a directory named after the file).
# 3) Runs the mix, then the encode, then copies v013.mp4 back.
# Usage: bash v013_to_pc.sh  (from the v013 output dir)
set -u
BASE="$HOME/workspace/agentnet-corner/video_production/v013-iconic-sounds-45s"
PC="w@100.101.158.71"
PROXY_HOST=$(echo "$HTTPS_PROXY" | sed -E 's#https?://([^:/@]+@)?([^:/]+).*#\2#')
SSH_OPTS=(-i "$HOME/.ssh/pc_torque" -o "ProxyCommand=nc -X connect -x ${PROXY_HOST}:3130 %h %p" -o BatchMode=yes)

run_ps1() { # $1 = C:\ path of a .ps1 already on the PC
  ssh "${SSH_OPTS[@]}" "$PC" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$1" "<" NUL
}

echo "== mkdir on PC =="
scp "${SSH_OPTS[@]}" "$BASE/v013_mkdir.ps1" "$PC:C:/Users/w/v013_mkdir.ps1"
run_ps1 'C:\Users\w\v013_mkdir.ps1'

echo "== scp voice + captions + filter =="
scp "${SSH_OPTS[@]}" "$BASE/voice.wav" "$PC:C:/Users/w/v013_render/voice.wav"
scp "${SSH_OPTS[@]}" "$BASE/captions.ass" "$PC:C:/Users/w/v013_render/captions.ass"
scp "${SSH_OPTS[@]}" "$BASE/assemble_filter_pc.txt" "$PC:C:/Users/w/v013_render/assemble_filter_pc.txt"

echo "== scp 5 samples =="
for s in sample_bell sample_motorbike sample_vendor sample_ringtone sample_modem; do
  scp "${SSH_OPTS[@]}" "$BASE/sounds/$s.wav" "$PC:C:/Users/w/v013_render/sounds/$s.wav"
done

echo "== scp 7 cards =="
for c in stage_hook stage_n5 stage_n4 stage_n3 stage_n2 stage_n1 stage_end; do
  scp "${SSH_OPTS[@]}" "$BASE/cards/$c.png" "$PC:C:/Users/w/v013_render/cards/$c.png"
done

echo "== scp mix/encode scripts =="
scp "${SSH_OPTS[@]}" "$BASE/v013_mix.py" "$PC:C:/Users/w/v013_mix.py"
scp "${SSH_OPTS[@]}" "$BASE/v013_mix_run.ps1" "$PC:C:/Users/w/v013_mix_run.ps1"
scp "${SSH_OPTS[@]}" "$BASE/v013_encode_run.ps1" "$PC:C:/Users/w/v013_encode_run.ps1"

echo "== run mix on PC =="
run_ps1 'C:\Users\w\v013_mix_run.ps1'
echo "== run encode on PC =="
run_ps1 'C:\Users\w\v013_encode_run.ps1'

echo "== copy v013.mp4 back =="
scp "${SSH_OPTS[@]}" "$PC:C:/Users/w/v013_render/v013.mp4" "$BASE/v013.mp4"
scp "${SSH_OPTS[@]}" "$PC:C:/Users/w/v013_render/audio_final.m4a" "$BASE/audio_final.m4a"
ls -la "$BASE/v013.mp4" "$BASE/audio_final.m4a"
echo "TRANSFER+DONE"
