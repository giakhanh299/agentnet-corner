"""Round 2 — MMS-TTS pacing fix: slower within-sentence speed + short pauses.

User verdict (round 1): the MMS voice itself is GOOD — keep it. Only the
pauses and speed are wrong. Round 1's mms_varied.wav had per-sentence
183/194/131 wpm with 0.6s/0.8s gaps: fast bursts + long gaps. This round
slows the speech INSIDE sentences (transformers 5.23.0 VitsModel has no
length_scale; it has `speaking_rate` — lower = slower, verified by probe2:
rate 1.0 -> 164 wpm, 0.75 -> 135 wpm, 1.25 -> 196 wpm on sentence 1)
and uses SHORT, well-placed pauses.

Pause scheme (same for all variants; the task's three numbers mapped to
the three pause points that exist): 0.3s after the hook, 0.4s micro-pause
at the comma inside sentence 2 (split into two clauses), 0.6s before the
payoff line. Variant D uses a 0.25s comma micro-pause instead, at default
speed, to isolate gap placement from speed.

Variants (same 3 test sentences as round 1, 40 words):
  A  mms_slow12.wav   speaking_rate 0.83  (= length_scale 1.2)
  B  mms_slow135.wav  speaking_rate 0.74  (= length_scale 1.35)
  C  mms_slow09.wav   speaking_rate 0.92  (ADDED bracket: probe showed
       sentence 1 already at 164 wpm at rate 1.0, so 0.83 may drop the
       overall below the 150-165 zone; 0.92 should land near its centre)
  D  mms_clause.wav   speaking_rate 1.0 + 0.25s comma micro-pause
       (control: default speed, clause split only)

Each variant: per-sentence speech wpm (pauses excluded), overall wpm
(pauses included), speech-only wpm, faster-whisper large-v3 word-match.
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\voice_compare"

# (name, text, word count) — sentence 2 is split at the comma into 2 clauses.
SENTENCES = [
    ("hook", ["Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?"]),
    ("beat", ["Thủy thủ viết tất cả vào sổ nhật ký của tàu,", "gọi là sổ log."]),
    ("payoff", ["Đăng nhập là ký tên vào sổ log của tàu."]),
]
GAP_AFTER_HOOK = 0.3   # s1 -> s2
GAP_BEFORE_PAYOFF = 0.6  # s2 -> s3
EXPECTED_TEXT = ("Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước? "
                 "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log. "
                 "Đăng nhập là ký tên vào sổ log của tàu.")

VARIANTS = [
    # (filename, speaking_rate, comma_pause_s, label)
    ("mms_slow12.wav", 0.83, 0.4, "A: speaking_rate 0.83 (= length_scale 1.2)"),
    ("mms_slow135.wav", 0.74, 0.4, "B: speaking_rate 0.74 (= length_scale 1.35)"),
    ("mms_slow09.wav", 0.92, 0.4, "C: speaking_rate 0.92 (added bracket, near zone centre)"),
    ("mms_clause.wav", 1.0, 0.25, "D: speaking_rate 1.0 + 0.25s comma pause (control)"),
]


def synth(model, tok, device, text, rate):
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs, speaking_rate=rate).waveform[0].cpu().numpy()
    return np.clip(w, -1, 1).astype(np.float32)


def save_wav(path, audio):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())


def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()


t0 = time.time()
print("Loading facebook/mms-tts-vie ...", flush=True)
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded on {device}", flush=True)

results = {}  # filename -> (per_sentence_wpm list, overall_wpm, speech_wpm, total_s)

for fname, rate, comma_pause, label in VARIANTS:
    print(f"\n=== {label} -> {fname} ===", flush=True)
    parts = []
    per_sentence_wpm = []
    speech_s = 0.0
    total_words = 0
    for si, (name, clauses) in enumerate(SENTENCES):
        clause_wavs = []
        s_dur = 0.0
        s_words = 0
        for ci, clause in enumerate(clauses):
            w = synth(model, tok, device, clause, rate)
            clause_wavs.append(w)
            s_dur += len(w) / SR
            s_words += len(clause.split())
        speech_s += s_dur
        total_words += s_words
        wpm = s_words / s_dur * 60
        per_sentence_wpm.append(wpm)
        print(f"  {name}: {s_dur:.2f}s speech, {s_words} words, {wpm:.0f} wpm", flush=True)
        # join clauses with the comma micro-pause
        for ci, w in enumerate(clause_wavs):
            parts.append(w)
            if ci < len(clause_wavs) - 1:
                parts.append(np.zeros(int(comma_pause * SR), dtype=np.float32))
        # inter-sentence gaps
        if si == 0:
            parts.append(np.zeros(int(GAP_AFTER_HOOK * SR), dtype=np.float32))
        elif si == 1:
            parts.append(np.zeros(int(GAP_BEFORE_PAYOFF * SR), dtype=np.float32))
    full = np.concatenate(parts)
    total_s = len(full) / SR
    out = os.path.join(OUTDIR, fname)
    save_wav(out, full)
    overall = total_words / total_s * 60
    speech_only = total_words / speech_s * 60
    print(f"  Saved {out}: {total_s:.2f}s total ({speech_s:.2f}s speech + "
          f"{total_s - speech_s:.2f}s pauses), {total_words} words, "
          f"overall {overall:.0f} wpm, speech-only {speech_only:.0f} wpm", flush=True)
    results[fname] = (per_sentence_wpm, overall, speech_only, total_s)

# --- Whisper self-check for every variant ---
from faster_whisper import WhisperModel
import soundfile as sf
import difflib

print("\nLoading faster-whisper large-v3 for the tone check ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
E = tokens(EXPECTED_TEXT)
for fname, rate, comma_pause, label in VARIANTS:
    path = os.path.join(OUTDIR, fname)
    audio, sr = sf.read(path, dtype="float32")
    assert sr == 16000
    segments, info = wm.transcribe(audio, language="vi", beam_size=5)
    heard = " ".join(s.text.strip() for s in segments)
    H = tokens(heard)
    sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    matched_idx = set()
    for b in sm.get_matching_blocks():
        matched_idx.update(range(b.a, b.a + b.size))
    missed = [E[i] for i in range(len(E)) if i not in matched_idx]
    per_wpm, overall, speech_only, total_s = results[fname]
    print(f"{fname}: Whisper {matched}/{len(E)} = {matched / len(E) * 100:.1f}% | "
          f"per-sentence wpm {[round(x) for x in per_wpm]} | overall {overall:.0f} wpm | "
          f"speech-only {speech_only:.0f} wpm", flush=True)
    print(f"  Heard: {heard}", flush=True)
    print(f"  Missed/misheard: {missed}", flush=True)

print(f"\nTOTAL {time.time() - t0:.1f}s", flush=True)
print("VOICE_R2_SYNTH_DONE", flush=True)
