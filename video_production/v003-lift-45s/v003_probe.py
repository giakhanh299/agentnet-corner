"""V003 probe — 3 risky MMS words, each in its real sentence, speaking_rate 0.92.

Sentences (from script_v003-lift-45s.md):
  P1 hook:  "Cáp thang máy đứt ở tầng tám mươi lăm — nhảy lên thì sống không?"
           -> risky word "tám mươi lăm" (v001: "hai mươi mốt" failed)
  P2 beat2: "Nhưng thang máy có tới bốn lớp an toàn, kẹp chặt ray mỗi khi quá tốc độ."
           -> risky phrase "kẹp chặt ray" ("ray" is rare)
  P3 beat3: "Nếu thang thật sự rơi, cách khoa học nhất là nằm ngửa xuống sàn, tay ôm đầu."
           -> risky word "ngửa"

Each sentence is synthesized alone and Whisper-checked alone (v002 lesson:
per-sentence probe is more accurate than whole-file listening).
Fallbacks (from the script file) if a word is misheard:
  "tám mươi lăm" -> "tầng cao nhất" (keep "TẦNG 85" on-screen only)
  "kẹp chặt ray" -> "kẹp chặt đường ray" or "ghì chặt vào ray"
  "ngửa"         -> "nằm dài xuống sàn"
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

PROBES = [
    ("P1_tam_muoi_lam", "Cáp thang máy đứt ở tầng tám mươi lăm — nhảy lên thì sống không?"),
    ("P2_kep_chat_ray", "Nhưng thang máy có tới bốn lớp an toàn, kẹp chặt ray mỗi khi quá tốc độ."),
    ("P3_nam_ngua", "Nếu thang thật sự rơi, cách khoa học nhất là nằm ngửa xuống sàn, tay ôm đầu."),
]


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
os.makedirs(OUTDIR, exist_ok=True)

wavs = {}
for name, text in PROBES:
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs, speaking_rate=RATE).waveform[0].cpu().numpy()
    w = np.clip(w, -1, 1).astype(np.float32)
    path = os.path.join(OUTDIR, name + ".wav")
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((w * 32767).astype(np.int16).tobytes())
    nwords = len(text.split())
    print(f"{name}: {len(w)/SR:.2f}s, {nwords} words, {nwords/(len(w)/SR)*60:.0f} wpm -> {path}", flush=True)
    wavs[name] = (path, text)

from faster_whisper import WhisperModel
import soundfile as sf
import difflib

print("Loading faster-whisper large-v3 ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
for name, text in PROBES:
    path, _ = wavs[name]
    audio, sr = sf.read(path, dtype="float32")
    segments, info = wm.transcribe(audio, language="vi", beam_size=5)
    heard = " ".join(s.text.strip() for s in segments)
    E, H = tokens(text), tokens(heard)
    sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    matched_idx = set()
    for b in sm.get_matching_blocks():
        matched_idx.update(range(b.a, b.a + b.size))
    missed = [E[i] for i in range(len(E)) if i not in matched_idx]
    print(f"{name}: Whisper {matched}/{len(E)} = {matched/len(E)*100:.1f}%", flush=True)
    print(f"  Expected: {text}", flush=True)
    print(f"  Heard:    {heard}", flush=True)
    print(f"  Missed:   {missed}", flush=True)

print(f"TOTAL {time.time() - t0:.1f}s")
print("V003_PROBE_DONE")
