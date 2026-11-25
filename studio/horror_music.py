"""Tự sáng tác nhạc nền rùng rợn (không bản quyền, mỗi seed ra một bản khác).

Lớp âm thanh:
1. Drone trầm 2 nốt lệch nhau tạo tiếng "rung" (beating), lên xuống chậm.
2. Gió đêm: nhiễu lọc thấp, cường độ thay đổi.
3. Đàn bầu tổng hợp: nốt ngũ cung luyến cao độ + rung (vibrato), thưa, có vang.
4. Nhịp tim: bắt đầu từ ~55% thời lượng, nhanh dần.
5. Cụm nốt nghịch tai dâng lên ở cao trào rồi cắt im lặng.

Chạy: python studio/horror_music.py --seconds 80 --seed 7 --out nhac_ma.wav
Sau đó chuẩn hóa: ffmpeg -i nhac_ma.wav -af loudnorm=I=-20:TP=-2:LRA=11 nhac_ma_norm.wav
"""
from __future__ import annotations

import argparse
import wave
from pathlib import Path

import numpy as np

SR = 48000
# Ngũ cung (thang oán) quanh La: A3 C4 D4 E4 G4 A4
PENTA = [220.0, 261.63, 293.66, 329.63, 392.0, 440.0]


def _env(n: int, attack: float, release: float) -> np.ndarray:
    a = max(1, int(attack * SR))
    r = max(1, int(release * SR))
    e = np.ones(n, dtype=np.float32)
    e[:a] = np.linspace(0, 1, a, dtype=np.float32)
    e[-r:] *= np.linspace(1, 0, r, dtype=np.float32)
    return e


def _lowpass(x: np.ndarray, alpha: float) -> np.ndarray:
    # Lọc thấp 1 cực, vector hóa theo khối để đủ nhanh
    y = np.empty_like(x)
    acc = 0.0
    for i in range(0, len(x), 4096):
        blk = x[i:i + 4096]
        out = np.empty_like(blk)
        for j, v in enumerate(blk):
            acc += alpha * (v - acc)
            out[j] = acc
        y[i:i + 4096] = out
    return y


def _reverb(x: np.ndarray, delays=(0.031, 0.047, 0.071, 0.113), fb: float = 0.55) -> np.ndarray:
    out = x.copy()
    for d in delays:
        k = int(d * SR)
        buf = np.zeros_like(x)
        buf[k:] = x[:-k]
        for _ in range(3):
            buf[k:] += fb * buf[:-k]
            fb *= 0.8
        out += 0.25 * buf
    return out


def drone(t: np.ndarray, rng) -> np.ndarray:
    f1 = 55.0
    f2 = f1 * 2 ** (rng.uniform(0.6, 1.2) / 12)  # lệch < 1.2 nửa cung -> rung
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * t / rng.uniform(9, 14))
    sig = np.sin(2 * np.pi * f1 * t) + 0.7 * np.sin(2 * np.pi * f2 * t) + 0.25 * np.sin(2 * np.pi * f1 * 2.01 * t)
    return (0.22 * lfo * sig).astype(np.float32)


def wind(n: int, t: np.ndarray, rng) -> np.ndarray:
    noise = rng.standard_normal(n).astype(np.float32)
    low = _lowpass(noise, 0.02)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / rng.uniform(6, 10) + rng.uniform(0, 6))
    return (0.35 * low * swell).astype(np.float32)


def dan_bau_note(freq: float, dur: float, rng) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    bend = 2 ** ((rng.choice([-2, -1, 1, 2]) * np.clip(t / (dur * 0.6), 0, 1)) / 12)  # luyến
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.4, 0, 1)
    phase = 2 * np.pi * np.cumsum(freq * bend * vib) / SR
    tone = np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.12 * np.sin(3 * phase)
    return (tone * _env(n, 0.02, dur * 0.7) * np.exp(-t / (dur * 0.8))).astype(np.float32)


def heartbeat(n: int, start: float, rng) -> np.ndarray:
    out = np.zeros(n, dtype=np.float32)
    total = n / SR
    tt = start
    bpm = 58.0
    thump_len = int(0.12 * SR)
    tk = np.arange(thump_len) / SR
    thump = (np.sin(2 * np.pi * 48 * tk) * np.exp(-tk / 0.04)).astype(np.float32)
    while tt < total - 1.5:
        for off, gain in ((0.0, 1.0), (0.22, 0.7)):
            i = int((tt + off) * SR)
            if i + thump_len < n:
                out[i:i + thump_len] += gain * thump
        bpm = min(118.0, bpm * 1.035)
        tt += 60.0 / bpm
    return 0.6 * out


def riser(n: int, start: float, end: float) -> np.ndarray:
    out = np.zeros(n, dtype=np.float32)
    a, b = int(start * SR), int(end * SR)
    t = np.arange(b - a) / SR
    prog = t / t[-1]
    cluster = sum(np.sin(2 * np.pi * f * (1 + 0.5 * prog) * t) for f in (311.1, 329.6, 349.2, 466.2))
    out[a:b] = (0.12 * cluster * prog ** 2).astype(np.float32)
    return out


def compose(seconds: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    left = drone(t, rng) + wind(n, t, rng)
    right = drone(t, rng) + wind(n, t, rng)

    # Đàn bầu thưa, đặt ngẫu nhiên trái/phải
    bau = np.zeros(n, dtype=np.float32)
    pan = np.zeros(n, dtype=np.float32)
    tt = rng.uniform(2.0, 4.0)
    while tt < seconds * 0.85:
        dur = rng.uniform(2.2, 3.8)
        note = dan_bau_note(float(rng.choice(PENTA)), dur, rng)
        i = int(tt * SR)
        j = min(n, i + len(note))
        bau[i:j] += note[: j - i]
        pan[i:j] = rng.uniform(-0.7, 0.7)
        tt += dur + rng.uniform(2.5, 6.0)
    bau = _reverb(bau)
    left += 0.30 * bau * (1 - pan) / 2 * 2
    right += 0.30 * bau * (1 + pan) / 2 * 2

    hb = heartbeat(n, seconds * 0.55, rng)
    rs = riser(n, seconds * 0.78, seconds * 0.92)
    left += hb + rs
    right += hb + rs

    # Cắt im lặng 0.8s sau cao trào, rồi drone nhỏ dần đến hết
    cut_a, cut_b = int(seconds * 0.92 * SR), int((seconds * 0.92 + 0.8) * SR)
    for ch in (left, right):
        ch[cut_a:cut_b] = 0
        ch[cut_b:] *= np.linspace(0.5, 0, n - cut_b, dtype=np.float32)
        ch[: int(1.5 * SR)] *= np.linspace(0, 1, int(1.5 * SR), dtype=np.float32)

    stereo = np.stack([left, right], axis=1)
    peak = np.max(np.abs(stereo)) or 1.0
    return (stereo / peak * 0.8).astype(np.float32)


def write_wav(path: Path, stereo: np.ndarray) -> None:
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main() -> None:
    ap = argparse.ArgumentParser(description="Sáng tác nhạc nền rùng rợn")
    ap.add_argument("--seconds", type=float, default=80)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=Path, default=Path("nhac_ma.wav"))
    a = ap.parse_args()
    write_wav(a.out, compose(a.seconds, a.seed))
    print(f"Đã tạo {a.out} ({a.seconds:.0f}s, seed={a.seed})")


if __name__ == "__main__":
    main()
