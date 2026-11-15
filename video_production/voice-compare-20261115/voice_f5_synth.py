"""F5-TTS synthesis of the 3 test sentences (Test B).

Reference voice: sentence 1 of the MMS control (mms_varied.wav, first
4.91s) + its text as ref_text. So the F5 sample has the SAME timbre as
the MMS control — the comparison isolates F5's prosody/pacing, not a
new voice. Sentences are joined with the same gaps as the other voices
(0.6s after s1, 0.8s before the payoff).
"""
import sys, os, subprocess, glob, wave, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

BASE = r"C:\Users\w\agentnet-corner\ai-stack"
OUT = os.path.join(BASE, "voice_compare")
F5 = os.path.join(BASE, ".venv-f5", "Scripts", "f5-tts_infer-cli.exe")

SENTENCES = [
    "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?",
    "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log.",
    "Đăng nhập là ký tên vào sổ log của tàu.",
]
GAPS = [0.6, 0.8]
REF_TEXT = SENTENCES[0]
# Overridable via env: F5_SPEED=0.75 F5_OUTNAME=f5tts_slow.wav
SPEED = float(os.environ.get("F5_SPEED", "1.0"))
OUTNAME = os.environ.get("F5_OUTNAME", "f5tts.wav")
PREFIX = os.path.splitext(OUTNAME)[0]


def read_wav16(path):
    with wave.open(path, "rb") as f:
        n = f.getnframes()
        sr = f.getframerate()
        ch = f.getnchannels()
        sw = f.getsampwidth()
        raw = f.readframes(n)
    assert sr == 16000 and ch == 1 and sw == 2, f"{path}: sr={sr} ch={ch} sw={sw}"
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def write_wav16(path, data, sr=16000):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((np.clip(data, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    # 1. ref audio = first 4.91s of mms_varied.wav (sentence 1, MMS voice)
    mms = os.path.join(OUT, "mms_varied.wav")
    full = read_wav16(mms)
    ref = full[:int(4.91 * 16000)]
    ref_path = os.path.join(OUT, "f5_ref_s1.wav")
    write_wav16(ref_path, ref)
    print(f"REF: {len(ref) / 16000:.2f}s -> {ref_path}", flush=True)

    # 2. generate each sentence via the CLI
    wavs = []
    for i, text in enumerate(SENTENCES):
        odir = os.path.join(OUT, f"{PREFIX}_s{i+1}")
        os.makedirs(odir, exist_ok=True)
        t0 = time.time()
        r = subprocess.run(
            [F5, "--model", "F5TTS_v1_Base",
             "--ref_audio", ref_path,
             "--ref_text", REF_TEXT,
             "--gen_text", text,
             "--output_dir", odir,
             "--output_file", f"{PREFIX}_s{i+1}_raw.wav",
             "--speed", str(SPEED),
             "--device", "cuda"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(f"s{i+1} CLI rc={r.returncode} in {time.time() - t0:.1f}s", flush=True)
        if r.returncode != 0:
            print("STDOUT:", r.stdout[-2000:], flush=True)
            print("STDERR:", r.stderr[-2000:], flush=True)
            raise SystemExit(f"F5 CLI failed on sentence {i+1}")
        src = os.path.join(odir, f"{PREFIX}_s{i+1}_raw.wav")
        if not os.path.exists(src):
            cands = glob.glob(os.path.join(odir, "*.wav"))
            if not cands:
                raise SystemExit(f"No wav produced in {odir}")
            src = max(cands, key=os.path.getsize)
        wav16 = os.path.join(OUT, f"{PREFIX}_s{i+1}.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                        "-ar", "16000", "-ac", "1", wav16], check=True)
        d = read_wav16(wav16)
        print(f"s{i+1}: {len(d) / 16000:.2f}s, {len(text.split())} words, "
              f"{len(text.split()) / (len(d) / 16000) * 60:.0f} wpm", flush=True)
        wavs.append(d)

    # 3. join with gaps
    parts = [wavs[0]]
    for gap, d in zip(GAPS, wavs[1:]):
        parts.append(np.zeros(int(gap * 16000), dtype=np.float32))
        parts.append(d)
    joined = np.concatenate(parts)
    out = os.path.join(OUT, OUTNAME)
    write_wav16(out, joined)
    print(f"F5 FINAL (speed={SPEED}): {len(joined) / 16000:.2f}s -> {out}", flush=True)


main()
print("F5_DONE")
