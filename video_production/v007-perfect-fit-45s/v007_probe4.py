"""Probe round 4 for V007 (final): #5 rewordings + #2 second sentence alone.

  s1_n5_vuakhit:  #5 "chìa khóa vừa khít ổ"
  s2_n5_cam:      #5 "chìa khóa cắm vào ổ khóa"
  s3_n2_s2:       #2 second sentence alone
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v007_probe4"

PROBES = [
    ("s1_n5_vuakhit", "Số năm: chìa khóa vừa khít ổ, xoay một cái là mở."),
    ("s2_n5_cam", "Số năm: chìa khóa cắm vào ổ khóa, xoay một cái là mở."),
    ("s3_n2_s2", "Như thể cái khe sinh ra cho nó."),
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
