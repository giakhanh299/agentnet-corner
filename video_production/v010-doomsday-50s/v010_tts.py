"""V010 full voice - MMS-TTS (facebook/mms-tts-vie) on the PC.
TAKE 3: per-beat speaking_rate (take 2: hook 151, beat1 171, beat2 157,
beat3 155, payoff 174 wpm; total 54.40s, speech-only 161 wpm; Whisper
84.7% - same as take 1. Take 2's hook garbled "video nay" per Whisper
("di eo lai") at rate 1.0, and beat1/payoff ran hot at 171/174).
Take 3: hook 0.95, beat1 0.95, beat2 0.85, beat3 0.95, payoff 0.90.
Target: every beat ~150-165 wpm speech-only, total ~55s. Take 2's
voice.wav is kept on the PC as v010_voice_take2.wav - fall back to it
if take 3 is worse.

Script (137 words, 5 beats) from
scripts-batch-20261116/script_v010-doomsday-50s.md.
Pause scheme: 0.3s after hook, 0.4s between beats and at clause splits,
0.6s before payoff (NOT the old fixed 1.2s).

PROBE RESULTS (2026-11-16, PC, rate 0.92, faster-whisper large-v3):
  P1 "tan the" 82.4% - keyword heard correctly; missed are Whisper's
     "muoi ba"->"13" normalization + "video"->"gieo" (Whisper). KEPT.
  P2 "vo cung" 95.0% - heard correctly; only "do"->"no". KEPT.
  P3 "dat dinh" 75.0% - heard correctly; missed are "mot chin sau ba"
     ->"1963" normalization. KEPT.
  P4 "truong nhom" 100.0%. KEPT.
  All 4 probe words PASS - no fallback swaps needed.
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v010"
OUT = os.path.join(OUTDIR, "v010_voice.wav")
SEG_OUT = os.path.join(OUTDIR, "v010_fw_segments.txt")
HEARD_OUT = os.path.join(OUTDIR, "v010_fw_heard.txt")
TIMING_OUT = os.path.join(OUTDIR, "v010_beat_timing.txt")

# (beat name, [clauses], gap_after_s, speaking_rate)
BEATS = [
    ("hook", ["Ngày mười ba vừa rồi, thế giới phải tận thế. Nhưng bạn vẫn đang xem video này."], 0.3, 0.95),
    ("beat1", ["Tin đồn đó bắt đầu từ một bài báo thật, đăng từ năm một chín sáu mươi.",
               "Tựa bài báo ghi rõ: Ngày tận thế, thứ sáu, ngày mười ba tháng mười một."], 0.4, 0.95),
    ("beat2", ["Ba nhà khoa học tính rằng dân số tăng nhanh mãi, rồi chạm tới vô cùng vào đúng năm đó.",
               "Nhưng họ cũng không tin, vì đó là sinh nhật của ông trưởng nhóm."], 0.4, 0.85),
    ("beat3", ["Nhưng thực tế khác hẳn.",
               "Tốc độ tăng dân số đạt đỉnh từ năm một chín sáu ba rồi giảm dần.",
               "Hôm nay thế giới có hơn tám tỉ người, không phải hàng trăm tỉ."], 0.6, 0.95),
    ("payoff", ["Bài học: kéo quá khứ ra tương lai, toán cũng nói dối. Bạn nghĩ sao? Bình luận nhé!"], 0.0, 0.90),
]
CLAUSE_GAP = 0.4
EXPECTED_TEXT = " ".join(" ".join(clauses) for _, clauses, _, _ in BEATS)


def synth(model, tok, device, text, rate):
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs, speaking_rate=rate).waveform[0].cpu().numpy()
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
for name, clauses, gap_after, rate in BEATS:
    start = t_cur
    beat_words = 0
    beat_speech = 0.0
    for ci, clause in enumerate(clauses):
        w = synth(model, tok, device, clause, rate)
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
    print(f"{name}: start {start:.2f}s, {beat_speech:.2f}s speech, {beat_words} words, {wpm:.0f} wpm (rate {rate})", flush=True)
    timing.append(f"{name}: {start:.2f}-{t_cur:.2f} ({beat_words} words, {wpm:.0f} wpm, rate {rate})")
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
print("V010_TTS_DONE")
