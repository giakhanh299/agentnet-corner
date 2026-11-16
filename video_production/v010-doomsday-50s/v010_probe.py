"""V010 probe - 4 risky MMS words, each in its real sentence, speaking_rate 0.92.

Sentences (from scripts-batch-20261116/script_v010-doomsday-50s.md):
  P1 tan_the:    "Ngay muoi ba vua roi, the gioi phai tan the. Nhung ban van dang xem video nay."
                 -> risky word "tan the" (hook keyword)
  P2 vo_cung:    "Ba nha khoa hoc tinh rang dan so tang nhanh mai, roi cham toi vo cung vao dung nam do."
                 -> risky word "vo cung"
  P3 dat_dinh:   "Toc do tang dan so dat dinh tu nam mot chin sau ba roi giam dan."
                 -> risky word "dat dinh"
  P4 truong_nhom:"Nhung ho cung khong tin, vi do la sinh nhat cua ong truong nhom."
                 -> risky phrase "truong nhom"

Each sentence is synthesized alone and Whisper-checked alone (v002 lesson:
per-sentence probe is more accurate than whole-file listening).
Fallbacks (from the script file) if a word is misheard:
  "tan the"     -> hook becomes "ngay the gioi phai ket thuc"
  "vo cung"     -> "tang mai khong dung"
  "dat dinh"    -> "len cao nhat"
  "truong nhom" -> "nguoi dung dau nhom"
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v010"

PROBES = [
    ("P1_tan_the", "Ngày mười ba vừa rồi, thế giới phải tận thế. Nhưng bạn vẫn đang xem video này."),
    ("P2_vo_cung", "Ba nhà khoa học tính rằng dân số tăng nhanh mãi, rồi chạm tới vô cùng vào đúng năm đó."),
    ("P3_dat_dinh", "Tốc độ tăng dân số đạt đỉnh từ năm một chín sáu ba rồi giảm dần."),
    ("P4_truong_nhom", "Nhưng họ cũng không tin, vì đó là sinh nhật của ông trưởng nhóm."),
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
print("V010_PROBE_DONE")
