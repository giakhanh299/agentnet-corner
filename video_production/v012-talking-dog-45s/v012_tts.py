"""V012 full voice - VieNeu-TTS v3 Turbo, preset "Mai Anh", on the PC.

NEW production voice (user decision 2026-11-16 ~20:39). Recipe from
voice-compare-20261116/vieneu_test.py: SDK Vieneu().infer(text,
voice="Mai Anh"), 48 kHz output, native ~238 wpm. Slow with ffmpeg
atempo=0.65 on the WHOLE assembled track (exactly like the approved
vieneu_slow.wav sample) -> ~155 wpm. Pause scheme (native): 0.3s after
hook, 0.4s between clauses/beats, 0.6s before payoff (stretched x1.538
by atempo, same as the approved sample).

PROBE RESULTS (2026-11-16, PC, VieNeu Mai Anh + faster-whisper large-v3):
- hook 100%, "Bin" 100%, "om dien thoai" 100%, "di dao" 100% - ALL KEPT.
- "mot tram sau muoi lam": Whisper heard "165" (8/13) - Whisper number
  normalisation, same artefact as v009/v011 ("200 met", "60%"). The
  words are spoken; NO swap. Full-track Whisper check below is the
  real verdict (target >= 75% on the slowed voice).

Script (121 words, 5 beats) from
scripts-batch-20261116/script_v012-talking-dog-45s.md. No swaps.
Captions use the script text as spoken.

Pipeline: synth clauses (native) -> assemble with pauses -> atempo 0.65
-> measure + TRIM leading silence in the slowed wav BEFORE timings are
frozen (v010 lesson) -> save voice.wav (48 kHz mono) + voice_16k.wav
(for the Whisper check) + v012_units.json (slowed timings).
"""
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import soundfile as sf

from vieneu import Vieneu

VOICE = "Mai Anh"
SR = 48000
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v012"
NATIVE_OUT = os.path.join(OUTDIR, "v012_voice_native.wav")
SLOWED_OUT = os.path.join(OUTDIR, "v012_voice_slow48k.wav")
OUT = os.path.join(OUTDIR, "v012_voice.wav")
OUT16K = os.path.join(OUTDIR, "v012_voice_16k.wav")
UNITS_OUT = os.path.join(OUTDIR, "v012_units.json")

# (beat name, [clauses], gap_after_s)
BEATS = [
    ("hook", ["Ch\u00f3 nh\u00e0 b\u1ea1n hi\u1ec3u \u0111\u01b0\u1ee3c bao nhi\u00eau t\u1eeb c\u1ee7a b\u1ea1n?"], 0.3),
    ("beat1", ["Trung b\u00ecnh, m\u1ed9t ch\u00fa ch\u00f3 hi\u1ec3u kho\u1ea3ng m\u1ed9t tr\u0103m s\u00e1u m\u01b0\u01a1i l\u0103m t\u1eeb.",
               "G\u1ea7n b\u1eb1ng m\u1ed9t \u0111\u1ee9a tr\u1ebb hai tu\u1ed5i.",
               "Nh\u01b0ng c\u00f3 m\u1ed9t t\u1eeb, ch\u00f3 nh\u00e0 b\u1ea1n nghe l\u00e0 ch\u1ea1y ngay."], 0.4),
    ("beat2", ["T\u00f4i l\u00e0 Bin.",
               "S\u00e1ng ch\u1ee7 \u0111i l\u00e0m, t\u00f4i \u1edf nh\u00e0 ch\u1edd.",
               "Tr\u01b0a ch\u1ee7 ch\u01b0a v\u1ec1, t\u00f4i ch\u1edd ti\u1ebfp.",
               "T\u1ed1i ch\u1ee7 v\u1ec1, ch\u1ec9 \u00f4m \u0111i\u1ec7n tho\u1ea1i.",
               "T\u00f4i hi\u1ec3u h\u01a1n m\u1ed9t tr\u0103m t\u1eeb c\u1ee7a ch\u1ee7, m\u00e0 ch\u1eb3ng t\u1eeb n\u00e0o l\u00e0 ch\u01a1i v\u1edbi t\u00f4i."], 0.4),
    ("beat3", ["Nh\u01b0ng ch\u1ec9 c\u1ea7n ch\u1ee7 n\u00f3i hai t\u1eeb th\u00f4i, t\u00f4i ch\u1ea1y ngay.",
               "Hai t\u1eeb \u0111\u00f3 l\u00e0: \u0111i d\u1ea1o."], 0.6),
    ("payoff", ["T\u1ed1i nay, th\u1eed n\u00f3i hai t\u1eeb \u0111\u00f3 v\u1edbi ch\u00f3 nh\u00e0 b\u1ea1n xem.",
                "Ch\u00f3 nh\u00e0 b\u1ea1n th\u00edch t\u1eeb n\u00e0o nh\u1ea5t? B\u00ecnh lu\u1eadn nh\u00e9!"], 0.0),
]
CLAUSE_GAP = 0.4
ATEMPO = 0.65

