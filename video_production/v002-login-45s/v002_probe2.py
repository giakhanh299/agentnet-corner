"""Probe round 2 for V002: settle beat-1 verb, counting verb, and "hai ly".

Round 1 found: "buoc"->"muon" (2/2), "dem"->"den" (2/2),
"hai"->"hay" in "hang hai" (2/2), "log"->"lo" (2/2, both spellings).
This round tests alternatives for the first three; "log" is kept as-is
(on-screen text + captions carry the spelling; see script.md).
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
OUT = r"C:\Users\w\agentnet-corner\ai-stack\v002_probe2.wav"

PROBES = [
    ("q1_base", "Họ ném một khúc gỗ xuống biển, buộc vào sợi dây thắt nút, rồi đếm nút tuột ra."),
    ("q2_cot", "Họ ném một khúc gỗ xuống biển, cột vào sợi dây thắt nút, rồi tính xem có bao nhiêu nút tuột ra."),
    ("q3_dau", "Họ ném một khúc gỗ xuống biển, đầu dây thắt nút, rồi đo xem dây tuột ra bao nhiêu nút."),
    ("q4_haily", "Tốc độ tàu đo bằng nút thắt — một nút bằng một hải lý mỗi giờ."),
    ("q5_ghi", "Mọi con số ghi vào sổ nhật ký hàng hải, gọi là sổ log."),
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
for name, text in PROBES:
    t1 = time.time()
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs).waveform[0].cpu().numpy()
    w = np.clip(w, -1, 1).astype(np.float32)
    print(f"{name}: {len(w) / SR:.2f}s, synth {time.time() - t1:.2f}s :: {text}", flush=True)
    parts.append(w)
    parts.append(np.zeros(int(PAUSE_S * SR), dtype=np.float32))
full = np.concatenate(parts)
with wave.open(OUT, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"Saved {OUT}: {len(full) / SR:.2f}s", flush=True)

from faster_whisper import WhisperModel
import soundfile as sf

print("Loading faster-whisper large-v3 ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
audio, sr = sf.read(OUT, dtype="float32")
segments, info = wm.transcribe(audio, language="vi", beam_size=5)
heard = [s.text.strip() for s in segments]
print(f"Whisper returned {len(heard)} segments for {len(PROBES)} probes", flush=True)

def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()

import difflib
for i, (name, expected) in enumerate(PROBES):
    h = heard[i] if i < len(heard) else "<missing>"
    E, H = tokens(expected), tokens(h)
    sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    print(f"{name}: {matched}/{len(E)} = {matched / len(E) * 100:.0f}% | heard: {h}", flush=True)
print(f"TOTAL {time.time() - t0:.1f}s", flush=True)
