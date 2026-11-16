"""VieNeu-TTS v3 Turbo test — same 3 sentences as voice-compare rounds 1-3.
Voice: Mai Anh (female preset). Pauses: 0.3s after hook, 0.4s at the comma
split inside sentence 2, 0.6s before payoff (round-2 scheme).
Output: 48 kHz float32 from SDK -> saved as vieneu_48k.wav, then resampled
to 16 kHz mono vieneu.wav for the Whisper check (same as MMS samples).
"""
import sys
import time

import numpy as np
import soundfile as sf

from vieneu import Vieneu

OUTDIR = "/home/hatch/workspace/agentnet-corner/video_production/voice-compare-20261116"
VOICE = "Mai Anh"
SR = 48000

# (clause text, gap_after_s)
SEGMENTS = [
    ("Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?", 0.3),
    ("Thủy thủ viết tất cả vào sổ nhật ký của tàu,", 0.4),
    ("gọi là sổ log.", 0.6),
    ("Đăng nhập là ký tên vào sổ log của tàu.", 0.0),
]

t0 = time.time()
print("Loading Vieneu() ...", flush=True)
tts = Vieneu()
print(f"Loaded in {time.time() - t0:.1f}s", flush=True)
print("Preset voices:", len(tts.list_preset_voices()), flush=True)

parts = []
timing = []
t_cur = 0.0
total_words = 0
speech_s = 0.0
for text, gap_after in SEGMENTS:
    s0 = time.time()
    audio = tts.infer(text, voice=VOICE)
    synth_s = time.time() - s0
    audio = np.asarray(audio, dtype=np.float32)
    dur = len(audio) / SR
    words = len(text.split())
    total_words += words
    speech_s += dur
    print(f"seg {dur:.2f}s audio, {words} words, {words/dur*60:.0f} wpm, synth {synth_s:.2f}s (RTF {synth_s/dur:.2f}): {text}", flush=True)
    timing.append((text, t_cur, dur, words))
    parts.append(audio)
    t_cur += dur
    if gap_after > 0:
        parts.append(np.zeros(int(gap_after * SR), dtype=np.float32))
        t_cur += gap_after

full = np.concatenate(parts)
total_s = len(full) / SR
sf.write(f"{OUTDIR}/vieneu_48k.wav", full, SR)
print(f"Saved vieneu_48k.wav: {total_s:.2f}s total ({speech_s:.2f}s speech + {total_s - speech_s:.2f}s pauses), "
      f"{total_words} words, overall {total_words/total_s*60:.0f} wpm, speech-only {total_words/speech_s*60:.0f} wpm", flush=True)
print(f"TOTAL wall (incl. model load): {time.time() - t0:.1f}s", flush=True)
with open(f"{OUTDIR}/vieneu_timing.txt", "w", encoding="utf-8") as f:
    for text, start, dur, words in timing:
        f.write(f"{start:.2f}-{start+dur:.2f} ({words} words, {words/dur*60:.0f} wpm) {text}\n")
    f.write(f"TOTAL {total_s:.2f}s, {total_words} words, overall {total_words/total_s*60:.0f} wpm, speech-only {total_words/speech_s*60:.0f} wpm\n")
print("VIENEU_DONE")
