import sys, asyncio
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import aiohttp
from edge_tts.drm import DRM
from edge_tts.communicate import (
    WSS_URL, WSS_HEADERS, SEC_MS_GEC_VERSION, _SSL_CTX,
    connect_id, date_to_string, ssml_headers_plus_data,
)

# Exact string the library builds (mkssml) for the plain sentence.
SSML_PLAIN = ("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
              "xml:lang='en-US'><voice name='vi-VN-HoaiMyNeural'>"
              "<prosody pitch='+0Hz' rate='+0%' volume='+0%'>"
              "Xin chao, day la mot thu nghiem."
              "</prosody></voice></speak>")
# Exact string the library builds for the SSML input (escaped inner SSML).
SSML_ESCAPED = ("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
                "xml:lang='en-US'><voice name='vi-VN-HoaiMyNeural'>"
                "<prosody pitch='+0Hz' rate='+0%' volume='+0%'>"
                "&lt;speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" "
                "xml:lang=\"vi-VN\"&gt;&lt;voice name=\"vi-VN-HoaiMyNeural\"&gt;"
                "Xin chao, day la mot thu nghiem.&lt;/voice&gt;&lt;/speak&gt;"
                "</prosody></voice></speak>")


async def attempt(label, ssml):
    n_audio = 0
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=None, connect=None,
                                      sock_connect=10, sock_read=60)
    ) as session, session.ws_connect(
        f"{WSS_URL}&ConnectionId={connect_id()}"
        f"&Sec-MS-GEC={DRM.generate_sec_ms_gec()}"
        f"&Sec-MS-GEC-Version={SEC_MS_GEC_VERSION}",
        compress=15,
        headers=DRM.headers_with_muid(WSS_HEADERS),
        ssl=_SSL_CTX,
    ) as ws:
        await ws.send_str(
            f"X-Timestamp:{date_to_string()}\r\n"
            "Content-Type:application/json; charset=utf-8\r\n"
            "Path:speech.config\r\n\r\n"
            '{"context":{"synthesis":{"audio":{"metadataoptions":{'
            '"sentenceBoundaryEnabled":"true","wordBoundaryEnabled":"false"'
            "},"
            '"outputFormat":"audio-24khz-48kbitrate-mono-mp3"'
            "}}}}\r\n"
        )
        await ws.send_str(ssml_headers_plus_data(
            connect_id(), date_to_string(), ssml))
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(f"{label} TEXT:", msg.data[:200].replace("\r", " ").replace("\n", " "), flush=True)
                if "turn.end" in msg.data:
                    break
            elif msg.type == aiohttp.WSMsgType.BINARY:
                n_audio += len(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"{label} WS_ERROR:", msg.data, flush=True)
                break
        print(f"{label} AUDIO_BYTES_TOTAL: {n_audio}", flush=True)


async def main():
    await attempt("PLAIN", SSML_PLAIN)
    await attempt("ESCAPED", SSML_ESCAPED)


asyncio.run(main())
print("RAW2_DONE")
