#!/bin/bash
# V005 audio mix: voice_norm + bgm_comedy + SFX, then two-pass loudnorm.
# SFX placement (ms) from unit timings: reveals 3480/11320/19640/28500/37680;
# riser 34600-37680 (into #1); victory LIGHT 37680 (trimmed 1.5s, vol 0.35);
# laugh after #4 punchline 19300 (#2's laugh SKIPPED: it would collide with
# the riser + #1 reveal — the #1 build-up is protected); ding at CTA 45870.
# whoosh+pop at 100ms. BGM vol 0.12, fade out last 2s.
# amix normalize=0 (no auto-normalize); loudnorm pass after.
set -e
cd "$(dirname "$0")"
A=../../stickman-shorts/src/assets/audio
ffmpeg -v error -y \
  -i voice_norm.wav \
  -i "$A/music/bgm_comedy.ogg" \
  -i "$A/sfx/whoosh.ogg" \
  -i "$A/sfx/pop.ogg" \
  -i "$A/sfx/ding.ogg" \
  -i "$A/sfx/riser.ogg" \
  -i "$A/sfx/victory.ogg" \
  -i "$A/sfx/laugh.ogg" \
  -filter_complex "\
[0:a]anull[voice];\
[1:a]atrim=0:49.95,afade=t=out:st=47.95:d=2,volume=0.12[bgm];\
[2:a]adelay=100|100,volume=0.8[w];\
[3:a]adelay=100|100,volume=0.8[p0];\
[3:a]adelay=3480|3480,volume=0.8[p5];\
[3:a]adelay=11320|11320,volume=0.8[p4];\
[3:a]adelay=19640|19640,volume=0.8[p3];\
[3:a]adelay=28500|28500,volume=0.8[p2];\
[3:a]adelay=37680|37680,volume=0.8[p1];\
[5:a]adelay=34600|34600,volume=0.6[ris];\
[6:a]atrim=0:1.5,adelay=37680|37680,volume=0.35[vic];\
[7:a]adelay=19300|19300,volume=0.5[lau];\
[4:a]adelay=45870|45870,volume=0.8[din];\
[voice][bgm][w][p0][p5][p4][p3][p2][p1][ris][vic][lau][din]amix=inputs=13:duration=longest:normalize=0[mix]" \
  -map "[mix]" -c:a pcm_s16le mix_raw.wav
echo "mix_raw done"
ffmpeg -hide_banner -i mix_raw.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/Parsed_loudnorm/,/}/p' | grep -E "input_i|input_tp|input_lra|input_thresh|target_offset"
