"""V012 probe - VieNeu-TTS v3 Turbo, preset "Mai Anh", on the PC.

Probes the script's risky words with VieNeu + saves one wav per probe
sentence. A separate check script (faster-whisper large-v3 in .venv-ai)
scores each wav. Fallbacks from the script if a probe fails:
  "mot tram sau muoi lam" -> "hon mot tram tu"
  "Bin" -> "Mit"
  "di dao" -> "di choi" (payoff word, must be right)
  "om dien thoai" -> "cam dien thoai"
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import soundfile as sf

from vieneu import Vieneu

VOICE = "Mai Anh"
SR = 48000
OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v012"
os.makedirs(OUTDIR, exist_ok=True)

PROBES = [
    ("hook", "Ch\u00f3 nh\u00e0 b\u1ea1n hi\u1ec3u \u0111\u01b0\u1ee3c bao nhi\u00eau t\u1eeb c\u1ee7a b\u1ea1n?"),
    ("p165", "Trung b\u00ecnh, m\u1ed9t ch\u00fa ch\u00f3 hi\u1ec3u kho\u1ea3ng m\u1ed9t tr\u0103m s\u00e1u m\u01b0\u01a1i l\u0103m t\u1eeb."),
    ("pbin", "T\u00f4i l\u00e0 Bin."),
    ("pom", "T\u1ed1i ch\u1ee7 v\u1ec1, ch\u1ec9 \u00f4m \u0111i\u1ec7n tho\u1ea1i."),
    ("pdao", "Hai t\u1eeb \u0111\u00f3 l\u00e0: \u0111i d\u1ea1o."),
]

t0 = time.time()
print("Loading Vieneu() ...", flush=True)
tts = Vieneu()
print(f"Loaded in {time.time() - t0:.1f}s", flush=True)
print("Preset voices:", len(tts.list_preset_voices()), flush=True)
print("Mai Anh in presets:", "Mai Anh" in [str(v) for v in tts.list_preset_voices()], flush=True)

manifest = []
for name, text in PROBES:
    s0 = time.time()
    audio = tts.infer(text, voice=VOICE)
    audio = np.asarray(audio, dtype=np.float32)
    dur = len(audio) / SR
    words = len(text.split())
    out = os.path.join(OUTDIR, f"v012_probe_{name}.wav")
    sf.write(out, audio, SR)
    print(f"{name}: {dur:.2f}s, {words} words, {words/dur*60:.0f} wpm, synth {time.time()-s0:.2f}s :: {text}", flush=True)
    manifest.append({"name": name, "text": text, "wav": out, "dur": round(dur, 2)})

with open(os.path.join(OUTDIR, "v012_probe_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(f"TOTAL {time.time() - t0:.1f}s")
print("V012_PROBE_DONE")
