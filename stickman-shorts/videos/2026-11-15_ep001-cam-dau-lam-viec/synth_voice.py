#!/usr/bin/env python3
"""Synthesize Ep001 voice with MMS (facebook/mms-tts-vie), free, offline.

Reuses the v001 working path (sentence-by-sentence MMS): the model is
already cached in ~/.cache/huggingface, torch/transformers live in the
project venv (~/workspace/agentnet-corner/venv). Edge TTS failed in v001
(0-byte mp3) and is NOT retried here.

Each script beat is synthesized separately so the scene can time itself
to the real voice. Pauses between beats: 0.3s / 0.4s / 0.4s, and 0.7s
of silence before the payoff (F7: 0.5s lang truoc cau chot).
Writes voice.wav (16k mono) + segments/*.wav + timing.json.
"""
import json
import os
import wave

import numpy as np
import torch
from transformers import AutoTokenizer, VitsModel

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 16000

SEGMENTS = [
    ("hook", "Cùng làm mười tiếng mỗi ngày, sao một người giàu, một người vẫn nghèo?"),
    ("beat1_an", "An làm thuê mười tiếng một ngày. Hết giờ, anh nhận lương theo giờ, về nhà mệt lả, ngủ một giấc, sáng mai lại cày tiếp. Một năm trôi qua, tiền trong túi anh vẫn thế."),
    ("beat2_binh", "Bình cũng làm mười tiếng một ngày. Nhưng anh chỉ làm thuê năm tiếng. Năm tiếng còn lại, anh học cách bán hàng, học cách để tiền làm việc. Anh xây một cây cầu. Ai đi qua, anh thu một đồng."),
    ("beat3_nam_sau", "Một năm sau, An vẫn đổi giờ lấy tiền. Bình không bán giờ nữa. Cầu của anh làm việc cả khi anh ngủ. Cùng một sức, khác nhau ở cách nghĩ."),
    ("payoff", "Giàu không phải làm nhiều hơn. Giàu là làm khác đi. Bạn chọn bên nào?"),
]
# silence (seconds) inserted AFTER each segment
PAUSES = [0.3, 0.4, 0.4, 0.7, 0.0]

print("loading model facebook/mms-tts-vie ...")
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
print("model loaded")

os.makedirs(os.path.join(HERE, "segments"), exist_ok=True)

parts = []
timing = []
t = 0.0
for (name, text), pause in zip(SEGMENTS, PAUSES):
    inputs = tok(text, return_tensors="pt")
    with torch.no_grad():
        w = model(**inputs).waveform[0].numpy()
    w = np.clip(w, -1, 1).astype(np.float32)
    dur = len(w) / SR
    seg_path = os.path.join(HERE, "segments", f"{name}.wav")
    with wave.open(seg_path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((w * 32767).astype(np.int16).tobytes())
    timing.append({"beat": name, "start_s": round(t, 3), "duration_s": round(dur, 3),
                   "words": len(text.split()), "wpm": round(len(text.split()) / dur * 60, 1)})
    print(f"{name}: {dur:.2f}s ({len(text.split())} words, {len(text.split())/dur*60:.0f} wpm)")
    parts.append(w)
    t += dur
    if pause > 0:
        parts.append(np.zeros(int(pause * SR), dtype=np.float32))
        t += pause

full = np.concatenate(parts)
with wave.open(os.path.join(HERE, "voice.wav"), "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes())

timing.append({"total_s": round(len(full) / SR, 3),
               "total_words": sum(len(s[1].split()) for s in SEGMENTS)})
with open(os.path.join(HERE, "timing.json"), "w", encoding="utf-8") as f:
    json.dump(timing, f, ensure_ascii=False, indent=2)
print(f"total: {len(full)/SR:.2f}s, wrote voice.wav + timing.json")
