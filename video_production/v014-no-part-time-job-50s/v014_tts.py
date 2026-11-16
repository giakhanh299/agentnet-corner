"""VieNeu-TTS v3 Turbo for V014 on the PC — per-unit native synthesis (48 kHz).

Voice: Mai Anh (female preset). Units = script clauses; pauses are added
later AFTER per-unit atempo=0.65 slowing (so pauses stay exactly
0.3/0.4/0.6s). Saves per-unit 48k wavs + 16k mono copies (for the
faster-whisper check) + units.json (native durations).
Runs in .venv-vieneu on the PC.
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

OUTDIR = r"C:\Users\w\agentnet-corner\ai-stack\v014_tts"
os.makedirs(OUTDIR, exist_ok=True)
VOICE = "Mai Anh"
SR = 48000

# (unit, text, pause_after_s) — pauses applied AFTER slowing, not here.
UNITS = [
    ("hook", "Đừng làm thêm giờ nữa. Máy tính nhà bạn làm video nhanh hơn bạn tưởng.", 0.3),
    ("b1", "Tôi làm video bốn mươi lăm giây thế này: giọng đọc xong trong chưa đầy một giây, kiểm tra giọng chỉ mất chưa đầy năm giây.", 0.4),
    ("b2a", "Bốn bước thôi. Một, viết kịch bản ngắn, khoảng một trăm hai mươi từ.", 0.3),
    ("b2b", "Hai, cho máy đọc giọng. Ba, vẽ hình bằng trí tuệ nhân tạo.", 0.3),
    ("b2c", "Bốn, dựng trên máy nhà, mười hai giây là xong.", 0.4),
    ("b3a", "Không hứa bạn giàu nhanh.", 0.3),
    ("b3b", "Nhưng một buổi tối, bạn làm được một video. Một tuần, bạn có bảy video, mà không cần quay phim gì cả.", 0.6),
    ("payoff", "Làm thêm kiểu cũ đổi giờ lấy tiền. Làm kiểu này, máy làm hộ giờ của bạn. Bạn chọn cách nào? Bình luận nhé!", 0.0),
]

t0 = time.time()
print("Loading Vieneu() ...", flush=True)
tts = Vieneu()
print(f"Loaded in {time.time() - t0:.1f}s; preset voices: {len(tts.list_preset_voices())}", flush=True)

units_timing = []
total_words = 0
speech_s = 0.0
for name, text, pause_after in UNITS:
    s0 = time.time()
    audio = tts.infer(text, voice=VOICE)
    synth_s = time.time() - s0
    audio = np.asarray(audio, dtype=np.float32)
    dur = len(audio) / SR
    words = len(text.split())
    total_words += words
    speech_s += dur
    print(f"{name}: {dur:.2f}s audio, {words} words, {words / dur * 60:.0f} wpm, synth {synth_s:.2f}s (RTF {synth_s / dur:.2f}): {text}", flush=True)
    units_timing.append({"unit": name, "text": text, "pause_after": pause_after,
                         "native_dur": round(dur, 3), "words": words})
    sf.write(os.path.join(OUTDIR, f"v014_unit_{name}_native48k.wav"), audio, SR)
    # 16 kHz mono copy for the faster-whisper check (same as round-4 samples)
    audio16 = audio
    import librosa
    audio16 = librosa.resample(audio, orig_sr=SR, target_sr=16000)
    sf.write(os.path.join(OUTDIR, f"v014_unit_{name}_16k.wav"), audio16, 16000)

print(f"Saved per-unit wavs: {speech_s:.2f}s speech, {total_words} words, "
      f"speech-only {total_words / speech_s * 60:.0f} wpm", flush=True)
with open(os.path.join(OUTDIR, "v014_units.json"), "w", encoding="utf-8") as f:
    json.dump(units_timing, f, ensure_ascii=False, indent=2)
print(f"TOTAL wall (incl. model load): {time.time() - t0:.1f}s", flush=True)
print("V014_TTS_DONE")
