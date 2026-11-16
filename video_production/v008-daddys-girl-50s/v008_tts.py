"""v008 TTS — probe risky words + full script synthesis (MMS-TTS, speaking_rate 0.92).

Script: "Con gai cua bo" (130 words per script file, F7, 50s). Voice =
facebook/mms-tts-vie on CUDA, sentence/clause-by-clause, joined with
short pauses (round-2 scheme: 0.3s after hook, 0.4s between beats,
0.6s before the payoff line, 0.15s micro-pause at clause splits).
The 0.6s pause sits at the END of beat3 (before payoff) and the BGM
dips to 0.0 there in assemble — same pattern as v004's 0.5s silence.

Probe words (script file): "Na", "phang phac", "doi", "ra roi".
Fallbacks (script-authorized, apply ONLY if a probe clearly fails):
  "Na"      -> "Be" (and fix the on-screen name too)
  "phang phac" -> "im lang han" (v005 precedent: Whisper hearing
                  "phan phat" counts as OK — keep the word)
  "doi"     -> "gian, khong them noi voi ai" in beat 2 + fix payoff
  "ra roi"  -> "met lam"

Writes: voice.wav (full), segments/<beat>.wav, timing.json (beat AND
clause starts/durations/words/wpm + total), probe results printed.
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
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v008_tts"

# (beat, [(clause spoken text, pause_after_s), ...])
# Spoken text: em-dashes replaced by commas (MMS reads them oddly);
# captions keep the script's original punctuation.
BEATS = [
    ("hook", [
        ("Con gái làm vỡ lọ hoa mẹ thích nhất, rồi bố về nhà.", 0.3),
    ]),
    ("beat1", [
        ("Mẹ mắng một câu, Na cúi đầu, nước mắt chực rơi.", 0.15),
        ("Cả nhà bỗng im phăng phắc, chỉ còn tiếng kim đồng hồ.", 0.4),
    ]),
    ("beat2", [
        ("Na giận dỗi, ôm gối ngồi một góc, không thèm nói với ai.", 0.15),
        ("Càng dỗi, càng mong có người đến dỗ.", 0.15),
        ("Nhưng chẳng ai đến cả.", 0.4),
    ]),
    ("beat3", [
        ("Bố đi làm về, mệt lắm, thấy con ngồi góc nhà thì bước vào thật khẽ.", 0.15),
        ("Bố không mắng, bố chỉ lặng im một lúc, rồi ngồi xuống bên cạnh.", 0.6),
    ]),
    ("payoff", [
        ("Rồi bố ôm con vào lòng, khẽ nói: con gái của bố đây rồi.", 0.15),
        ("Na bật cười, mọi giận dỗi tan hết trong một cái ôm.", 0.4),
    ]),
    ("cta", [
        ("Ai là con gái của bố? Bình luận nhé!", 0.0),
    ]),
]

EXPECTED_TEXT = " ".join(t for _, clauses in BEATS for t, _ in clauses)

PROBES = [
    ("na", "Na cúi đầu, nước mắt chực rơi.", "Na"),
    ("phang", "Cả nhà bỗng im phăng phắc.", "phăng phắc"),
    ("doi", "Na giận dỗi, ôm gối ngồi một góc.", "dỗi"),
    ("buoc", "thấy con ngồi góc nhà thì bước vào thật khẽ.", "bước vào"),
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
    # "phang phac": v005 precedent — Whisper hearing "phan phat" counts as OK.
    # Whisper also renders it toneless ("phang phac") — that counts too.
    if name == "phang":
        ok = any(s in heard.lower() for s in ("phăng phắc", "phan phát", "phang phác"))
    elif name == "buoc":
        ok = ("bước" in heard.lower()) and ("vào" in heard.lower())
    else:
        ok = target.lower() in heard.lower()
    probe_ok[name] = ok
    print(f"probe {name} ({target}): {'OK' if ok else 'FAIL'} | heard: {heard}", flush=True)

# --- FULL synthesis ---
print("\n=== FULL ===", flush=True)
parts = []
timing = []
clauses_out = []
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
        clauses_out.append({"beat": beat, "start_s": round(t, 3),
                            "end_s": round(t + dur, 3), "text": text,
                            "words": nwords})
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
               "overall_wpm": round(total_words / total_s * 60, 1),
               "clauses": clauses_out})
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
print("V008_TTS_DONE", flush=True)
