"""V011 full voice - MMS-TTS (facebook/mms-tts-vie) on the PC, speaking_rate 0.92.

Script (115 words after probe swaps, 5 beats) from
scripts-batch-20261116/script_v011-canada-lakes-45s.md.
Voice plan: round-2 variant C (speaking_rate 0.92, speech-only ~160 wpm,
in the 150-165 safe zone). Pause scheme: 0.3s after hook, 0.4s between
beats and at clause splits, 0.6s before payoff (NOT the old fixed 1.2s).

PROBE SWAPS (2026-11-16, PC, 4 probe rounds):
- "Canada" FAIL (P1: heard "ca la"; P4: heard "Kalala") - MMS cannot
  say the English word. Script fallback was "nuoc nay" / "toi do", but
  that never names the country in voice (beat 1 answers "nuoc nao?").
  BETTER FIX (P7/P8, probe round 4): Vietnamese transliteration
  "Ca-na-da" - Whisper hears it as "Canada" in BOTH sentences (P7, P8).
  Used consistently in beat 1 + payoff. Captions use "Canada".
- "bang ha" FAIL (P2: heard "bang ha" tone swap ha->ha) -> "bang tuyet
  khong lo" (P5, 94.4%, heard correctly).
- "ho trung" FAIL (P2: heard "ho trung" tone swap ung->ung) -> "ho sau"
  (P5, 94.4%, heard correctly).
- "cao xoi" - missed twice ("cao xu" / "cao xep") but the fallback
  "cao nat" scored WORSE (P6, 83.3% vs P5 94.4% for the same sentence,
  different misses) - run-to-run Whisper noise, not an MMS failure.
  KEPT "cao xoi".
- "Thuong" PASS (P3, 78.6%; "Thuong" itself heard - misses were
  "Rieng"->"kieng", "ngot"->"mot", "cau"->"cong" Whisper confusions).
  KEPT. "Trai Dat" PASS (P4, 94.7%). KEPT.
- "Muoi" first-word issue (P2 heard "Nguoi") - known first-word
  artifact (v003 "Cap"->"Cac", v006 "Nuoc"->"Dat"); on-screen label
  "BANG HA - 10.000 NAM TRUOC" carries it. KEPT.

Word count: 113 -> 115 ("bang ha" 2w -> "bang tuyet khong lo" 4w).
Captions use "Canada" (correct spelling, what the listener hears);
synthesis input uses "Ca-na-da". Whisper check expected text uses
"Canada" (Whisper outputs "Canada" for the spoken "Ca-na-da").

Beats (start times are printed + saved for the video assembly / captions):
  hook   0-5s    "Mot nuoc giu hon nua so ho tren ca hanh tinh. Doan thu xem nuoc nao?"
  beat1  5-15s   "Do la Ca-na-da. Hon sau muoi phan tram so ho tren the gioi nam o day,
                  hon ba muoi mot nghin ho lon."
  beat2  15-28s  "Vi sao nhieu den vay? Muoi nghin nam truoc, bang tuyet khong lo cao
                  xoi mat dat, de lai hang trieu ho sau. Bang tan, nuoc dong lai
                  thanh ho."
  beat3  28-38s  "Trong do co ho Lon, cum ho nuoc ngot lon nhat the gioi. Rieng ho
                  Thuong giu gan mot phan nam luong nuoc ho ngot toan cau."
  payoff 38-45s  "Mot nuoc, hon nua so ho cua ca Trai Dat. Ban da tung toi Ca-na-da
                  chua? Binh luan nhe!"
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
OUT = os.path.join(OUTDIR, "v011_voice.wav")
SEG_OUT = os.path.join(OUTDIR, "v011_fw_segments.txt")
HEARD_OUT = os.path.join(OUTDIR, "v011_fw_heard.txt")
TIMING_OUT = os.path.join(OUTDIR, "v011_beat_timing.txt")

# (beat name, [clauses], gap_after_s)
BEATS = [
    ("hook", ["Một nước giữ hơn nửa số hồ trên cả hành tinh.",
              "Đoán thử xem nước nào?"], 0.3),
    ("beat1", ["Đó là Ca-na-đa.",
               "Hơn sáu mươi phần trăm số hồ trên thế giới nằm ở đây, hơn ba mươi mốt nghìn hồ lớn."], 0.4),
    ("beat2", ["Vì sao nhiều đến vậy?",
               "Mười nghìn năm trước, băng tuyết khổng lồ cào xới mặt đất, để lại hàng triệu hố sâu.",
               "Băng tan, nước đọng lại thành hồ."], 0.4),
    ("beat3", ["Trong đó có hồ Lớn, cụm hồ nước ngọt lớn nhất thế giới.",
               "Riêng hồ Thượng giữ gần một phần năm lượng nước hồ ngọt toàn cầu."], 0.6),
    ("payoff", ["Một nước, hơn nửa số hồ của cả Trái Đất.",
                "Bạn đã từng tới Ca-na-đa chưa? Bình luận nhé!"], 0.0),
]
CLAUSE_GAP = 0.4
# Expected text for the Whisper check: "Canada" (what Whisper hears for
# the spoken "Ca-na-da"), all other words as spoken.
EXPECTED_TEXT = " ".join(" ".join(clauses) for _, clauses, _ in BEATS).replace("Ca-na-đa", "Canada")


def synth(model, tok, device, text):
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs, speaking_rate=RATE).waveform[0].cpu().numpy()
    return np.clip(w, -1, 1).astype(np.float32)


t0 = time.time()
print("Loading facebook/mms-tts-vie ...", flush=True)
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded on {device}", flush=True)
os.makedirs(OUTDIR, exist_ok=True)

parts = []
timing = []
t_cur = 0.0
total_words = 0
speech_s = 0.0
for name, clauses, gap_after in BEATS:
    start = t_cur
    beat_words = 0
    beat_speech = 0.0
    for ci, clause in enumerate(clauses):
        w = synth(model, tok, device, clause)
        dur = len(w) / SR
        beat_speech += dur
        beat_words += len(clause.split())
        parts.append(w)
        t_cur += dur
        if ci < len(clauses) - 1:
            parts.append(np.zeros(int(CLAUSE_GAP * SR), dtype=np.float32))
            t_cur += CLAUSE_GAP
    speech_s += beat_speech
    total_words += beat_words
    wpm = beat_words / beat_speech * 60
    print(f"{name}: start {start:.2f}s, {beat_speech:.2f}s speech, {beat_words} words, {wpm:.0f} wpm", flush=True)
    timing.append(f"{name}: {start:.2f}-{t_cur:.2f} ({beat_words} words, {wpm:.0f} wpm)")
    if gap_after > 0:
        parts.append(np.zeros(int(gap_after * SR), dtype=np.float32))
        t_cur += gap_after

full = np.concatenate(parts)
total_s = len(full) / SR
with wave.open(OUT, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"Saved {OUT}: {total_s:.2f}s total ({speech_s:.2f}s speech + {total_s - speech_s:.2f}s pauses), "
      f"{total_words} words, overall {total_words/total_s*60:.0f} wpm, speech-only {total_words/speech_s*60:.0f} wpm", flush=True)
with open(TIMING_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(timing) + f"\nTOTAL {total_s:.2f}s, {total_words} words, overall {total_words/total_s*60:.0f} wpm\n")

# --- Whisper self-check on the whole file ---
from faster_whisper import WhisperModel
import soundfile as sf
import difflib

print("Loading faster-whisper large-v3 ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
audio, sr = sf.read(OUT, dtype="float32")
assert sr == 16000
segments, info = wm.transcribe(audio, language="vi", beam_size=5)
seg_lines = []
heard_parts = []
for s in segments:
    line = f"[{s.start:.2f}-{s.end:.2f}] {s.text.strip()}"
    print(line, flush=True)
    seg_lines.append(line)
    heard_parts.append(s.text.strip())
heard = " ".join(heard_parts)


def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()


E, H = tokens(EXPECTED_TEXT), tokens(heard)
sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
matched = sum(b.size for b in sm.get_matching_blocks())
matched_idx = set()
for b in sm.get_matching_blocks():
    matched_idx.update(range(b.a, b.a + b.size))
missed = [E[i] for i in range(len(E)) if i not in matched_idx]
print(f"Expected ({len(E)} words): {EXPECTED_TEXT}", flush=True)
print(f"Heard    ({len(H)} words): {heard}", flush=True)
print(f"TTS tone check: {matched}/{len(E)} words heard correctly = {matched/len(E)*100:.1f}%", flush=True)
print(f"Missed/misheard words: {missed}", flush=True)
with open(SEG_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(seg_lines) + "\n")
with open(HEARD_OUT, "w", encoding="utf-8") as f:
    f.write(heard + "\n")
print(f"Saved segments to {SEG_OUT}, heard text to {HEARD_OUT}, timing to {TIMING_OUT}", flush=True)
print(f"TOTAL {time.time() - t0:.1f}s")
print("V011_TTS_DONE")
