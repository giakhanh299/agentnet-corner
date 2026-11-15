import sys, asyncio
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import aiohttp
from edge_tts.drm import DRM
from edge_tts.communicate import (
    WSS_URL, WSS_HEADERS, SEC_MS_GEC_VERSION, _SSL_CTX,
    connect_id, date_to_string, ssml_headers_plus_data,
)

SSML_PLAIN = ("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
              "xml:lang='en-US'><voice name='vi-VN-HoaiMyNeural'>"
              "<prosody pitch='+0Hz' rate='+0%' volume='+0%'>"
              "Xin chao, day la mot thu nghiem."
              "</prosody></voice></speak>")


async def main():
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
            connect_id(), date_to_string(), SSML_PLAIN))
        n_audio = 0
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print("TEXT:", msg.data[:600], flush=True)
                if "turn.end" in msg.data:
                    break
            elif msg.type == aiohttp.WSMsgType.BINARY:
                n_audio += len(msg.data)
                print("BINARY:", len(msg.data), "bytes (total audio",
                      n_audio, ")", flush=True)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print("WS_ERROR:", msg.data, flush=True)
                break
        print("AUDIO_BYTES_TOTAL:", n_audio, flush=True)


asyncio.run(main())
print("RAW_DONE")
