"""Kokoro probe: does it support Vietnamese, and with which voice?

1. Lists the Kokoro-82M voice files on HF and prints any with a 'v' prefix.
2. Tries KPipeline(lang_code='v') and synthesizes sentence 1 with the
   first Vietnamese voice found (if any).
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from huggingface_hub import list_repo_files

print("=== Kokoro-82M voice files on HF ===")
files = list_repo_files("hexgrad/Kokoro-82M", repo_type="model")
voices = sorted(f for f in files if f.startswith("voices/") and f.endswith(".pt"))
print("total voices:", len(voices))
for v in voices:
    print(" ", v)
vi = [v for v in voices if v.startswith("voices/v")]
print("VIETNAMESE voices:", vi if vi else "NONE")

if not vi:
    print("KOKORO_NO_VIETNAMESE_VOICE")
    raise SystemExit(0)

from kokoro import KPipeline
import soundfile as sf

voice = os.path.splitext(os.path.basename(vi[0]))[0]
print(f"=== trying KPipeline(lang_code='v') with voice {voice} ===")
try:
    pipe = KPipeline(lang_code="v")
except Exception as e:
    print("PIPELINE_V_FAILED:", type(e).__name__, str(e)[:800])
    raise SystemExit(0)

text = "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?"
try:
    gen = pipe(text, voice=voice)
    for i, (gs, ps, audio) in enumerate(gen):
        print("graphemes:", gs)
        print("phonemes:", ps)
        print("audio samples:", len(audio))
        sf.write(r"C:\Users\w\agentnet-corner\ai-stack\voice_compare\kokoro_s1.wav",
                 audio, 24000)
        print("WROTE kokoro_s1.wav")
        break
    print("KOKORO_S1_OK")
except Exception as e:
    print("KOKORO_GEN_FAILED:", type(e).__name__, str(e)[:800])
