"""Sáng tác nhạc nền Kiếm Hiệp Cổ Trang sạch bản quyền 100% (cho kênh Giang Hồ Kỳ Truyện).

4 lớp điện ảnh cổ trang (ngũ cung D-E-F-A-B♭ / D-F-G-A-C):
  1. Đàn tranh / cổ cầm gảy ngũ cung (Karplus-Strong / harmonic pluck)
  2. Sáo trúc vi vu trầm bổng (sine + breath noise + vibrato nhẹ)
  3. Trống trận / trống đại trầm tạo khí thế giang hồ
  4. Nền dây trầm (erhu/cello drone) giữ mạch bi tráng

python studio/wuxia_music.py --seconds 60 --seed 1 --out wuxia.wav
"""
from __future__ import annotations

import argparse
import wave
from pathlib import Path
import numpy as np

SR = 48000
PENTA_D = [293.66, 349.23, 392.00, 440.00, 523.25, 587.33, 698.46, 783.99]  # D minor pentatonic


def _guzheng(freq: float, dur: float = 1.1) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float64) / SR
    env = np.exp(-t * 3.8) * (1.0 - np.exp(-t * 280.0))
    sig = (0.68 * np.sin(2 * np.pi * freq * t)
           + 0.30 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 5.0)
           + 0.16 * np.sin(2 * np.pi * freq * 3 * t) * np.exp(-t * 8.5)
           + 0.08 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t * 14.0))
    return sig * env


def _taiko(dur: float = 0.55) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float64) / SR
    f = 55.0 + 70.0 * np.exp(-t * 16.0)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    hit = np.sin(2 * np.pi * 160.0 * t) * np.exp(-t * 35.0) * 0.35
    return body + hit


def compose(seconds: float, seed: int = 1, bpm: float = 86.0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = max(SR, int(seconds * SR))
    t = np.arange(n, dtype=np.float64) / SR
    beat = 60.0 / bpm

    left = np.zeros(n, dtype=np.float64)
    right = np.zeros(n, dtype=np.float64)

    # 1. Deep cinematic drone (D2 + A2)
    lfo = 0.78 + 0.22 * np.sin(2 * np.pi * 0.14 * t)
    drone = (0.20 * np.sin(2 * np.pi * 73.42 * t)
             + 0.14 * np.sin(2 * np.pi * 110.00 * t)
             + 0.08 * np.sin(2 * np.pi * 146.83 * t)) * lfo
    left += drone
    right += drone

    # 2. Guzheng pentatonic phrases
    step = beat / 2.0
    n_steps = int(seconds / step)
    for i in range(n_steps):
        if i % 4 == 3 and rng.random() < 0.5:
            continue
        pos = int(i * step * SR)
        f = PENTA_D[int(rng.integers(0, len(PENTA_D)))]
        note = _guzheng(f, 1.05) * (0.24 if i % 4 == 0 else 0.15)
        end = min(n, pos + len(note))
        pan = 0.25 + 0.5 * rng.random()
        left[pos:end] += note[:end - pos] * (1.0 - pan * 0.45)
        right[pos:end] += note[:end - pos] * (0.55 + pan * 0.45)

    # 3. Bamboo flute sustained phrases every 2 bars
    bar = beat * 4.0
    for b in range(int(seconds / (bar * 2))):
        pos = int((b * 2 + 0.25) * bar * SR)
        dur = min(bar * 1.4, seconds - (pos / SR))
        if dur < 1.0:
            break
        ln = int(dur * SR)
        lt = np.arange(ln, dtype=np.float64) / SR
        f0 = PENTA_D[int(rng.integers(3, 7))]
        vib = 1.0 + 0.006 * np.sin(2 * np.pi * 5.2 * lt)
        env = np.minimum(1.0, lt / 0.45) * np.minimum(1.0, np.maximum(0.0, (dur - lt) / 0.6))
        flute = (0.14 * np.sin(2 * np.pi * np.cumsum(f0 * vib) / SR)
                 + 0.03 * np.sin(2 * np.pi * np.cumsum(2 * f0 * vib) / SR)) * env
        end = min(n, pos + ln)
        left[pos:end] += flute[:end - pos] * 0.85
        right[pos:end] += flute[:end - pos] * 1.05

    # 4. Epic war drum hits on strong beats
    drum = _taiko() * 0.28
    for b in range(int(seconds / beat)):
        if b % 4 == 0 or (b % 8 == 6):
            pos = int(b * beat * SR)
            end = min(n, pos + len(drum))
            left[pos:end] += drum[:end - pos]
            right[pos:end] += drum[:end - pos]

    stereo = np.stack([left, right], axis=1)
    fi, fo = int(0.6 * SR), int(1.4 * SR)
    stereo[:fi] *= np.linspace(0, 1, fi)[:, None]
    stereo[-fo:] *= np.linspace(1, 0, fo)[:, None]
    peak = np.max(np.abs(stereo)) or 1.0
    stereo = stereo / peak * 0.50
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
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    write_wav(a.out, compose(a.seconds, a.seed))
    print(f"OK: {a.out} ({a.seconds}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
