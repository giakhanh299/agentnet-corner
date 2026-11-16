"""faster-whisper large-v3 check for V014 VieNeu units (PC, .venv-ai).

Transcribes each v014_unit_<name>_16k.wav, compares tokens vs the expected
text from v014_units.json, prints heard text + match % + missed words.
Also writes v014_fw_segments.txt and v014_fw_heard.txt.
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

OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v014_tts"

with open(os.path.join(OUTDIR, "v014_units.json"), encoding="utf-8") as f:
    UNITS = json.load(f)

print("Loading faster-whisper large-v3 ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")

def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()

seg_lines = []
all_expected = []
all_heard = []
for u in UNITS:
    name = u["unit"]
    wav = os.path.join(OUTDIR, f"v014_unit_{name}_16k.wav")
    audio, sr = sf.read(wav, dtype="float32")
    assert sr == 16000
    segments, _info = wm.transcribe(audio, language="vi", beam_size=5)
    heard_parts = []
    for s in segments:
        line = f"[{s.start:.2f}-{s.end:.2f}] {s.text.strip()}"
        seg_lines.append(f"{name} {line}")
        heard_parts.append(s.text.strip())
    heard = " ".join(heard_parts)
    expected = u["text"]
    E, H = tokens(expected), tokens(heard)
    sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    matched_idx = set()
    for b in sm.get_matching_blocks():
        matched_idx.update(range(b.a, b.a + b.size))
    missed = [E[i] for i in range(len(E)) if i not in matched_idx]
    print(f"{name}: {matched}/{len(E)} = {matched / len(E) * 100:.1f}% :: heard: {heard}", flush=True)
    print(f"   missed: {missed}", flush=True)
    all_expected.extend(E)
    all_heard.extend(H)

sm = difflib.SequenceMatcher(a=all_expected, b=all_heard, autojunk=False)
matched = sum(b.size for b in sm.get_matching_blocks())
print(f"TOTAL: {matched}/{len(all_expected)} = {matched / len(all_expected) * 100:.1f}%", flush=True)
with open(os.path.join(OUTDIR, "v014_fw_segments.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(seg_lines) + "\n")
with open(os.path.join(OUTDIR, "v014_fw_heard.txt"), "w", encoding="utf-8") as f:
    f.write(" ".join(all_heard) + "\n")
print("V014_FW_CHECK_DONE")
