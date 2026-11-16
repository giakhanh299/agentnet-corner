"""Transcribe the 3 'giau' probe variants with faster-whisper large-v3 (PC, .venv-ai)."""
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_site = os.path.normpath(os.path.join(os.path.dirname(sys.executable), "..", "Lib", "site-packages"))
_torch_lib = os.path.join(_site, "torch", "lib")
if os.path.isdir(_torch_lib):
    os.add_dll_directory(_torch_lib)
for _d in glob.glob(os.path.join(_site, "nvidia", "*", "bin")):
    os.add_dll_directory(_d)

import soundfile as sf
from faster_whisper import WhisperModel

OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v014_tts"
print("Loading faster-whisper large-v3 ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
for name in ["giau_take1", "giau_take2", "giau_se"]:
    wav = os.path.join(OUTDIR, f"v014_{name}_16k.wav")
    audio, sr = sf.read(wav, dtype="float32")
    segments, _info = wm.transcribe(audio, language="vi", beam_size=5)
    heard = " ".join(s.text.strip() for s in segments)
    print(f"{name}: heard: {heard}", flush=True)
print("V014_PROBE_GIAU_CHECK_DONE")
