#!/usr/bin/env python3
"""VieNeu-TTS v3 Turbo probes for V013 on the controller VPS.

Voice: "Mai Anh" (female preset) — the approved production voice.
Each risky word is tested in its real sentence + the script's fallback
sentence. Also synthesizes the bread-vendor call sample ("Ai banh mi
khong?") with the same voice (script says MMS; PC is unreachable from
this session, so VieNeu is the fallback — the parent may swap it for an
MMS take on the PC; see v013_production_notes.md).

One process only: VieNeu cold load is ~197s on this VPS.
Output: 48 kHz wav per probe + a JSON with durations.
Whisper check is done separately with whisper.cpp Base (weaker than
large-v3 on the PC — the parent MUST re-verify on the PC).
"""
import json
import os
import sys
import time

import numpy as np
import soundfile as sf

from vieneu import Vieneu

OUTDIR = "/home/hatch/workspace/agentnet-corner/video_production/v013-iconic-sounds-45s"
PROBE_DIR = os.path.join(OUTDIR, "probes")
os.makedirs(PROBE_DIR, exist_ok=True)
VOICE = "Mai Anh"
SR = 48000

# (name, text) — probe + fallback for each risky word (real diacritics kept)
PROBES = [
    ("p_chuongtruong", "Số năm: tiếng chuông trường."),
    ("p_chuongtruong_fb", "Số năm: tiếng chuông tan học."),
    ("p_deno", "Số bốn: tiếng xe máy đề nổ."),
    ("p_deno_fb", "Số bốn: tiếng xe máy nổ máy."),
    ("p_rao", "Số ba: tiếng rao bánh mì."),
    ("p_rao_fb", "Số ba: tiếng bán bánh mì."),
    ("p_cucgach", "Số hai: nhạc chuông điện thoại cục gạch."),
    ("p_cucgach_fb", "Số hai: nhạc chuông điện thoại cũ."),
    ("p_modem", "Số một: tiếng modem quay số."),
    ("p_modem_fb", "Số một: tiếng quay số."),
]

VENDOR = ("vendor_call", "Ai bánh mì không?")

t0 = time.time()
print("Loading Vieneu() ...", flush=True)
tts = Vieneu()
print(f"Loaded in {time.time() - t0:.1f}s", flush=True)

results = {}
for name, text in PROBES + [VENDOR]:
    s0 = time.time()
    audio = tts.infer(text, voice=VOICE)
    audio = np.asarray(audio, dtype=np.float32)
    dur = len(audio) / SR
    print(f"{name}: {dur:.2f}s, synth {time.time() - s0:.1f}s :: {text}", flush=True)
    sf.write(os.path.join(PROBE_DIR, name + ".wav"), audio, SR)
    results[name] = {"text": text, "dur": round(dur, 2)}

with open(os.path.join(PROBE_DIR, "probe_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"PROBE DONE in {time.time() - t0:.1f}s", flush=True)
