"""MMS-TTS (facebook/mms-tts-vie) for V005 on the PC + Whisper self-check.

Adapted from v002_tts.py + round-2 voice_r2_synth.py.
Speaking_rate 0.92 (variant C, round 2 — in the 150-165 wpm zone).
Pauses: 0.3s after hook, 0.3s micro-pause between clauses inside a beat,
0.4s between beats, 0.6s before #1 (riser zone), 0.4s before CTA.

Word swaps from probe results (see v005_probe.py / v005_probe2.py):
  - "trĩu" -> "nặng nề" (probe: trĩu heard as "triếu"; nặng nề heard clean)
  - "Tao" kept (100% probe)
  - "phăng phắc" KEPT despite MMS hearing "phan phát" (final-consonant
    mangling) — all 4 alternatives tested failed worse ("thin thít"->
    "Kim Thiên Thí", "im re"->"Inge", "nín thinh"->"nứng thiên").
    On-screen list text + captions carry the correct spelling (same
    precedent as "log" in v002).
  - "…" in #2 replaced by "." for synthesis only (on-screen keeps "…").
  - "—" in #1 replaced by "," for synthesis only.
"""
import glob
import json
import os
import re
import sys
import time
import wave

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_site = os.path.normpath(os.path.join(os.path.dirname(sys.executable), "..", "Lib", "site-packages"))
_torch_lib = os.path.join(_site, "torch", "lib")
if os.path.isdir(_torch_lib):
    os.add_dll_directory(_torch_lib)
for _d in glob.glob(os.path.join(_site, "nvidia", "*", "bin")):
    os.add_dll_directory(_d)

import numpy as np
import torch
from transformers import AutoTokenizer, VitsModel

SR = 16000
RATE = 0.92
OUT = r"C:\Users\w\agentnet-corner\ai-stack\v005_voice.wav"
UNITS_OUT = r"C:\Users\w\agentnet-corner\ai-stack\v005_units.json"
SEG_OUT = r"C:\Users\w\agentnet-corner\ai-stack\v005_fw_segments.txt"
HEARD_OUT = r"C:\Users\w\agentnet-corner\ai-stack\v005_fw_heard.txt"

# (beat, text, pause_after_s, speaking_rate) — n1a (the emotional #1 quote)
# is slowed to 0.80: at 0.92 it came out at 190 wpm, too fast for the
# emotion flip; the quote must land slow and tender.
UNITS = [
    ("hook", "Top năm câu nói huyền thoại của mẹ!", 0.3, 0.92),
    ("n5a", "Số năm: Ăn cơm đi, nguội hết rồi!", 0.3, 0.92),
    ("n5b", "Mẹ nói câu này ba lần một bữa, lần nào cũng vậy.", 0.4, 0.92),
    ("n4a", "Số bốn: Tao nói mày có nghe không?", 0.3, 0.92),
    ("n4b", "Câu này mà vang lên là cả nhà im phăng phắc.", 0.4, 0.92),
    ("n3a", "Số ba: Hồi bằng tuổi mày, mẹ đã biết nấu cơm, giặt đồ.", 0.3, 0.92),
    ("n3b", "Câu này mẹ kể từ lúc con lên năm.", 0.4, 0.92),
    ("n2a", "Số hai: Con nhà người ta.", 0.3, 0.92),
    ("n2b", "Chỉ ba chữ thôi mà đủ làm con thấy mình thua cả xóm.", 0.6, 0.92),
    ("n1a", "Số một: Mẹ không cần gì đâu, con cứ lo cho con đi.", 0.3, 0.80),
    ("n1b", "Nghe thì nhẹ, mà tim con nặng nề.", 0.4, 0.92),
    ("cta", "Số một của bạn là câu nào? Bình luận nhé!", 0.0, 0.92),
]

t0 = time.time()
print("Loading facebook/mms-tts-vie ...", flush=True)
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded in {time.time() - t0:.1f}s on {device}, speaking_rate={RATE}", flush=True)

parts = []
units_timing = []
total_words = 0
t_cur = 0.0
t_syn = time.time()
for name, text, pause_after, rate in UNITS:
    t1 = time.time()
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs, speaking_rate=rate).waveform[0].cpu().numpy()
    w = np.clip(w, -1, 1).astype(np.float32)
    dur = len(w) / SR
    nwords = len(text.split())
    total_words += nwords
    print(f"{name}: {dur:.2f}s, {nwords} words, {nwords / dur * 60:.0f} wpm, rate {rate}, synth {time.time() - t1:.2f}s :: {text}", flush=True)
    units_timing.append({"unit": name, "text": text, "start": round(t_cur, 2), "end": round(t_cur + dur, 2), "words": nwords})
    parts.append(w)
    t_cur += dur
    if pause_after > 0:
        parts.append(np.zeros(int(pause_after * SR), dtype=np.float32))
        t_cur += pause_after
full = np.concatenate(parts)
with wave.open(OUT, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes())
total_dur = len(full) / SR
speech_dur = sum(u["end"] - u["start"] for u in units_timing)
print(f"Saved {OUT}: {total_dur:.2f}s total, {total_words} words", flush=True)
print(f"Speech-only: {speech_dur:.2f}s = {total_words / speech_dur * 60:.0f} wpm; overall: {total_words / total_dur * 60:.0f} wpm", flush=True)
print(f"Synthesis {time.time() - t_syn:.1f}s", flush=True)
with open(UNITS_OUT, "w", encoding="utf-8") as f:
    json.dump(units_timing, f, ensure_ascii=False, indent=2)
print(f"Saved unit timings to {UNITS_OUT}", flush=True)

# --- Whisper self-check ---
from faster_whisper import WhisperModel
import soundfile as sf

print("Loading faster-whisper large-v3 for the tone check ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
audio, sr = sf.read(OUT, dtype="float32")
assert sr == 16000
segments, info = wm.transcribe(audio, language="vi", beam_size=5)
seg_lines = []
heard_parts = []
for s in segments:
    line = f"[{s.start:.2f}-{s.end:.2f}] {s.text.strip()}"
    print(line, flush=True)
    seg_lines.append(line)
    heard_parts.append(s.text.strip())
heard = " ".join(heard_parts)
expected = " ".join(t for _, t, _, _ in UNITS)

def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()

import difflib
E, H = tokens(expected), tokens(heard)
sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
matched = sum(b.size for b in sm.get_matching_blocks())
matched_idx = set()
for b in sm.get_matching_blocks():
    matched_idx.update(range(b.a, b.a + b.size))
missed = [E[i] for i in range(len(E)) if i not in matched_idx]
print(f"Expected ({len(E)} words): {expected}", flush=True)
print(f"Heard    ({len(H)} words): {heard}", flush=True)
print(f"TTS tone check: {matched}/{len(E)} words heard correctly = {matched / len(E) * 100:.1f}%", flush=True)
print(f"Missed/misheard words: {missed}", flush=True)
with open(SEG_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(seg_lines) + "\n")
with open(HEARD_OUT, "w", encoding="utf-8") as f:
    f.write(heard + "\n")
print(f"Saved segments to {SEG_OUT}, heard text to {HEARD_OUT}", flush=True)
print(f"TOTAL {time.time() - t0:.1f}s", flush=True)
