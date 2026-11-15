"""MMS-TTS control with VARIED pauses (Test D).

Same 3 test sentences as the other voices, same MMS-TTS model, but the
inter-sentence silences vary by sentence type instead of v002's fixed
1.2s: 0.6s after the hook, 0.8s before the payoff. This isolates whether
the pauses alone fix the problem, or the voice itself is the problem.
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
OUT = r"C:\Users\w\agentnet-corner\ai-stack\voice_compare\mms_varied.wav"

SENTENCES = [
    ("hook", "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?"),
    ("beat", "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log."),
    ("payoff", "Đăng nhập là ký tên vào sổ log của tàu."),
]
# Varied gaps (seconds): after hook 0.6s, after beat 0.8s (before payoff).
GAPS = [0.6, 0.8]

t0 = time.time()
print("Loading facebook/mms-tts-vie ...", flush=True)
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded in {time.time() - t0:.1f}s on {device}", flush=True)

parts = []
total_words = 0
speech_s = 0.0
t_syn = time.time()
for (name, text), gap in zip(SENTENCES, GAPS + [0.0]):
    t1 = time.time()
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs).waveform[0].cpu().numpy()
    w = np.clip(w, -1, 1).astype(np.float32)
    dur = len(w) / SR
    speech_s += dur
    nwords = len(text.split())
    total_words += nwords
    print(f"{name}: {dur:.2f}s, {nwords} words, {nwords / dur * 60:.0f} wpm, synth {time.time() - t1:.2f}s", flush=True)
    parts.append(w)
    if gap > 0:
        parts.append(np.zeros(int(gap * SR), dtype=np.float32))
full = np.concatenate(parts)
with wave.open(OUT, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"Saved {OUT}: {len(full) / SR:.2f}s total ({speech_s:.2f}s speech + "
      f"{sum(GAPS):.1f}s gaps), {total_words} words, "
      f"overall {total_words / (len(full) / SR) * 60:.0f} wpm, "
      f"speech-only {total_words / speech_s * 60:.0f} wpm, "
      f"synthesis {time.time() - t_syn:.1f}s", flush=True)

# --- Whisper self-check ---
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
