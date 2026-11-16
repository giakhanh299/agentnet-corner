#!/bin/bash
# v008 assemble — Manim raw video (PC render) + MMS voice + bgm_calm envelope
# + door_knock/pop + captions. Proven recipe (v001/Ep001/v002/v004):
# mix -> loudnorm I=-16 TP=-1.5 -> alimiter limit=0.7:level=false
# (level=true is auto-gain, WRONG). No apad (hangs with amix
# duration=first); amix uses duration=longest. Final mux uses -shortest
# (voice 48.36s < raw video 49.40s).
# Voice was TRIMMED 0.36s at the head (MMS emitted a 0.41s leading pad;
# voice now starts ~0.05s). All times below are the TRIMMED timeline
# (timing.json; original PC timings in timing_pc.json). The raw video is
# also trimmed 0.36s at the mux step (-ss before -i) so visuals stay in
# sync with the voice.
# Beat boundaries (trimmed voice):
#   hook 0-4.436 / beat1 4.436-14.234 / beat2 14.234-24.342 /
#   beat3 24.342-35.14 (0.6s pre-payoff silence 34.54-35.14) /
#   payoff 35.14-44.826 / cta 44.826-48.362
set -euo pipefail
cd "$(dirname "$0")"

SFX="../../stickman-shorts/src/assets/audio"

# 1) audio mix -> mix.wav
#    BGM envelope (relative to voice): hook 0.11 / beat1 0.11 / beat2 0.12 /
#    beat3 0.18 (swell as dad comes home) / 0.0 during the 0.6s pre-payoff
#    silence (34.54-35.14) / payoff 0.11 / cta 0.11 -> BGM ~20-24 dB below voice.
#    door_knock (0.4) at 24.342 (dad arrives). pop (0.35) at 35.14 (the hug).
ffmpeg -y -v error \
  -i voice.wav \
  -i "$SFX/music/bgm_calm.ogg" \
  -i "$SFX/sfx/door_knock.ogg" \
  -i "$SFX/sfx/pop.ogg" \
  -filter_complex "[0:a]aformat=sample_rates=48000:channel_layouts=stereo[voice];[1:a]volume='if(between(t,0,4.436),0.11,if(between(t,4.436,14.234),0.11,if(between(t,14.234,24.342),0.12,if(between(t,24.342,34.54),0.18,if(between(t,34.54,35.14),0.0,0.11)))))':eval=frame,atrim=0:48.362,aformat=sample_rates=48000:channel_layouts=stereo[bgm];[2:a]adelay=24342:all=1,volume=0.4,aformat=sample_rates=48000:channel_layouts=stereo[knock];[3:a]adelay=35140:all=1,volume=0.35,aformat=sample_rates=48000:channel_layouts=stereo[pop];[voice][bgm][knock][pop]amix=inputs=4:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.7:level=false[mix]" \
  -map "[mix]" -ar 48000 mix.wav

# 2) mux video + mix + captions -> v008.mp4
ffmpeg -y -v error -ss 0.36 -i raw.mp4 -i mix.wav \
  -filter_complex "[0:v]ass=captions.ass[vout]" \
  -map "[vout]" -map 1:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -shortest -movflags +faststart v008.mp4

echo "ASSEMBLE_OK"
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate,codec_name -of default=noprint_wrappers=1 v008.mp4
