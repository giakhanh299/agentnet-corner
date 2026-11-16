#!/bin/bash
# V007 audio mix: voice_norm + bgm_comedy + SFX, then two-pass loudnorm.
# SFX placement (ms) from unit timings: reveals 6060/14980/22040/29570/36470;
# riser 33470-36470 (into #1, file 3.08s); ding at #1 reveal 36470;
# victory LIGHT 40130 (n1b start, trimmed 1.5s, vol 0.35 — script: #1 is
# the payoff, victory sting light, do not drown the voice); whoosh+pop
# at 100ms. BGM vol 0.12, fade out last 2s. No laugh (script does not
# call for one). amix normalize=0 (no auto-normalize); loudnorm pass after.
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
  -filter_complex "\
[0:a]anull[voice];\
[1:a]atrim=0:48.40,afade=t=out:st=46.40:d=2,volume=0.12[bgm];\
[2:a]adelay=100|100,volume=0.8[w];\
[3:a]adelay=100|100,volume=0.8[p0];\
[3:a]adelay=6060|6060,volume=0.8[p5];\
[3:a]adelay=14980|14980,volume=0.8[p4];\
[3:a]adelay=22040|22040,volume=0.8[p3];\
[3:a]adelay=29570|29570,volume=0.8[p2];\
[3:a]adelay=36470|36470,volume=0.8[p1];\
[5:a]adelay=33470|33470,volume=0.6[ris];\
[6:a]atrim=0:1.5,adelay=40130|40130,volume=0.35[vic];\
[4:a]adelay=36470|36470,volume=0.8[din];\
[voice][bgm][w][p0][p5][p4][p3][p2][p1][ris][vic][din]amix=inputs=12:duration=longest:normalize=0[mix]" \
  -map "[mix]" -c:a pcm_s16le mix_raw.wav
echo "mix_raw done"
ffmpeg -hide_banner -i mix_raw.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/Parsed_loudnorm/,/}/p' | grep -E "input_i|input_tp|input_lra|input_thresh|target_offset"
