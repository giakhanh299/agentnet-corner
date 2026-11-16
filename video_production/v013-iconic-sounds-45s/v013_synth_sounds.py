#!/usr/bin/env python3
"""V013 sound samples: self-synthesize Gran Vals ringtone + dial-up modem,
trim + loudness-normalize all 5 samples to a common level.

Sources:
- bell: Openverse CC0 "School Bell" by civvy (Freesound 620392), 7.80s
  -> loudest 2s window.
- motorbike: Openverse CC0 "MotorCycle Engine Start" (Freesound 679416),
  2.86s -> first 2s (ignition at start).
- modem: Openverse CC0 "MODEM_3.aif" (Freesound 454649), 17.84s
  -> loudest 3s window (the handshake screech).
- ringtone: SELF-SYNTHESIZED Gran Vals (1902, Francisco Tarrega, public
  domain) — the 13-note Nokia-tune phrase. NEVER a Nokia file.
- vendor call: VieNeu "Ai banh mi khong?" (see v013_probe.py) -> 2s.
- modem synth is a fallback only if the CC0 modem slice is unusable;
  the CC0 slice is preferred (real recording).

All 5 outputs: 48 kHz mono wav, loudnorm single-pass to I=-23 LUFS,
TP=-2. The PC mix sets the final level vs voice (task: -18 to -24 dB
below voice; script says samples at voice level — conflict flagged in
v013_production_notes.md; the mix script implements the task target).
"""
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

BASE = "/home/hatch/workspace/agentnet-corner/video_production/v013-iconic-sounds-45s"
SND = os.path.join(BASE, "sounds")
SR = 48000

def run(cmd):
    print("+ " + " ".join(cmd), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f"FAILED rc={r.returncode}: {' '.join(cmd[:3])}")
    return r

def decode(mp3, wav):
    run(["ffmpeg", "-v", "error", "-y", "-i", mp3,
         "-ar", str(SR), "-ac", "1", wav])

def loudest_window(x, sr, win_s):
    """Start index of the loudest win_s window (RMS)."""
    w = int(win_s * sr)
    if len(x) <= w:
        return 0
    # RMS in 0.1s hops
    hop = int(0.1 * sr)
    best_i, best_e = 0, -1.0
    for i in range(0, len(x) - w + 1, hop):
        e = float(np.mean(x[i:i + w] ** 2))
        if e > best_e:
            best_e, best_i = e, i
    return best_i

def trim_and_norm(src_wav, out_wav, win_s, mode="loudest"):
    x, sr = sf.read(src_wav, dtype="float32")
    assert sr == SR, sr
    if mode == "loudest":
        i0 = loudest_window(x, sr, win_s)
    else:  # first
        i0 = 0
    seg = x[i0:i0 + int(win_s * sr)]
    tmp = out_wav + ".tmp.wav"
    sf.write(tmp, seg, SR)
    run(["ffmpeg", "-v", "error", "-y", "-i", tmp,
         "-af", "loudnorm=I=-23:TP=-2:LRA=11", "-ar", str(SR), "-ac", "1",
         out_wav])
    os.remove(tmp)
    y, _ = sf.read(out_wav, dtype="float32")
    print(f"{os.path.basename(out_wav)}: {len(y)/SR:.2f}s, peak {np.max(np.abs(y)):.3f}, "
          f"rms {float(np.sqrt(np.mean(y**2))):.4f} (src window at {i0/SR:.2f}s)", flush=True)

# ---------- 1. Gran Vals ringtone (self-synthesized) ----------
# 13-note phrase (Nokia tune), E5 D5 F#4 G4 | C5 B4 D4 E4 | B4 A4 D4 E4 | A4
NOTES = [  # (freq Hz, dur s)
    (659.25, 0.16), (587.33, 0.16), (369.99, 0.32), (392.00, 0.32),
    (523.25, 0.16), (493.88, 0.16), (293.66, 0.32), (329.63, 0.32),
    (493.88, 0.16), (440.00, 0.16), (293.66, 0.32), (329.63, 0.32),
    (440.00, 0.48),
]
parts = []
for f, d in NOTES:
    n = int(d * SR)
    t = np.arange(n) / SR
    # retro monophonic beep: sine + weak 2nd harmonic, fast attack, exp decay
    tone = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    env = np.exp(-t * 6.0)
    env[: int(0.005 * SR)] = np.linspace(0, 1, int(0.005 * SR))
    parts.append(tone * env)
