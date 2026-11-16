"""Probe 'giau' for V014 b3a on the PC (.venv-vieneu).

Whisper large-v3 heard the b3a unit 'Khong hua ban giau nhanh' as
'... ban sau nhanh' (giau -> sau). Re-synthesize the line twice as-is
plus a 'se' variant, save 16k mono copies for the check step.
"""
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import soundfile as sf

from vieneu import Vieneu

OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v014_tts"
VOICE = "Mai Anh"
SR = 48000

CASES = [
    ("giau_take1", "Không hứa bạn giàu nhanh."),
    ("giau_take2", "Không hứa bạn giàu nhanh."),
    ("giau_se", "Không hứa bạn sẽ giàu nhanh."),
]

t0 = time.time()
print("Loading Vieneu() ...", flush=True)
tts = Vieneu()
print(f"Loaded in {time.time() - t0:.1f}s", flush=True)
import librosa
for name, text in CASES:
    audio = np.asarray(tts.infer(text, voice=VOICE), dtype=np.float32)
    print(f"{name}: {len(audio) / SR:.2f}s :: {text}", flush=True)
    sf.write(os.path.join(OUTDIR, f"v014_{name}_48k.wav"), audio, SR)
    audio16 = librosa.resample(audio, orig_sr=SR, target_sr=16000)
    sf.write(os.path.join(OUTDIR, f"v014_{name}_16k.wav"), audio16, 16000)
print("V014_PROBE_GIAU_DONE")
