#!/usr/bin/env python3
"""V012 audio mix on the PC: VieNeu voice + bgm_comedy + SFX, two-pass loudnorm.

Runs on the PC with plain Python 3.12.10 (no special packages; shells out
to ffmpeg). Adapted from v009_mix.py.

SFX placement (ms) from measured VieNeu unit timings (run 3):
pop 4050 (beat1 label "165 tu"), door_knock 17960 (beat2 start, owner
leaves), pop 38020 + victory 38020 (beat3 "DI DAO"). BGM vol 0.12,
fade out last 2s. amix normalize=0 (no auto-normalize); loudnorm pass
after. Pass 2 uses measured_* from pass 1 + linear=true (ffmpeg 8.1
pass-1 JSON has no "linear" key - v006 lesson), then
alimiter=limit=0.7:level=false (level=true is auto-gain, NOT true-peak
mode - v001 lesson).
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

VOICE = r"C:\Users\w\agentnet-corner\ai-stack\v012\v012_voice.wav"
A = r"C:\Users\w\agentnet-corner\stickman-shorts\src\assets\audio"
OUTDIR = r"C:\Users\w\v012_render"
MIX_RAW = OUTDIR + r"\mix_raw.wav"
FINAL = OUTDIR + r"\audio_final.m4a"
TOTAL = 55.47  # voice duration (s)

FC = (
    "[0:a]aresample=48000,aformat=channel_layouts=stereo[voice];"
    f"[1:a]atrim=0:{TOTAL},afade=t=out:st={TOTAL - 2:.2f}:d=2,volume=0.12[bgm];"
    "[2:a]adelay=4050|4050,volume=0.8[p1];"
    "[3:a]adelay=17960|17960,volume=0.8[knock];"
    "[2:a]adelay=38020|38020,volume=0.8[p2];"
    "[4:a]adelay=38020|38020,volume=0.8[vic];"
    "[voice][bgm][p1][knock][p2][vic]"
    "amix=inputs=6:duration=longest:normalize=0[mix]"
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
     "-i", A + r"\music\bgm_comedy.ogg",
     "-i", A + r"\sfx\pop.ogg",
     "-i", A + r"\sfx\door_knock.ogg",
     "-i", A + r"\sfx\victory.ogg",
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
