"""Sáng tác nhạc nền kiến thức / tò mò sạch bản quyền 100% (cho Tập Làm Content · KENH_008).

4 lớp nhẹ, hiện đại, dễ nghe dưới giọng kể chuyện:
  1. Warm Rhodes pad (hợp âm Cmaj9 -> Am7 -> Fmaj7 -> G6)
  2. Marimba / kalimba pluck nhịp 104 BPM (tạo cảm giác tò mò, thông minh)
  3. Soft muted kick + brushed shaker nhẹ giữ tiết tấu
  4. Bass ấm nâng đáy (sine + triangle nhẹ)

python studio/curiosity_music.py --seconds 60 --seed 15 --out curiosity.wav
"""
from __future__ import annotations

import argparse
import wave
from pathlib import Path
import numpy as np

SR = 48000

CHORDS = [
    (261.63, 329.63, 392.00, 493.88),  # Cmaj7
    (220.00, 261.63, 329.63, 392.00),  # Am7
    (174.61, 220.00, 261.63, 329.63),  # Fmaj7
    (196.00, 246.94, 293.66, 392.00),  # G6
]
BASS = [130.81, 110.00, 87.31, 98.00]
PENTA = [523.25, 587.33, 659.25, 783.99, 880.00, 1046.50]


def _pluck(rng: np.random.Generator, freq: float, dur: float = 0.42) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float64) / SR
    env = np.exp(-t * 9.5) * (1.0 - np.exp(-t * 180.0))
    sig = (0.75 * np.sin(2 * np.pi * freq * t)
           + 0.22 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 18)
           + 0.08 * np.sin(2 * np.pi * freq * 3 * t) * np.exp(-t * 30))
    return sig * env


def _kick(dur: float = 0.16) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float64) / SR
    f = 48.0 + 75.0 * np.exp(-t * 32.0)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase) * np.exp(-t * 18.0)


def compose(seconds: float, seed: int = 15, bpm: float = 104.0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = max(SR, int(seconds * SR))
    t = np.arange(n, dtype=np.float64) / SR
    beat = 60.0 / bpm
    bar = beat * 4.0

    left = np.zeros(n, dtype=np.float64)
    right = np.zeros(n, dtype=np.float64)

    # 1. Warm pad + bass per bar
    n_bars = int(np.ceil(seconds / bar))
    for b in range(n_bars):
        ci = b % len(CHORDS)
        s0 = int(b * bar * SR)
        s1 = min(n, int((b + 1) * bar * SR))
        if s1 <= s0:
            break
        lt = t[s0:s1] - b * bar
        env = np.minimum(1.0, lt / 0.15) * np.minimum(1.0, np.maximum(0.0, (bar - lt) / 0.25))
        pad = np.zeros(s1 - s0, dtype=np.float64)
        for f in CHORDS[ci]:
            pad += 0.12 * np.sin(2 * np.pi * f * lt) + 0.04 * np.sin(2 * np.pi * f * 2 * lt)
        bass = 0.22 * np.sin(2 * np.pi * BASS[ci] * lt) * np.exp(-lt * 0.65)
        left[s0:s1] += (pad * 0.45 + bass) * env
        right[s0:s1] += (pad * 0.45 + bass) * env

    # 2. Curious marimba arpeggio (eighth notes)
    step = beat / 2.0
    n_steps = int(seconds / step)
    pattern = [int(rng.integers(0, len(PENTA))) for _ in range(8)]
    for i in range(n_steps):
        if i % 8 in (1, 5) and rng.random() < 0.45:
            continue
        pos = int(i * step * SR)
        freq = PENTA[pattern[i % 8]]
        pl = _pluck(rng, freq, 0.38) * (0.20 if i % 2 == 0 else 0.13)
        end = min(n, pos + len(pl))
        pan = 0.35 + 0.3 * ((i % 4) / 3.0)
        left[pos:end] += pl[:end - pos] * (1.0 - pan * 0.4)
        right[pos:end] += pl[:end - pos] * (0.6 + pan * 0.4)

    # 3. Soft kick (beats 1 & 3) + light shaker (offbeats)
    kick_wave = _kick() * 0.24
    for b in range(int(seconds / beat)):
        pos = int(b * beat * SR)
        if b % 2 == 0:
            end = min(n, pos + len(kick_wave))
            left[pos:end] += kick_wave[:end - pos]
            right[pos:end] += kick_wave[:end - pos]
        sh_pos = int((b + 0.5) * beat * SR)
        sh_len = int(0.05 * SR)
        if sh_pos + sh_len < n:
            st = np.arange(sh_len) / SR
            sh = rng.normal(0, 1, sh_len) * np.exp(-st * 60.0) * 0.035
            sh = np.diff(np.concatenate(([0.0], sh)))  # high-pass crispness
            left[sh_pos:sh_pos + sh_len] += sh * 0.8
            right[sh_pos:sh_pos + sh_len] += sh * 1.1

    stereo = np.stack([left, right], axis=1)
    # Fade in/out
    fi, fo = int(0.5 * SR), int(1.2 * SR)
    stereo[:fi] *= np.linspace(0, 1, fi)[:, None]
    stereo[-fo:] *= np.linspace(1, 0, fo)[:, None]
    peak = np.max(np.abs(stereo)) or 1.0
    stereo = stereo / peak * 0.48
    return (stereo * 32767).astype(np.int16)


def write_wav(path: Path, pcm: np.ndarray) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=60.0)
    ap.add_argument("--seed", type=int, default=15)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    write_wav(a.out, compose(a.seconds, a.seed))
    print(f"OK: {a.out} ({a.seconds}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
