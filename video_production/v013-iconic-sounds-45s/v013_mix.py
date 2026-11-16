#!/usr/bin/env python3
"""V013 audio mix on the PC: VieNeu voice + bgm_upbeat + 5 sound samples
+ SFX, two-pass loudnorm. Runs on the PC with plain Python 3.12.10
(shells out to ffmpeg). Adapted from v009_mix.py.

Voice: VieNeu "Mai Anh" slowed atempo 0.70, 45.75s total, 116 words,
161 wpm speech-only (v013_units.json timings).
Sample/SFX placement (ms) from unit timings:
  ding at unit starts: 7650 / 13180 / 19170 / 24690 / 33530
  pop at payoff: 41540; whoosh at 100ms (hook energy, v009 pattern)
  bell 9650 (n5+2.0s, 2s) | motorbike 15180 (n4+2.0s, 2s)
  vendor call 21170 (n3+2.0s, 1.2s) | ringtone 27190 (n2+2.5s, 3s)
  modem 35530 (n1+2.0s, 3s)
Levels: BGM vol 0.12; samples vol 0.12 (~-19 dB below voice, inside the
-18 to -24 dB task target). NOTE — script says samples at voice level
("am thanh mau phat o muc ngang giong"); the task instruction overrides
it to -18..-24 dB below voice. If the parent wants the script's level,
change sample volumes to 1.0 here.
amix normalize=0; loudnorm pass after. Pass 2 uses measured_* from
pass 1 + linear=true (ffmpeg 8.1 pass-1 JSON has no "linear" key),
then alimiter=limit=0.7:level=false.
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

R = r"C:\Users\w\v013_render"
VOICE = R + r"\voice.wav"
SND = R + r"\sounds"
A = r"C:\Users\w\agentnet-corner\stickman-shorts\src\assets\audio"
MIX_RAW = R + r"\mix_raw.wav"
FINAL = R + r"\audio_final.m4a"
TOTAL = 45.75  # voice duration (s)

FC = (
    "[0:a]aresample=48000,aformat=channel_layouts=stereo[voice];"
    f"[1:a]atrim=0:{TOTAL},afade=t=out:st={TOTAL - 2:.2f}:d=2,volume=0.12[bgm];"
    "[2:a]adelay=100|100,volume=0.8[w];"
    "[3:a]adelay=100|100,volume=0.8[p0];"
    "[3:a]adelay=41540|41540,volume=0.8[pcta];"
    "[4:a]adelay=7650|7650,volume=0.8[d5];"
    "[4:a]adelay=13180|13180,volume=0.8[d4];"
    "[4:a]adelay=19170|19170,volume=0.8[d3];"
    "[4:a]adelay=24690|24690,volume=0.8[d2];"
    "[4:a]adelay=33530|33530,volume=0.8[d1];"
    "[5:a]adelay=9650|9650,volume=0.12[bell];"
    "[6:a]adelay=15180|15180,volume=0.12[bike];"
    "[7:a]adelay=21170|21170,volume=0.12[vendor];"
    "[8:a]adelay=27190|27190,volume=0.12[ring];"
    "[9:a]adelay=35530|35530,volume=0.12[modem];"
    "[voice][bgm][w][p0][pcta][d5][d4][d3][d2][d1]"
    "[bell][bike][vendor][ring][modem]"
    "amix=inputs=15:duration=longest:normalize=0[mix]"
)

def run(cmd, **kw):
    print("+ " + " ".join(cmd), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f"FAILED rc={r.returncode}: {' '.join(cmd[:3])}")
    return r

run(["ffmpeg", "-v", "error", "-y",
     "-i", VOICE,
     "-i", A + r"\music\bgm_upbeat.ogg",
     "-i", A + r"\sfx\whoosh.ogg",
     "-i", A + r"\sfx\pop.ogg",
     "-i", A + r"\sfx\ding.ogg",
     "-i", SND + r"\sample_bell.wav",
     "-i", SND + r"\sample_motorbike.wav",
     "-i", SND + r"\sample_vendor.wav",
     "-i", SND + r"\sample_ringtone.wav",
     "-i", SND + r"\sample_modem.wav",
     "-filter_complex", FC,
     "-map", "[mix]", "-c:a", "pcm_s16le", MIX_RAW])
print("mix_raw done", flush=True)

# --- loudnorm pass 1 (measure) ---
r = run(["ffmpeg", "-hide_banner", "-i", MIX_RAW,
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
         "-f", "null", "-"])
m = re.search(r"\{[^}]*\"input_i\"[^}]*\}", r.stderr, re.S)
if not m:
    print(r.stderr[-3000:], file=sys.stderr)
    raise SystemExit("loudnorm pass-1 JSON not found")
meas = json.loads(m.group(0))
print("pass1 measured:", {k: meas.get(k) for k in
      ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")}, flush=True)

# --- loudnorm pass 2 (apply) + true-peak limiter ---
af = (
    "loudnorm=I=-16:TP=-1.5:LRA=11"
    f":measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
    f":measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}"
    f":offset={meas['target_offset']}:linear=true"
    ",alimiter=limit=0.7:level=false"
)
run(["ffmpeg", "-v", "error", "-y", "-i", MIX_RAW,
     "-af", af, "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", FINAL])
print("audio_final done", flush=True)

# --- verify the final file ---
r = run(["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size", "-show_entries",
         "stream=codec_name,sample_rate,channels,bit_rate",
         "-of", "default=noprint_wrappers=1", FINAL])
print(r.stdout, flush=True)
r = run(["ffmpeg", "-hide_banner", "-i", FINAL,
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
         "-f", "null", "-"])
m = re.search(r"\{[^}]*\"input_i\"[^}]*\}", r.stderr, re.S)
if m:
    v = json.loads(m.group(0))
    print(f"FINAL loudness: {v.get('input_i')} LUFS, TP {v.get('input_tp')} dBTP, LRA {v.get('input_lra')}", flush=True)
print("MIX DONE", flush=True)
