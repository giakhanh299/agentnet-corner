"""V006 full voice — MMS-TTS (facebook/mms-tts-vie) on the PC, speaking_rate 0.92.

Script (130 words after probe swap, 5 beats) from
scripts-batch-20261116/script_v006-triple-point-45s.md.
Voice plan: round-2 variant C (speaking_rate 0.92, speech-only ~160 wpm,
in the 150-165 safe zone). Pause scheme: 0.3s after hook, 0.4s between
beats and at clause splits, 0.6s before payoff (NOT the old fixed 1.2s).

PROBE SWAP (2026-11-16, PC): "áp suất" -> heard "ác súc" (P1, 88.2%,
both tokens missed) — swapped to "sức ép không khí" per the script's
fallback, consistently in all 4 occurrences (beat1 x1, beat2 x2, beat3 x1).
Word count 122 -> 130. "đóng băng" (P2, 90.9%, keyword heard), "buồng kín"
(P3, 100%), "trạng thái" (P4, 100%) all PASS — kept as-is. Hook's first
word "Nước" heard as "Đất" (same first-word issue as v003's "Cáp"->"Các");
on-screen text carries the spelling, hook kept.
PROBE2 SWAP (2026-11-16, PC): "loãng" -> heard "loạn" TWICE (whole-file
check + isolated P5, 84.6%) — MMS cannot say "loãng". Swapped to "mỏng
hơn" (P6, 100.0%) in beat2 clause 1. Word count unchanged (130).

Beats (start times are printed + saved for the video assembly / captions):
  hook   0-4s    "Nước vừa sôi vừa đóng băng một lúc — tin được không?"
  beat1  4-13s   "Nước sôi ở độ nào, không phải do nước quyết định, mà do
                  sức ép không khí quyết định."
  beat2  13-25s  "Lên núi cao, không khí loãng hơn, sức ép không khí thấp hơn,
                  nước sôi ở nhiệt độ thấp hơn hẳn. Xuống càng thấp, sức ép
                  không khí càng lớn, nước càng khó sôi."
  beat3  25-38s  "Cho nước vào một buồng kín rồi rút hết không khí ra. Sức ép
                  không khí tụt xuống đúng điểm mà nước lỏng vừa đủ tồn tại.
                  Một phần nước sôi lên, một phần đóng băng lại — cùng một lúc."
  payoff 38-45s  "Đó là điểm ba trạng thái — nơi đá, nước và hơi nước cùng tồn
                  tại. Bạn có dám thử không? Bình luận nhé!"
"""
import glob
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v006"
OUT = os.path.join(OUTDIR, "v006_voice.wav")
SEG_OUT = os.path.join(OUTDIR, "v006_fw_segments.txt")
HEARD_OUT = os.path.join(OUTDIR, "v006_fw_heard.txt")
TIMING_OUT = os.path.join(OUTDIR, "v006_beat_timing.txt")

# (beat name, [clauses], gap_after_s)
BEATS = [
    ("hook", ["Nước vừa sôi vừa đóng băng một lúc — tin được không?"], 0.3),
    ("beat1", ["Nước sôi ở độ nào,",
               "không phải do nước quyết định,",
               "mà do sức ép không khí quyết định."], 0.4),
    ("beat2", ["Lên núi cao, không khí mỏng hơn, sức ép không khí thấp hơn, nước sôi ở nhiệt độ thấp hơn hẳn.",
               "Xuống càng thấp, sức ép không khí càng lớn, nước càng khó sôi."], 0.4),
    ("beat3", ["Cho nước vào một buồng kín rồi rút hết không khí ra.",
               "Sức ép không khí tụt xuống đúng điểm mà nước lỏng vừa đủ tồn tại.",
               "Một phần nước sôi lên, một phần đóng băng lại — cùng một lúc."], 0.6),
    ("payoff", ["Đó là điểm ba trạng thái — nơi đá, nước và hơi nước cùng tồn tại. Bạn có dám thử không? Bình luận nhé!"], 0.0),
]
CLAUSE_GAP = 0.4
EXPECTED_TEXT = " ".join(" ".join(clauses) for _, clauses, _ in BEATS)


def synth(model, tok, device, text):
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs, speaking_rate=RATE).waveform[0].cpu().numpy()
    return np.clip(w, -1, 1).astype(np.float32)


t0 = time.time()
print("Loading facebook/mms-tts-vie ...", flush=True)
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded on {device}", flush=True)
os.makedirs(OUTDIR, exist_ok=True)

parts = []
timing = []
t_cur = 0.0
total_words = 0
speech_s = 0.0
for name, clauses, gap_after in BEATS:
    start = t_cur
    beat_words = 0
    beat_speech = 0.0
    for ci, clause in enumerate(clauses):
        w = synth(model, tok, device, clause)
        dur = len(w) / SR
        beat_speech += dur
        beat_words += len(clause.split())
        parts.append(w)
        t_cur += dur
        if ci < len(clauses) - 1:
            parts.append(np.zeros(int(CLAUSE_GAP * SR), dtype=np.float32))
            t_cur += CLAUSE_GAP
    speech_s += beat_speech
    total_words += beat_words
    wpm = beat_words / beat_speech * 60
    print(f"{name}: start {start:.2f}s, {beat_speech:.2f}s speech, {beat_words} words, {wpm:.0f} wpm", flush=True)
    timing.append(f"{name}: {start:.2f}-{t_cur:.2f} ({beat_words} words, {wpm:.0f} wpm)")
    if gap_after > 0:
        parts.append(np.zeros(int(gap_after * SR), dtype=np.float32))
        t_cur += gap_after

full = np.concatenate(parts)
total_s = len(full) / SR
with wave.open(OUT, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"Saved {OUT}: {total_s:.2f}s total ({speech_s:.2f}s speech + {total_s - speech_s:.2f}s pauses), "
      f"{total_words} words, overall {total_words/total_s*60:.0f} wpm, speech-only {total_words/speech_s*60:.0f} wpm", flush=True)
with open(TIMING_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(timing) + f"\nTOTAL {total_s:.2f}s, {total_words} words, overall {total_words/total_s*60:.0f} wpm\n")

# --- Whisper self-check on the whole file ---
from faster_whisper import WhisperModel
import soundfile as sf
import difflib

print("Loading faster-whisper large-v3 ...", flush=True)
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


def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()


E, H = tokens(EXPECTED_TEXT), tokens(heard)
sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
matched = sum(b.size for b in sm.get_matching_blocks())
matched_idx = set()
for b in sm.get_matching_blocks():
    matched_idx.update(range(b.a, b.a + b.size))
missed = [E[i] for i in range(len(E)) if i not in matched_idx]
print(f"Expected ({len(E)} words): {EXPECTED_TEXT}", flush=True)
print(f"Heard    ({len(H)} words): {heard}", flush=True)
print(f"TTS tone check: {matched}/{len(E)} words heard correctly = {matched/len(E)*100:.1f}%", flush=True)
print(f"Missed/misheard words: {missed}", flush=True)
with open(SEG_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(seg_lines) + "\n")
with open(HEARD_OUT, "w", encoding="utf-8") as f:
    f.write(heard + "\n")
print(f"Saved segments to {SEG_OUT}, heard text to {HEARD_OUT}, timing to {TIMING_OUT}", flush=True)
print(f"TOTAL {time.time() - t0:.1f}s")
print("V006_TTS_DONE")
