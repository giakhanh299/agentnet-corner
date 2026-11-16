"""V012 full-voice Whisper check - faster-whisper large-v3 in .venv-ai.
Transcribes the SLOWED voice (16 kHz copy) and scores vs the script.
Target >= 75%.
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
with open(os.path.join(OUTDIR, "v012_units.json"), encoding="utf-8") as f:
    meta = json.load(f)
EXPECTED = " ".join(u["clause"] for u in meta["units"])

print("Loading faster-whisper large-v3 ...", flush=True)
wm = WhisperModel("large-v3", device="cuda", compute_type="float16")
audio, sr = sf.read(os.path.join(OUTDIR, "v012_voice_16k.wav"), dtype="float32")
assert sr == 16000
segments, _ = wm.transcribe(audio, language="vi", beam_size=5)
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


E, H = tokens(EXPECTED), tokens(heard)
sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
matched = sum(b.size for b in sm.get_matching_blocks())
matched_idx = set()
for b in sm.get_matching_blocks():
    matched_idx.update(range(b.a, b.a + b.size))
missed = [E[i] for i in range(len(E)) if i not in matched_idx]
print(f"Expected ({len(E)} words): {EXPECTED}", flush=True)
print(f"Heard    ({len(H)} words): {heard}", flush=True)
print(f"TTS tone check: {matched}/{len(E)} words heard correctly = {matched/len(E)*100:.1f}%", flush=True)
print(f"Missed/misheard words: {missed}", flush=True)
with open(os.path.join(OUTDIR, "v012_fw_segments.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(seg_lines) + "\n")
with open(os.path.join(OUTDIR, "v012_fw_heard.txt"), "w", encoding="utf-8") as f:
    f.write(heard + "\n")
print("V012_TTS_CHECK_DONE")
