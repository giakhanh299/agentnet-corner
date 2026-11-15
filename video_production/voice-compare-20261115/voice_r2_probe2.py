"""Probe 2: which way does VitsModel `speaking_rate` go?

Synthesize sentence 1 at speaking_rate 1.0 / 0.75 / 1.25 and print
duration + wpm for each. If 0.75 is LONGER than 1.0, lower = slower
(then length_scale 1.2 ~= speaking_rate 0.83, 1.35 ~= 0.74).
If 0.75 is SHORTER, the direction is inverted and the main script
must use the reciprocal values.
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

import numpy as np
import torch
from transformers import AutoTokenizer, VitsModel

SR = 16000
TEXT = "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?"
NWORDS = len(TEXT.split())

print("Loading facebook/mms-tts-vie ...", flush=True)
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model on {device}", flush=True)

for rate in (1.0, 0.75, 1.25):
    inputs = tok(TEXT, return_tensors="pt").to(device)
    t1 = time.time()
    with torch.no_grad():
        w = model(**inputs, speaking_rate=rate).waveform[0].cpu().numpy()
    dur = len(w) / SR
    print(f"speaking_rate={rate}: {dur:.2f}s, {NWORDS} words, "
          f"{NWORDS / dur * 60:.0f} wpm, synth {time.time() - t1:.2f}s", flush=True)

print("PROBE2_DONE", flush=True)
