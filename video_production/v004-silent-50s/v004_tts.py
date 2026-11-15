"""v004 TTS — probe risky words + full script synthesis (MMS-TTS, speaking_rate 0.92).

Script: "Ong Tu sua giay" (130 words, F7, 50s). Voice = facebook/mms-tts-vie
on CUDA, sentence/clause-by-clause, joined with short pauses (round-2
scheme: 0.3s between sentences, 0.2s micro-pause at clause splits,
0.6s before the payoff line = the F7 0.5s silence, plus music dips there).

Probe words (script file): "Tu" (proper name), "luot", "sap".
If a probe word is misheard, the script file names replacements
("ong Ba" / "di qua" / "quay nho" or "goc sua giay") — report, do NOT
silently swap in the full synthesis.

Writes: voice.wav (full), segments/<beat>.wav, timing.json (beat
starts/durations/words/wpm + total), probe results printed.
Whisper large-v3 check on the full file + each probe sentence.
"""
import glob
import json
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
RATE = 0.92  # variant C (round 2): speech-only ~160 wpm, in the 150-165 zone
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v004_tts"

# (beat, [(clause spoken text, pause_after_s), ...])
# Spoken text: em-dashes replaced by commas (MMS reads them oddly);
# captions keep the script's original punctuation.
# Round 2 fixes (after the first run: 56.33s, over the 55s cap;
# "sạp" misread as "sạc"): "sạp" -> "quầy nhỏ" (script-authorized);
# short 2-word lead-in clauses merged into the following clause
# (MMS pads them slow: 90-97 wpm); micro-pauses 0.15s; 0.5s before payoff.
BEATS = [
    ("hook", [
        ("Mỗi ngày, hàng trăm người đi qua góc phố này.", 0.3),
    ]),
    ("beat1", [
        ("Ông Tư sửa giày ở góc phố này đã ba mươi năm.", 0.3),
        ("Người ta lướt qua mỗi ngày,", 0.15),
        ("không ai dừng lại,", 0.15),
        ("không ai hỏi tên ông,", 0.15),
        ("không ai nhớ mặt ông.", 0.3),
    ]),
    ("beat2", [
        ("Tối nào ông cũng đánh bóng một đôi giày nhỏ,", 0.15),
        ("của một người khách bỏ quên từ lâu, không bao giờ quay lại lấy.", 0.3),
        ("Ông để đôi giày trên quầy nhỏ, như đang đợi ai đó.", 0.3),
    ]),
    ("beat3", [
        ("Một chiều, một bé gái dừng lại,", 0.15),
        ("chỉ vào đôi giày nhỏ:", 0.15),
        ("Của ai vậy ông?", 0.3),
        ("Hôm sau, bé quay lại,", 0.15),
        ("tay cầm một bức vẽ:", 0.15),
        ("ông Tư ngồi sửa giày dưới ánh đèn vàng.", 0.5),
    ]),
    ("payoff", [
        ("Ông cười, lần đầu sau bao năm, có người nhìn thấy ông.", 0.3),
        ("Chỉ cần một người dừng lại.", 0.0),
    ]),
]

EXPECTED_TEXT = (
    "Mỗi ngày, hàng trăm người đi qua góc phố này. "
    "Ông Tư sửa giày ở góc phố này đã ba mươi năm. "
    "Người ta lướt qua mỗi ngày — không ai dừng lại, không ai hỏi tên ông, không ai nhớ mặt ông. "
    "Tối nào ông cũng đánh bóng một đôi giày nhỏ — của một người khách bỏ quên từ lâu, không bao giờ quay lại lấy. "
    "Ông để đôi giày trên quầy nhỏ, như đang đợi ai đó. "
    "Một chiều, một bé gái dừng lại, chỉ vào đôi giày nhỏ: Của ai vậy ông? "
    "Hôm sau, bé quay lại — tay cầm một bức vẽ: ông Tư ngồi sửa giày dưới ánh đèn vàng. "
    "Ông cười — lần đầu sau bao năm, có người nhìn thấy ông. "
    "Chỉ cần một người dừng lại."
)

PROBES = [
    ("tu", "Ông Tư sửa giày ở góc phố này.", "Tư"),
    ("luot", "Người ta lướt qua mỗi ngày.", "lướt"),
    ("quay", "Ông để đôi giày trên quầy nhỏ.", "quầy"),
]


