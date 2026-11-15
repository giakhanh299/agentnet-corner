import torch, wave, sys
import numpy as np
from transformers import VitsModel, AutoTokenizer
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
SR = 16000
lines = [l.strip() for l in open("script_text.txt", encoding="utf-8").read().strip().split("\n") if l.strip()]
parts = []
for i, line in enumerate(lines):
    inputs = tok(line, return_tensors="pt")
    with torch.no_grad():
        w = model(**inputs).waveform[0].numpy()
    parts.append(np.clip(w, -1, 1))
    print(f"line {i}: {len(w)/SR:.2f}s :: {line[:50]}")
    if i < len(lines) - 1:
        parts.append(np.zeros(int(0.9 * SR), dtype=np.float32))  # 0.45s pause between sentences
full = np.concatenate(parts)
pcm = (np.clip(full, -1, 1) * 32767).astype(np.int16)
with wave.open("voice_mms_sent.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes(pcm.tobytes())
print(f"total: {len(pcm)/SR:.2f}s")
