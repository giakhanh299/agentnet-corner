"""V012 probe check - faster-whisper large-v3 in .venv-ai (CUDA).
Transcribes each v012 probe wav and scores word accuracy vs expected.
"""
import difflib
import glob
import json
import os
import re
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

OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v012"
with open(os.path.join(OUTDIR, "v012_probe_manifest.json"), encoding="utf-8") as f:
    manifest = json.load(f)

print("Loading faster-whisper large-v3 ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")


def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()


for item in manifest:
    wav = item["wav"]
    audio, sr = sf.read(wav, dtype="float32")
    if sr != 16000:
        # resample 48k -> 16k via librosa-free linear approach: use soundfile + numpy
        import numpy as np
        idx = np.linspace(0, len(audio) - 1, int(len(audio) * 16000 / sr)).astype(int)
        audio = audio[idx]
        sr = 16000
    segments, _ = wm.transcribe(audio, language="vi", beam_size=5)
    heard = " ".join(s.text.strip() for s in segments)
    E, H = tokens(item["text"]), tokens(heard)
    sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    matched_idx = set()
    for b in sm.get_matching_blocks():
        matched_idx.update(range(b.a, b.a + b.size))
    missed = [E[i] for i in range(len(E)) if i not in matched_idx]
    pct = matched / len(E) * 100 if E else 0
    print(f"{item['name']}: {matched}/{len(E)} = {pct:.1f}% :: expected: {item['text']} :: heard: {heard} :: missed: {missed}", flush=True)
print("V012_PROBE_CHECK_DONE")