def save_wav(path, audio):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())


def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()


def synth(model, tok, device, text):
    inputs = tok(text, return_tensors="pt").to(device)
    with torch.no_grad():
        w = model(**inputs, speaking_rate=RATE).waveform[0].cpu().numpy()
    return np.clip(w, -1, 1).astype(np.float32)


os.makedirs(os.path.join(OUTDIR, "segments"), exist_ok=True)
t0 = time.time()
print("Loading facebook/mms-tts-vie ...", flush=True)
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded on {device}", flush=True)

# --- Whisper (load once, use for probes + full check) ---
from faster_whisper import WhisperModel
import soundfile as sf
import difflib

wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
print("Whisper large-v3 loaded", flush=True)


def whisper_hear(path):
    audio, sr = sf.read(path, dtype="float32")
    assert sr == 16000
    segments, _ = wm.transcribe(audio, language="vi", beam_size=5)
    return " ".join(s.text.strip() for s in segments)


# --- PROBE: risky words first ---
print("\n=== PROBE ===", flush=True)
probe_ok = {}
for name, text, target in PROBES:
    w = synth(model, tok, device, text)
    p = os.path.join(OUTDIR, f"probe_{name}.wav")
    save_wav(p, w)
    heard = whisper_hear(p)
    ok = target.lower() in heard.lower()
    probe_ok[name] = ok
    print(f"probe {name} ({target}): {'OK' if ok else 'FAIL'} | heard: {heard}", flush=True)

# --- FULL synthesis ---
print("\n=== FULL ===", flush=True)
parts = []
timing = []
t = 0.0
total_words = 0
for beat, clauses in BEATS:
    beat_start = t
    beat_words = 0
    beat_audio = []
    for text, pause in clauses:
        w = synth(model, tok, device, text)
        dur = len(w) / SR
        nwords = len(text.split())
        beat_words += nwords
        print(f"  {beat}: '{text[:45]}' {dur:.2f}s, {nwords}w, {nwords / dur * 60:.0f} wpm", flush=True)
        beat_audio.append(w)
        if pause > 0:
            beat_audio.append(np.zeros(int(pause * SR), dtype=np.float32))
        t += dur + pause
    beat_wav = np.concatenate(beat_audio)
    save_wav(os.path.join(OUTDIR, "segments", f"{beat}.wav"), beat_wav)
    beat_dur = len(beat_wav) / SR
    timing.append({"beat": beat, "start_s": round(beat_start, 3),
                   "duration_s": round(beat_dur, 3), "words": beat_words,
                   "wpm": round(beat_words / beat_dur * 60, 1)})
    total_words += beat_words
    parts.append(beat_wav)

full = np.concatenate(parts)
save_wav(os.path.join(OUTDIR, "voice.wav"), full)
total_s = len(full) / SR
timing.append({"total_s": round(total_s, 3), "total_words": total_words,
               "overall_wpm": round(total_words / total_s * 60, 1)})
with open(os.path.join(OUTDIR, "timing.json"), "w", encoding="utf-8") as f:
    json.dump(timing, f, ensure_ascii=False, indent=2)
print(f"Saved voice.wav: {total_s:.2f}s total, {total_words} words, "
      f"overall {total_words / total_s * 60:.0f} wpm", flush=True)
if total_s > 55:
    print(f"WARNING: total {total_s:.1f}s exceeds the 40-55s window!", flush=True)

# --- Whisper check on the full file ---
heard = whisper_hear(os.path.join(OUTDIR, "voice.wav"))
E, H = tokens(EXPECTED_TEXT), tokens(heard)
sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
matched = sum(b.size for b in sm.get_matching_blocks())
matched_idx = set()
for b in sm.get_matching_blocks():
    matched_idx.update(range(b.a, b.a + b.size))
missed = [E[i] for i in range(len(E)) if i not in matched_idx]
print(f"\nWhisper full check: {matched}/{len(E)} = {matched / len(E) * 100:.1f}%", flush=True)
print(f"Heard: {heard}", flush=True)
print(f"Missed/misheard: {missed}", flush=True)

print(f"\nTOTAL {time.time() - t0:.1f}s", flush=True)
print("V004_TTS_DONE", flush=True)
