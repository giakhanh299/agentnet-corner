"""MMS-TTS (facebook/mms-tts-vie) test on the PC + Whisper self-check.

Same approach as the VPS (sentence-by-sentence, 16 kHz mono wav), but the
model runs on CUDA here if available. After synthesis, faster-whisper
large-v3 transcribes the output and compares it to the expected sentences,
so tone errors show up as misheard words.
"""
import glob
import os
import re
import sys
import time
import wave

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ctranslate2 needs torch's CUDA DLLs on the DLL search path (see
# ai_whisper_test.py): register torch\lib before importing faster_whisper.
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
OUT = r"C:\Users\w\agentnet-corner\ai-stack\tts_test.wav"

SENTENCES = [
    ("hook", "Cùng làm mười tiếng mỗi ngày, sao một người giàu, một người vẫn nghèo?"),
    ("beat1", "An làm thuê mười tiếng một ngày. Hết giờ, anh nhận lương theo giờ, về nhà mệt lả, ngủ một giấc, sáng mai lại cày tiếp."),
    ("payoff", "Giàu không phải làm nhiều hơn. Giàu là làm khác đi. Bạn chọn bên nào?"),
]
PAUSE_S = 0.5

t0 = time.time()
print("Loading facebook/mms-tts-vie ...", flush=True)
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded in {time.time() - t0:.1f}s on {device}", flush=True)

parts = []
total_words = 0
t_syn = time.time()
for name, text in SENTENCES:
    t1 = time.time()
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs).waveform[0].cpu().numpy()
    w = np.clip(w, -1, 1).astype(np.float32)
    dur = len(w) / SR
    nwords = len(text.split())
    total_words += nwords
    print(f"{name}: {dur:.2f}s, {nwords} words, {nwords / dur * 60:.0f} wpm, synth {time.time() - t1:.2f}s", flush=True)
    parts.append(w)
    parts.append(np.zeros(int(PAUSE_S * SR), dtype=np.float32))
full = np.concatenate(parts)
with wave.open(OUT, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"Saved {OUT}: {len(full) / SR:.2f}s total, {total_words} words, synthesis {time.time() - t_syn:.1f}s", flush=True)

# --- Whisper self-check: transcribe the TTS output and compare ---
from faster_whisper import WhisperModel
import soundfile as sf

print("Loading faster-whisper large-v3 for the tone check ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
audio, sr = sf.read(OUT, dtype="float32")
assert sr == 16000
segments, info = wm.transcribe(audio, language="vi", beam_size=5)
heard = " ".join(s.text.strip() for s in segments)
expected = " ".join(t for _, t in SENTENCES)

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
print(f"TOTAL {time.time() - t0:.1f}s", flush=True)
