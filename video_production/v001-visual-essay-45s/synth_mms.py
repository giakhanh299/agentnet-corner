import torch, wave, sys
import numpy as np
from transformers import VitsModel, AutoTokenizer
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
text = open(sys.argv[1], encoding="utf-8").read().strip()
inputs = tok(text, return_tensors="pt")
with torch.no_grad():
    w = model(**inputs).waveform[0].numpy()
w = np.clip(w, -1, 1)
pcm = (w * 32767).astype(np.int16)
with wave.open(sys.argv[2], "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
    f.writeframes(pcm.tobytes())
print("saved", sys.argv[2], f"{len(pcm)/16000:.2f}s")
