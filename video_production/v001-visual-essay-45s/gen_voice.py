import asyncio, os, ssl
import edge_tts.communicate as comm
import edge_tts.voices as voices_mod

CA = "/run/hatch/egress-tls/ca-bundle.pem"
comm._SSL_CTX = ssl.create_default_context(cafile=CA)
voices_mod._SSL_CTX = ssl.create_default_context(cafile=CA)
PROXY = os.environ.get("HTTPS_PROXY")

TEXT = open("script_text.txt", encoding="utf-8").read().strip()

async def main():
    vs = await voices_mod.list_voices(proxy=PROXY)
    vi = [v for v in vs if v.get("ShortName", "").startswith("vi-VN")]
    print("vi voices:", [v["ShortName"] for v in vi])
    c = comm.Communicate(TEXT, "vi-VN-NamMinhNeural", proxy=PROXY,
                         connect_timeout=20, receive_timeout=120)
    await c.save("voice_namminh.mp3")
    print("saved voice_namminh.mp3")

asyncio.run(main())
