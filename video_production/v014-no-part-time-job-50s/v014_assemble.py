"""Assemble V014 voice on the PC (.venv-ai python + ffmpeg).

- Takes per-unit native 48k wavs (b3a replaced by the passing take2 probe).
- Trims leading/trailing near-silence per unit (v010 lesson: trim BEFORE
  building captions/SFX timings so voice starts at ~0s).
- Slows each unit with ffmpeg atempo=0.69 (native 224 wpm -> ~155 wpm;
  0.65 would give 146 wpm, below the 150-165 zone, and 55.8s total).
- Assembles slowed units + exact pauses (0.3/0.4/0.6s) -> voice.wav 48k.
- Saves voice_16k.wav (mono 16k, for the faster-whisper final check) and
  v014_voice_timing.json (unit start/end in the final voice).
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import soundfile as sf

INDIR = r"C:\Users\w\agentnet-corner\ai-stack\v014_tts"
OUTDIR = r"C:\Users\w\v014_render"
os.makedirs(OUTDIR, exist_ok=True)
SR = 48000
ATEMPO = 0.69
THRESH = 0.01
KEEP_S = 0.01

# (unit, source wav, pause_after_s) — pauses applied after slowing.
UNITS = [
    ("hook", "v014_unit_hook_native48k.wav", 0.3),
    ("b1", "v014_unit_b1_native48k.wav", 0.4),
    ("b2a", "v014_unit_b2a_native48k.wav", 0.3),
    ("b2b", "v014_unit_b2b_native48k.wav", 0.3),
    ("b2c", "v014_unit_b2c_native48k.wav", 0.4),
    ("b3a", "v014_giau_take2_48k.wav", 0.3),
    ("b3b", "v014_unit_b3b_native48k.wav", 0.6),
    ("payoff", "v014_unit_payoff_native48k.wav", 0.0),
]

with open(os.path.join(INDIR, "v014_units.json"), encoding="utf-8") as f:
    META = {u["unit"]: u for u in json.load(f)}

def trim_silence(audio, sr):
    """Trim leading/trailing near-silence; keep KEEP_S at each edge."""
    idx = np.where(np.abs(audio) > THRESH)[0]
    if len(idx) == 0:
        return audio, 0.0, 0.0
    start = max(0, idx[0] - int(KEEP_S * sr))
    end = min(len(audio), idx[-1] + int(KEEP_S * sr) + 1)
    lead_trim = start / sr
    trail_trim = (len(audio) - end) / sr
    return audio[start:end], lead_trim, trail_trim

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("CMD FAILED:", " ".join(cmd), flush=True)
        print(r.stdout[-2000:], flush=True)
        print(r.stderr[-2000:], flush=True)
        raise SystemExit(1)

timing = []
parts = []
t_cur = 0.0
speech_s = 0.0
total_words = 0
for name, fname, pause_after in UNITS:
    src = os.path.join(INDIR, fname)
    audio, sr = sf.read(src, dtype="float32")
    assert sr == SR
    trimmed, lead_trim, trail_trim = trim_silence(audio, sr)
    words = META[name]["words"] if name in META else len(META.get(name, {}).get("text", "").split())
    if name == "b3a":
        words = 5
    total_words += words
    native_dur = len(trimmed) / SR
    trim_path = os.path.join(OUTDIR, f"v014_{name}_trim48k.wav")
    sf.write(trim_path, trimmed, SR)
    slow_path = os.path.join(OUTDIR, f"v014_{name}_slow48k.wav")
    run(["ffmpeg", "-y", "-v", "error", "-i", trim_path,
         "-af", f"atempo={ATEMPO}", slow_path])
    slow, sr2 = sf.read(slow_path, dtype="float32")
    slow_dur = len(slow) / SR
    speech_s += slow_dur
    wpm = words / slow_dur * 60
    print(f"{name}: native {native_dur:.2f}s (lead trim {lead_trim:.3f}s, trail trim {trail_trim:.3f}s) "
          f"-> slowed {slow_dur:.2f}s, {words} words, {wpm:.0f} wpm", flush=True)
    timing.append({"unit": name, "text": META[name]["text"] if name in META else "Không hứa bạn giàu nhanh.",
                   "start": round(t_cur, 3), "end": round(t_cur + slow_dur, 3),
                   "words": words, "pause_after": pause_after})
    parts.append(slow)
    t_cur += slow_dur
    if pause_after > 0:
        parts.append(np.zeros(int(pause_after * SR), dtype=np.float32))
        t_cur += pause_after

full = np.concatenate(parts)
sf.write(os.path.join(OUTDIR, "voice.wav"), full, SR)
run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(OUTDIR, "voice.wav"),
     "-ar", "16000", "-ac", "1", os.path.join(OUTDIR, "voice_16k.wav")])
total_dur = len(full) / SR
print(f"voice.wav: {total_dur:.2f}s total, speech {speech_s:.2f}s, {total_words} words", flush=True)
print(f"Speech-only: {total_words / speech_s * 60:.1f} wpm; overall: {total_words / total_dur * 60:.1f} wpm", flush=True)
print(f"Voice onset: first unit starts at {timing[0]['start']:.3f}s", flush=True)
with open(os.path.join(OUTDIR, "v014_voice_timing.json"), "w", encoding="utf-8") as f:
    json.dump({"atempo": ATEMPO, "total_dur": round(total_dur, 3),
               "speech_s": round(speech_s, 3), "words": total_words,
               "units": timing}, f, ensure_ascii=False, indent=2)
print("V014_ASSEMBLE_DONE")