t0 = time.time()
print("Loading Vieneu() ...", flush=True)
tts = Vieneu()
print(f"Loaded in {time.time() - t0:.1f}s", flush=True)
os.makedirs(OUTDIR, exist_ok=True)

parts = []
native_timing = []  # (beat, clause, start, dur, words)
t_cur = 0.0
total_words = 0
speech_s = 0.0
for name, clauses, gap_after in BEATS:
    for ci, clause in enumerate(clauses):
        s1 = time.time()
        audio = np.asarray(tts.infer(clause, voice=VOICE), dtype=np.float32)
        dur = len(audio) / SR
        words = len(clause.split())
        total_words += words
        speech_s += dur
        print(f"{name}[{ci}]: {dur:.2f}s, {words} words, {words/dur*60:.0f} wpm, synth {time.time()-s1:.2f}s :: {clause}", flush=True)
        native_timing.append({"beat": name, "clause": clause, "start": round(t_cur, 3),
                              "dur": round(dur, 3), "words": words})
        parts.append(audio)
        t_cur += dur
        if ci < len(clauses) - 1:
            parts.append(np.zeros(int(CLAUSE_GAP * SR), dtype=np.float32))
            t_cur += CLAUSE_GAP
    if gap_after > 0:
        parts.append(np.zeros(int(gap_after * SR), dtype=np.float32))
        t_cur += gap_after

full = np.concatenate(parts)
native_total = len(full) / SR
sf.write(NATIVE_OUT, full, SR)
print(f"Native assembled: {native_total:.2f}s total ({speech_s:.2f}s speech), "
      f"{total_words} words, speech-only {total_words/speech_s*60:.0f} wpm", flush=True)

# Slow the whole track with atempo (same as approved vieneu_slow.wav)
print(f"Applying atempo={ATEMPO} ...", flush=True)
r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", NATIVE_OUT,
                    "-filter:a", f"atempo={ATEMPO}", SLOWED_OUT],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("ATEMPO FAILED:", r.stderr, flush=True)
    raise SystemExit(1)
slowed, sr = sf.read(SLOWED_OUT, dtype="float32")
assert sr == SR
slow_total = len(slowed) / SR
print(f"Slowed: {slow_total:.2f}s (expected x{1/ATEMPO:.3f} = {native_total/ATEMPO:.2f}s)", flush=True)

# Measure leading near-silence (sample-level) and trim BEFORE timings freeze
absamp = np.abs(slowed)
thresh = 0.005
nz = np.argmax(absamp > thresh)
lead = nz / SR
print(f"Leading near-silence: {lead:.3f}s (first sample above {thresh})", flush=True)
trim_s = 0.0
if lead > 0.05:
    # trim everything up to 0.02s before the first audible sample
    cut = max(0, nz - int(0.02 * SR))
    slowed = slowed[cut:]
    trim_s = cut / SR
    print(f"Trimmed {trim_s:.3f}s of leading silence", flush=True)
sf.write(OUT, slowed, SR)

# 16 kHz mono copy for the Whisper check
r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", OUT,
                    "-ar", "16000", "-ac", "1", OUT16K],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("16K RESAMPLE FAILED:", r.stderr, flush=True)
    raise SystemExit(1)

# Scale native timings by 1/atempo, then shift by (lead - trim):
# every VieNeu clause carries ~lead seconds of leading near-silence, so
# the words of clause i start at nominal_scaled + (lead - trim), NOT at
# nominal_scaled - trim (that put the first clause at -0.11s).
offset = lead - trim_s
scale = 1.0 / ATEMPO
units = []
for it in native_timing:
    start = it["start"] * scale + offset
    dur = it["dur"] * scale
    units.append({"beat": it["beat"], "clause": it["clause"],
                  "start": round(start, 2), "end": round(start + dur, 2),
                  "dur": round(dur, 2), "words": it["words"]})
final_total = len(slowed) / SR
final_speech = speech_s * scale
print(f"FINAL voice: {final_total:.2f}s total, {total_words} words, "
      f"speech-only {total_words/final_speech*60:.0f} wpm, "
      f"overall {total_words/final_total*60:.0f} wpm, voice onset {units[0]['start']:.2f}s", flush=True)
with open(UNITS_OUT, "w", encoding="utf-8") as f:
    json.dump({"units": units, "total": round(final_total, 2),
               "words": total_words, "trim_s": round(trim_s, 3),
               "voice": VOICE, "atempo": ATEMPO}, f, ensure_ascii=False, indent=2)
print(f"Saved {OUT}, {OUT16K}, {UNITS_OUT}", flush=True)
print(f"TOTAL {time.time() - t0:.1f}s")
print("V012_TTS_DONE")
