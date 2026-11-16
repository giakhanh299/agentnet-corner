"""MMS-TTS demo for the V014 screen recording (PC, .venv-ai).

Loads facebook/mms-tts-vie and synthesizes the hook sentence, printing the
timing — the real command behind the '0,9 GIÂY' claim. Runs inside the
interactive screen session so the terminal output is captured by gdigrab.
"""
import glob
import os
import sys
import time

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
TEXT = "Đừng làm thêm giờ nữa. Máy tính nhà bạn làm video nhanh hơn bạn tưởng."

print("Loading facebook/mms-tts-vie ...", flush=True)
t0 = time.time()
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded in {time.time() - t0:.1f}s on {device}, speaking_rate=0.92", flush=True)
inputs = tok(TEXT, return_tensors="pt").to(device)
t1 = time.time()
with torch.no_grad():
    w = model(**inputs, speaking_rate=0.92).waveform[0].cpu().numpy()
synth = time.time() - t1
print(f"Synth: {len(w) / SR:.2f}s audio, {len(TEXT.split())} words, in {synth:.2f}s", flush=True)
print("MMS_DEMO_DONE")
