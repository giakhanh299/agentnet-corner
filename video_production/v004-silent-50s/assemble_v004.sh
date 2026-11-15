#!/bin/bash
# v004 assemble — Manim raw video + MMS voice + bgm_calm envelope + ding/swoosh + captions
# Proven recipe (v001/Ep001/v002): mix -> loudnorm I=-16 TP=-1.5 -> alimiter
# limit=0.7:level=false (level=true is auto-gain, WRONG). No apad (hangs with
# amix duration=first); amix uses duration=longest. Final mux uses -shortest
# (voice 52.36s < raw video 53.03s).
set -euo pipefail
cd "$(dirname "$0")"

RAW="../../stickman-shorts/media/videos/scene/1920p30/StickmanScene.mp4"
SFX="../../stickman-shorts/src/assets/audio"

# 1) audio mix -> mix.wav
#    voice: raw -18.50 LUFS (measured). BGM envelope (relative to voice):
#    hook 0.11 / beat1 0.11 / beat2 0.12 / beat3 0.18 (swell) / 0.0 during the
#    0.5s pre-payoff silence (45.52-46.03) / payoff 0.11  -> BGM ~20-24 dB
#    below voice. Ding (0.5) at 30.69 (girl appears). Swoosh (0.2) at the
#    three beat transitions 3.58 / 17.22 / 30.69 — the swoosh file peaks at
#    -3.7 dB raw, so 0.4 hit the alimiter ceiling (-3.1 dB); 0.2 lands it
#    just below the voice peak.
ffmpeg -y -v error \
  -i voice.wav \
  -i "$SFX/music/bgm_calm.ogg" \
  -i "$SFX/sfx/ding.ogg" \
  -i "$SFX/sfx/transition_swoosh.ogg" \
  -filter_complex "[0:a]aformat=sample_rates=48000:channel_layouts=stereo[voice];[1:a]volume='if(between(t,0,3.58),0.11,if(between(t,3.58,17.22),0.11,if(between(t,17.22,30.69),0.12,if(between(t,30.69,45.52),0.18,if(between(t,45.52,46.03),0.0,0.11)))))':eval=frame,atrim=0:52.36,aformat=sample_rates=48000:channel_layouts=stereo[bgm];[2:a]adelay=30690:all=1,volume=0.5,aformat=sample_rates=48000:channel_layouts=stereo[ding];[3:a]asplit=3[sw0][sw1][sw2];[sw0]adelay=3580:all=1,volume=0.2,aformat=sample_rates=48000:channel_layouts=stereo[s1];[sw1]adelay=17220:all=1,volume=0.2,aformat=sample_rates=48000:channel_layouts=stereo[s2];[sw2]adelay=30690:all=1,volume=0.2,aformat=sample_rates=48000:channel_layouts=stereo[s3];[voice][bgm][ding][s1][s2][s3]amix=inputs=6:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.7:level=false[mix]" \
  -map "[mix]" -ar 48000 mix.wav

# 2) mux video + mix + captions -> v004.mp4
ffmpeg -y -v error -i "$RAW" -i mix.wav \
  -filter_complex "[0:v]ass=captions.ass[vout]" \
  -map "[vout]" -map 1:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -shortest -movflags +faststart v004.mp4

echo "ASSEMBLE_OK"
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate,codec_name -of default=noprint_wrappers=1 v004.mp4