ring = np.concatenate(parts).astype(np.float32)
ring = ring / np.max(np.abs(ring)) * 0.9
sf.write(os.path.join(SND, "ringtone_raw.wav"), ring, SR)
print(f"ringtone_raw.wav: {len(ring)/SR:.2f}s synthesized", flush=True)
trim_and_norm(os.path.join(SND, "ringtone_raw.wav"),
              os.path.join(SND, "sample_ringtone.wav"), 3.0, mode="first")

# ---------- 2. Dial-up modem handshake (self-synthesized, fallback) ----------
def tone(f, d, amp=0.5):
    n = int(d * SR)
    t = np.arange(n) / SR
    return (amp * np.sin(2 * np.pi * f * t)).astype(np.float32)

def dtmf(f1, f2, d):
    n = int(d * SR)
    t = np.arange(n) / SR
    return (0.35 * (np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t))).astype(np.float32)

segs = []
segs.append(tone(350, 0.4) + tone(440, 0.4))          # dial tone 0.4s
segs.append(np.zeros(int(0.08 * SR), dtype=np.float32))
for f1, f2 in [(697, 1209), (770, 1336), (852, 1477)]:  # 3 DTMF digits
    segs.append(dtmf(f1, f2, 0.12))
    segs.append(np.zeros(int(0.06 * SR), dtype=np.float32))
# handshake: alternating 1400/2100 Hz bursts + swept noise
rng = np.random.default_rng(7)
for i in range(6):
    f = 1400 if i % 2 == 0 else 2100
    segs.append(tone(f, 0.14, amp=0.45))
    noise = rng.standard_normal(int(0.14 * SR)).astype(np.float32)
    # crude band-pass via moving average difference (keeps it simple)
    segs.append(noise * 0.12)
# closing "boing": descending chirp 1800 -> 600 Hz
n = int(0.35 * SR)
t = np.arange(n) / SR
phase = 2 * np.pi * (1800 * t - 0.5 * (1200 / 0.35) * t ** 2)
segs.append((0.5 * np.sin(phase) * np.exp(-t * 4)).astype(np.float32))
modem = np.concatenate(segs).astype(np.float32)
modem = modem / np.max(np.abs(modem)) * 0.9
sf.write(os.path.join(SND, "modem_synth_raw.wav"), modem, SR)
print(f"modem_synth_raw.wav: {len(modem)/SR:.2f}s synthesized (fallback)", flush=True)
trim_and_norm(os.path.join(SND, "modem_synth_raw.wav"),
              os.path.join(SND, "sample_modem_synth.wav"), 3.0, mode="first")

# ---------- 3. Trim + normalize the 3 CC0 downloads ----------
decode(os.path.join(SND, "bell_raw.mp3"), os.path.join(SND, "bell_48k.wav"))
decode(os.path.join(SND, "motorbike_raw.mp3"), os.path.join(SND, "motorbike_48k.wav"))
decode(os.path.join(SND, "modem_raw.mp3"), os.path.join(SND, "modem_48k.wav"))
trim_and_norm(os.path.join(SND, "bell_48k.wav"),
              os.path.join(SND, "sample_bell.wav"), 2.0, mode="loudest")
trim_and_norm(os.path.join(SND, "motorbike_48k.wav"),
              os.path.join(SND, "sample_motorbike.wav"), 2.0, mode="first")
trim_and_norm(os.path.join(SND, "modem_48k.wav"),
              os.path.join(SND, "sample_modem.wav"), 3.0, mode="loudest")
print("SOUNDS DONE", flush=True)
