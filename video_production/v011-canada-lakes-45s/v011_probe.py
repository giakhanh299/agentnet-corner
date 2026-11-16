"""V011 probe - 5 risky MMS words, each in its real sentence, speaking_rate 0.92.

Sentences (from scripts-batch-20261116/script_v011-canada-lakes-45s.md):
  P1 canada:    "Do la Canada. Hon sau muoi phan tram so ho tren the gioi nam o day, hon ba muoi mot nghin ho lon."
                -> risky word "Canada" (keyword, repeats 2x: beat 1 + payoff)
  P2 bang_ha:   "Muoi nghin nam truoc, bang ha cao xoi mat dat, de lai hang trieu ho trung."
                -> risky words "bang ha" + "ho trung" (both in this sentence)
  P3 thuong:    "Rieng ho Thuong giu gan mot phan nam luong nuoc ho ngot toan cau."
                -> risky word "Thuong" (Lake Superior name)
  P4 trai_dat:  "Mot nuoc, hon nua so ho cua ca Trai Dat. Ban da tung toi Canada chua? Binh luan nhe!"
                -> risky word "Trai Dat" (payoff keyword; also re-tests "Canada")

Each sentence is synthesized alone and Whisper-checked alone (v002 lesson:
per-sentence probe is more accurate than whole-file listening).
Fallbacks (from the script file) if a word is misheard:
  "Canada"    -> "nuoc nay" (beat 1) / "toi do" (payoff) - change consistently
  "bang ha"   -> "bang tuyet khong lo"
  "ho trung"  -> "ho sau"
  "Thuong"    -> "ho lon nhat"
  "Trai Dat"  -> "ca hanh tinh"
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v011"

PROBES = [
    ("P1_canada", "Đó là Canada. Hơn sáu mươi phần trăm số hồ trên thế giới nằm ở đây, hơn ba mươi mốt nghìn hồ lớn."),
    ("P2_bang_ha", "Mười nghìn năm trước, băng hà cào xới mặt đất, để lại hàng triệu hố trũng."),
    ("P3_thuong", "Riêng hồ Thượng giữ gần một phần năm lượng nước hồ ngọt toàn cầu."),
    ("P4_trai_dat", "Một nước, hơn nửa số hồ của cả Trái Đất. Bạn đã từng tới Canada chưa? Bình luận nhé!"),
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
print("V011_PROBE_DONE")
