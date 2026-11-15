import sys, asyncio, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import edge_tts

OUT = r"C:\Users\w\agentnet-corner\ai-stack\voice_compare"
os.makedirs(OUT, exist_ok=True)
VOICE = "vi-VN-HoaiMyNeural"


async def try_one(label, text, path):
    try:
        comm = edge_tts.Communicate(text, VOICE)
        await comm.save(path)
        size = os.path.getsize(path)
        print(f"{label}: OK {size} bytes", flush=True)
    except Exception as e:
        print(f"{label}: FAIL {type(e).__name__}: {e}", flush=True)


async def main():
    await try_one("SSML_DIACRITICS",
                  '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="vi-VN"><voice name="vi-VN-HoaiMyNeural">Mỗi lần đăng nhập<break time="300ms"/>, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?</voice></speak>',
                  os.path.join(OUT, "diag_ssml_diac.mp3"))
    await try_one("PLAIN_DIACRITICS",
                  "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?",
                  os.path.join(OUT, "diag_plain_diac.mp3"))


asyncio.run(main())
print("DIAG2_DONE")
