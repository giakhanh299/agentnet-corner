"""V003 probe round 3 — one more beat-2 variant avoiding "ray" entirely.

Probe 1/2: "kẹp chặt ray" -> "rai" (88.2%); "kẹp chặt đường ray" -> "gai"
(88.9%). "ray" is consistently misheard. Try the brake as the subject:
  "Nhưng thang máy có tới bốn lớp an toàn, phanh kẹp chặt mỗi khi quá tốc độ."
Same fact (safety brake clamps on overspeed), same word count (17).
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v003"
TEXT = "Nhưng thang máy có tới bốn lớp an toàn, phanh kẹp chặt mỗi khi quá tốc độ."


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

inputs = tok(TEXT, return_tensors="pt").to(device)
with torch.no_grad():
    w = model(**inputs, speaking_rate=RATE).waveform[0].cpu().numpy()
w = np.clip(w, -1, 1).astype(np.float32)
path = os.path.join(OUTDIR, "P2c_phanh.wav")
with wave.open(path, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((w * 32767).astype(np.int16).tobytes())
print(f"P2c_phanh: {len(w)/SR:.2f}s, {len(TEXT.split())} words -> {path}", flush=True)

from faster_whisper import WhisperModel
import soundfile as sf
import difflib

print("Loading faster-whisper large-v3 ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
audio, sr = sf.read(path, dtype="float32")
segments, info = wm.transcribe(audio, language="vi", beam_size=5)
heard = " ".join(s.text.strip() for s in segments)
E, H = tokens(TEXT), tokens(heard)
sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
matched = sum(b.size for b in sm.get_matching_blocks())
matched_idx = set()
for b in sm.get_matching_blocks():
    matched_idx.update(range(b.a, b.a + b.size))
missed = [E[i] for i in range(len(E)) if i not in matched_idx]
print(f"P2c_phanh: Whisper {matched}/{len(E)} = {matched/len(E)*100:.1f}%", flush=True)
print(f"  Expected: {TEXT}", flush=True)
print(f"  Heard:    {heard}", flush=True)
print(f"  Missed:   {missed}", flush=True)
print(f"TOTAL {time.time() - t0:.1f}s")
print("V003_PROBE3_DONE")
