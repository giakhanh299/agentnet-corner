import sys, subprocess, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TORCH_LIB = r"C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
os.environ["PATH"] = TORCH_LIB + ";" + os.environ["PATH"]
import asyncio
import edge_tts
import soundfile as sf
from faster_whisper import WhisperModel

OUT = r"C:\Users\w\agentnet-corner\ai-stack\voice_compare"
VOICE = "vi-VN-HoaiMyNeural"


def transcribe(model, path):
    wav = path.replace(".mp3", "_16k.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path,
                    "-ar", "16000", "-ac", "1", wav], check=True)
    data, sr = sf.read(wav)
    segments, info = model.transcribe(data, language="vi", beam_size=5)
    text = " ".join(s.text for s in segments)
    print(f"TRANSCRIBE {os.path.basename(path)}: {text}", flush=True)


async def try_plain(i):
    path = os.path.join(OUT, f"diag_plain_retry{i}.mp3")
    try:
        comm = edge_tts.Communicate("Xin chao, day la mot thu nghiem.", VOICE)
        await comm.save(path)
        print(f"PLAIN_RETRY{i}: OK {os.path.getsize(path)} bytes", flush=True)
    except Exception as e:
        print(f"PLAIN_RETRY{i}: FAIL {type(e).__name__}: {e}", flush=True)


async def main():
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    print("MODEL_LOADED", flush=True)
    transcribe(model, os.path.join(OUT, "diag_ssml_simple.mp3"))
    transcribe(model, os.path.join(OUT, "diag_ssml_break.mp3"))
    for i in range(3):
        await try_plain(i)


asyncio.run(main())
print("DIAG3_DONE")
