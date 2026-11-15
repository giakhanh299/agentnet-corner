"""Round 3 — Coqui VITS Vietnamese (multilingual-tts/VITS-OpenBible-Vietnamese).

Grapheme-based VITS (use_phonemes=False), 2 speakers, 22050 Hz, CC-BY-SA-4.0.
Model file ~998 MB (under the 3 GB threshold). Runs in .venv-vits (Python
3.10 — Coqui TTS 0.22 requires Python <3.12, so the 3.12 venvs can't use it).
Synthesizes the same 3 test sentences, resamples to 16 kHz mono, joins with
0.6s / 0.8s gaps like rounds 1-2. Whisper check is a separate step
(voice_whisper_check.py, .venv-ai).
"""
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

MODEL_DIR = r"C:\Users\w\agentnet-corner\ai-stack\voice_compare\vits_openbible"
OUT = r"C:\Users\w\agentnet-corner\ai-stack\voice_compare"
os.makedirs(OUT, exist_ok=True)

SENTENCES = [
    "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?",
    "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log.",
    "Đăng nhập là ký tên vào sổ log của tàu.",
]
GAPS = [0.6, 0.8]

from TTS.api import TTS

t0 = time.time()
tts = TTS(
    model_path=os.path.join(MODEL_DIR, "model_last.pth"),
    config_path=os.path.join(MODEL_DIR, "config.json"),
    gpu=True,
)
print(f"Model loaded in {time.time() - t0:.1f}s", flush=True)
print(f"Speakers: {tts.speakers}", flush=True)

import soundfile as sf
import numpy as np


def synth_sentence(text, speaker, tag):
    raw = os.path.join(OUT, f"vits_{tag}_raw.wav")
    t1 = time.time()
    tts.tts_to_file(text=text, speaker=speaker, file_path=raw)
    data, sr = sf.read(raw, dtype="float32")
    dur = len(data) / sr
    nwords = len(text.split())
    print(f"{tag}: {dur:.2f}s, {nwords} words, {nwords/dur*60:.0f} wpm, synth {time.time()-t1:.1f}s", flush=True)
    # resample to 16 kHz mono via ffmpeg (Coqui output is 22050 Hz)
    wav16 = os.path.join(OUT, f"vits_{tag}.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", raw,
         "-ar", "16000", "-ac", "1", wav16],
        check=True)
    data16, sr16 = sf.read(wav16, dtype="float32")
    return data16, sr16


speakers = tts.speakers or [None]
for spk_idx, spk in enumerate(speakers[:2]):
    tag = f"spk{spk_idx}"
    parts = []
    try:
        for i, text in enumerate(SENTENCES):
            data, sr = synth_sentence(text, spk, f"{tag}_s{i+1}")
            parts.append(data)
            if i < 2:
                parts.append(np.zeros(int(GAPS[i] * sr), dtype=np.float32))
        joined = np.concatenate(parts)
        out = os.path.join(OUT, f"vits_openbible_{tag}.wav")
        sf.write(out, joined, 16000)
        print(f"speaker {spk!r} FINAL: {len(joined)/16000:.2f}s -> {out}", flush=True)
    except Exception as e:
        print(f"speaker {spk!r} FAILED: {type(e).__name__}: {e}", flush=True)
print("VITS_SYNTH_DONE", flush=True)
