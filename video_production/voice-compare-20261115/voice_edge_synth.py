import sys, asyncio, subprocess, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import edge_tts
import numpy as np
import soundfile as sf

OUT = r"C:\Users\w\agentnet-corner\ai-stack\voice_compare"
os.makedirs(OUT, exist_ok=True)

# 300ms break after the comma inside sentences 1 and 2; 600ms between
# sentences 1-2; 800ms before the payoff (sentence 3). No fixed pause.
SSML = [
    '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="vi-VN"><voice name="{v}">Mỗi lần đăng nhập<break time="300ms"/>, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?</voice></speak>',
    '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="vi-VN"><voice name="{v}">Thủy thủ viết tất cả vào sổ nhật ký của tàu<break time="300ms"/>, gọi là sổ log.</voice></speak>',
    '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="vi-VN"><voice name="{v}">Đăng nhập là ký tên vào sổ log của tàu.</voice></speak>',
]
VOICES = ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"]
GAPS = [0.6, 0.8]  # seconds: after s1, after s2 (before payoff)


async def synth_one(ssml, voice, path):
    comm = edge_tts.Communicate(ssml, voice)
    await comm.save(path)


async def main():
    for voice in VOICES:
        tag = voice.replace("vi-VN-", "").replace("Neural", "").lower()
        wavs = []
        for i, ssml in enumerate(SSML):
            mp3 = os.path.join(OUT, f"edge_{tag}_s{i+1}.mp3")
            wav = os.path.join(OUT, f"edge_{tag}_s{i+1}.wav")
            await synth_one(ssml.format(v=voice), voice, mp3)
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-i", mp3,
                 "-ar", "16000", "-ac", "1", wav],
                check=True)
            data, sr = sf.read(wav)
            print(f"{voice} s{i+1}: {len(data)/sr:.2f}s", flush=True)
            wavs.append((data, sr))
        parts = [wavs[0][0]]
        for gap, (data, sr) in zip(GAPS, wavs[1:]):
            parts.append(np.zeros(int(gap * sr), dtype=wavs[0][0].dtype))
            parts.append(data)
        joined = np.concatenate(parts)
        out = os.path.join(OUT, f"edge_{tag}.wav")
        sf.write(out, joined, 16000)
        print(f"{voice} FINAL: {len(joined)/16000:.2f}s -> {out}", flush=True)


asyncio.run(main())
print("EDGE_DONE")
