#!/usr/bin/env python3
"""VieNeu-TTS v3 Turbo full narration for V013 on the controller VPS.

Voice: "Mai Anh" (female preset) — approved production voice.
Recipe: SDK Vieneu().infer(text, voice="Mai Anh") at 48 kHz, native
~222 wpm on THIS script, then per-unit ffmpeg atempo=0.70 -> ~155 wpm,
assemble with pauses, TRIM leading silence BEFORE building timings
(v010 lesson). NOTE on the tempo: the round-4 test sentences ran 238 wpm
native, so atempo=0.65 gave ~155 wpm; this script's native rate is
222 wpm, so 0.65 would give only 144 wpm (below the 150-165 zone) —
0.70 is used instead to land at ~155 wpm. Same voice, same method,
rate chosen to hit the zone.

Probe results (VPS whisper.cpp Base — weaker than PC large-v3; the
parent MUST re-verify on the PC; see v013_production_notes.md):
  - "chuong truong" KEPT ("Trung Chuong" under Base; on-screen text
    carries spelling; Base also mangled "So nam"/"tieng").
  - "de no" KEPT ("de"->"de", "no" correct; fallback "no may" worse).
  - "cuc gach" KEPT ("cuc"->"cuc" tone only, "gach" correct).
  - "rao" FAIL ("sau") -> "ban" (fallback heard clean). SWAPPED.
  - "modem" FAIL ("1 dam") -> "quay so" (fallback heard clean). SWAPPED.
Final word count: 116 (was 117; "modem quay so" -> "quay so" drops 1).

Units + pauses: hook 0.3 / #5-#2 0.4 each / #1 0.6 / payoff 0.0.
Output: voice.wav (48 kHz mono), v013_units.json (slowed timings),
v013_whisper_base.txt (Base check on the slowed voice).
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
import soundfile as sf

from vieneu import Vieneu

BASE = "/home/hatch/workspace/agentnet-corner/video_production/v013-iconic-sounds-45s"
VOICE = "Mai Anh"
ATEMPO = 0.70  # see note above: lands this script at ~155 wpm speech-only
SR = 48000
OUT = os.path.join(BASE, "voice.wav")
UNITS_OUT = os.path.join(BASE, "v013_units.json")
TMP = os.path.join(BASE, "tts_tmp")
os.makedirs(TMP, exist_ok=True)

# (unit, text, pause_after_s) — post-probe final text
UNITS = [
    ("hook", "Năm âm thanh này, nghe một giây là nhớ ngay. Số một, đảm bảo bạn đã nghe cả trăm lần.", 0.3),
    ("n5", "Số năm: tiếng chuông trường. Tan học là chạy, không cần ai nhắc.", 0.4),
    ("n4", "Số bốn: tiếng xe máy đề nổ. Sáng nào cũng nghe, cả xóm cùng dậy.", 0.4),
    ("n3", "Số ba: tiếng bán bánh mì. Chưa thấy xe đâu, đã thấy đói.", 0.4),
    ("n2", "Số hai: nhạc chuông điện thoại cục gạch. Giai điệu này có từ hơn một trăm năm trước, già hơn cả ông bà bạn.", 0.4),
    ("n1", "Số một: tiếng quay số. Nghe xong mới được lên mạng, mà rớt mạng là quay lại từ đầu.", 0.6),
    ("cta", "Bạn nhớ âm thanh nào nhất? Bình luận số của nó nhé!", 0.0),
]

def run(cmd):
    print("+ " + " ".join(cmd), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f"FAILED rc={r.returncode}: {' '.join(cmd[:3])}")
    return r

t0 = time.time()
print("Loading Vieneu() ...", flush=True)
tts = Vieneu()
print(f"Loaded in {time.time() - t0:.1f}s", flush=True)

# --- synthesize each unit natively, slow with atempo, record durations ---
parts = []          # slowed float32 arrays (48 kHz)
units_timing = []   # slowed timings, pauses NOT yet applied (filled below)
total_words = 0
t_syn = time.time()
native_durs = {}
for name, text, pause_after in UNITS:
    s0 = time.time()
    audio = np.asarray(tts.infer(text, voice=VOICE), dtype=np.float32)
    native = len(audio) / SR
    nwords = len(text.split())
    total_words += nwords
    print(f"{name}: native {native:.2f}s, {nwords} words, "
          f"{nwords / native * 60:.0f} wpm, synth {time.time() - s0:.1f}s :: {text}", flush=True)
    native_path = os.path.join(TMP, name + "_native.wav")
    slow_path = os.path.join(TMP, name + "_slow.wav")
    sf.write(native_path, audio, SR)
    run(["ffmpeg", "-v", "error", "-y", "-i", native_path,
         "-af", f"atempo={ATEMPO}", "-ar", str(SR), "-ac", "1", slow_path])
    slow, sr = sf.read(slow_path, dtype="float32")
    assert sr == SR
    slow_dur = len(slow) / SR
    print(f"  -> slowed {slow_dur:.2f}s ({nwords / slow_dur * 60:.0f} wpm), "
          f"ratio {slow_dur / native:.3f} (expect {1 / ATEMPO:.3f})", flush=True)
    parts.append((name, text, slow, pause_after, nwords))
    native_durs[name] = native
print(f"Synthesis {time.time() - t_syn:.1f}s", flush=True)

# --- assemble slowed units + pauses, trim leading silence ---
full_parts = []
t_cur = 0.0
for name, text, slow, pause_after, nwords in parts:
    units_timing.append({"unit": name, "text": text,
                         "start": round(t_cur, 2), "end": round(t_cur + len(slow) / SR, 2),
                         "words": nwords})
    full_parts.append(slow)
    t_cur += len(slow) / SR
    if pause_after > 0:
        full_parts.append(np.zeros(int(pause_after * SR), dtype=np.float32))
        t_cur += pause_after
full = np.concatenate(full_parts)
# trim leading near-silence (threshold -40 dBFS), keep 10 ms guard
idx = np.argmax(np.abs(full) > 0.01)
trim = max(0, idx - int(0.01 * SR))
trim_s = trim / SR
if trim > 0:
    full = full[trim:]
    for u in units_timing:
        u["start"] = round(max(0.0, u["start"] - trim_s), 2)
        u["end"] = round(u["end"] - trim_s, 2)
total_dur = len(full) / SR
speech_dur = sum(u["end"] - u["start"] for u in units_timing)
print(f"Leading silence trimmed: {trim_s:.3f}s", flush=True)
print(f"Saved {OUT}: {total_dur:.2f}s total, {total_words} words", flush=True)
print(f"Speech-only: {speech_dur:.2f}s = {total_words / speech_dur * 60:.0f} wpm; "
      f"overall: {total_words / total_dur * 60:.0f} wpm", flush=True)
sf.write(OUT, np.clip(full, -1, 1), SR, subtype="PCM_16")
with open(UNITS_OUT, "w", encoding="utf-8") as f:
    json.dump(units_timing, f, ensure_ascii=False, indent=2)
print(f"Saved unit timings to {UNITS_OUT}", flush=True)
print(f"TOTAL {time.time() - t0:.1f}s", flush=True)
