"""Probe MMS-TTS on the PC for V009's risky words (speaking_rate 0.92).

Each probe is synthesized to its own wav and Whisper-checked separately.

Primaries (from script):
  p1_huyt:     "huýt" - dolphin signature whistle
  p2_bachtuoc: "bạch tuộc" - #1 keyword (octopus, 3 hearts)
  p3_luot:     "lướt" - flying fish glides
  p4_co:       "cọ" - grasshopper rubs leg on wing
  p5_top:      "Top" - known MMS failure ("Tốc" in v005); kept, captions carry spelling
Fallbacks (only needed if a primary fails):
  p6_keu:      "huýt" -> "kêu một điệu riêng"
  p7_conbachtuoc: "bạch tuộc" -> "con bạch tuộc"
  p8_bay:      "lướt" -> "bay trên không"
  p9_cha:      "cọ" -> "chà chân vào cánh"
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v009_probe"

PROBES = [
    ("p1_huyt", "Mỗi con huýt một điệu riêng."),
    ("p2_bachtuoc", "Bạch tuộc có tới ba trái tim."),
    ("p3_luot", "Nó lướt trên không tới hai trăm mét."),
    ("p4_co", "Nó cọ chân vào cánh."),
    ("p5_top", "Top 5 sự thật về động vật."),
    ("p6_keu", "Mỗi con kêu một điệu riêng."),
    ("p7_conbachtuoc", "Con bạch tuộc có tới ba trái tim."),
    ("p8_bay", "Nó bay trên không tới hai trăm mét."),
    ("p9_cha", "Nó chà chân vào cánh."),
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
