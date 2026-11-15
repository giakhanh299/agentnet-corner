import glob
import os
import time
import sys

# Windows console is cp1252: Vietnamese diacritics crash print(). Force UTF-8.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ctranslate2 (faster-whisper's engine) loads cuBLAS via the DLL search path.
# torch 2.11 keeps its CUDA DLLs in site-packages\torch\lib (there is NO
# site-packages\nvidia dir in this install), which is NOT on the DLL search
# path for other packages. Register it before importing faster_whisper,
# otherwise: RuntimeError: Library cublas64_12.dll is not found.
_site = os.path.normpath(os.path.join(os.path.dirname(sys.executable), "..", "Lib", "site-packages"))
_torch_lib = os.path.join(_site, "torch", "lib")
if os.path.isdir(_torch_lib):
    os.add_dll_directory(_torch_lib)
for _d in glob.glob(os.path.join(_site, "nvidia", "*", "bin")):
    os.add_dll_directory(_d)

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

# NOTE: audio is decoded with soundfile and passed as a numpy array, NOT as a
# file path. faster-whisper 1.2.1 calls av.open(..., metadata_errors="ignore")
# which av 19 removed (TypeError), so the file-path route is broken on this
# venv. The numpy route bypasses av entirely. Input must be 16 kHz mono
# float32 (made with ffmpeg: -ar 16000 -ac 1).
AUDIO = r"C:\Users\w\agentnet-corner\ai-stack\ep001_voice_16k.wav"
OUT = r"C:\Users\w\agentnet-corner\ai-stack\ep001_fw_transcript.txt"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "large-v3"

t0 = time.time()
print(f"Loading model {MODEL} (device=cuda, compute_type=float16)...", flush=True)
model = WhisperModel(MODEL, device="cuda", compute_type="float16")
t_load = time.time() - t0
print(f"Model loaded in {t_load:.1f}s", flush=True)

audio, sr = sf.read(AUDIO, dtype="float32")
assert sr == 16000, f"expected 16000 Hz, got {sr}"
print(f"Audio: {len(audio) / sr:.1f}s, {sr} Hz, shape {audio.shape}", flush=True)

t1 = time.time()
segments, info = model.transcribe(audio, language="vi", beam_size=5)
print(f"Detected language: {info.language} (p={info.language_probability:.2f}), duration={info.duration:.1f}s", flush=True)
lines = []
for seg in segments:
    line = f"[{seg.start:.2f}-{seg.end:.2f}] {seg.text.strip()}"
    print(line, flush=True)
    lines.append(line)
t_trans = time.time() - t1
print(f"Transcription took {t_trans:.1f}s for {info.duration:.1f}s audio (RTF {t_trans / info.duration:.2f}x)", flush=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(f"Saved to {OUT}", flush=True)
print(f"TOTAL {time.time() - t0:.1f}s (load {t_load:.1f}s + transcribe {t_trans:.1f}s)", flush=True)
