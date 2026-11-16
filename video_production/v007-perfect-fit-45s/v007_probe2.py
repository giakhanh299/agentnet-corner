"""Probe round 2 for V007: full #2 sentence variants + #1/#5 payoff words.

  q1_n2_orig:  #2 as written (rãnh + milimét)
  q2_n2_fb:    #2 with both fallbacks (khe + "khít không còn khe hở")
  q3_n2_chay:  #2 shorter variant (chạy + khe)
  q4_n1:       #1 payoff (chốt cửa)
  q5_n5:       #5 (chìa khóa tra vào ổ)
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v007_probe2"

PROBES = [
    ("q1_n2_orig", "Số hai: bánh xe tải lăn đúng vào rãnh, khít từng milimét."),
    ("q2_n2_fb", "Số hai: bánh xe tải lăn đúng vào khe, khít không còn khe hở."),
    ("q3_n2_chay", "Số hai: bánh xe tải chạy đúng vào khe."),
    ("q4_n1", "Số một: chốt cửa sập vào đúng lỗ. Một tiếng cạch duy nhất."),
    ("q5_n5", "Số năm: chìa khóa tra vào ổ, xoay một cái là mở."),
]

os.makedirs(OUTDIR, exist_ok=True)
t0 = time.time()
print("Loading facebook/mms-tts-vie ...", flush=True)
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded in {time.time() - t0:.1f}s on {device}, speaking_rate={RATE}", flush=True)

def save_wav(path, w):
    w = np.clip(w, -1, 1).astype(np.float32)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((w * 32767).astype(np.int16).tobytes())

for name, text in PROBES:
    t1 = time.time()
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs, speaking_rate=RATE).waveform[0].cpu().numpy()
    save_wav(os.path.join(OUTDIR, name + ".wav"), w)
    print(f"{name}: {len(w) / SR:.2f}s, synth {time.time() - t1:.2f}s :: {text}", flush=True)

from faster_whisper import WhisperModel
import soundfile as sf

print("Loading faster-whisper large-v3 ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")

def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()

import difflib
for name, expected in PROBES:
    path = os.path.join(OUTDIR, name + ".wav")
    audio, sr = sf.read(path, dtype="float32")
    segments, info = wm.transcribe(audio, language="vi", beam_size=5)
    heard = " ".join(s.text.strip() for s in segments)
    E, H = tokens(expected), tokens(heard)
    sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    print(f"{name}: {matched}/{len(E)} = {matched / len(E) * 100:.0f}% | heard: {heard}", flush=True)

print(f"TOTAL {time.time() - t0:.1f}s", flush=True)
