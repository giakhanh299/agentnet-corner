"""Whisper word-match check for voice-comparison samples.

Usage: voice_whisper_check.py <wav1> [wav2 ...]  (all must be 16 kHz mono)
Transcribes each file with faster-whisper large-v3 on CUDA and compares
against the 3 test sentences. NOTE: Whisper normalizes numbers to digits
("năm trăm" -> "500"), so those two words count as missed even when the
TTS said them correctly — the printed rate is a lower bound.
"""
import sys, os, re, difflib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TORCH_LIB = r"C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
os.environ["PATH"] = TORCH_LIB + ";" + os.environ["PATH"]

import soundfile as sf
from faster_whisper import WhisperModel

EXPECTED = ("Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước? "
            "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log. "
            "Đăng nhập là ký tên vào sổ log của tàu.")


def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()


def main():
    files = sys.argv[1:]
    if not files:
        print("usage: voice_whisper_check.py <wav> [wav ...]")
        return
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    print("MODEL_LOADED", flush=True)
    E = tokens(EXPECTED)
    for path in files:
        data, sr = sf.read(path, dtype="float32")
        assert sr == 16000, f"{path} sr={sr}"
        segments, info = model.transcribe(data, language="vi", beam_size=5)
        heard = " ".join(s.text.strip() for s in segments)
        H = tokens(heard)
        sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
        matched = sum(b.size for b in sm.get_matching_blocks())
        matched_idx = set()
        for b in sm.get_matching_blocks():
            matched_idx.update(range(b.a, b.a + b.size))
        missed = [E[i] for i in range(len(E)) if i not in matched_idx]
        dur = len(data) / sr
        print(f"CHECK {os.path.basename(path)}: {dur:.2f}s, "
              f"{matched}/{len(E)} = {matched / len(E) * 100:.1f}%, "
              f"missed={missed}", flush=True)
        print(f"  heard: {heard}", flush=True)


main()
print("CHECK_DONE")
