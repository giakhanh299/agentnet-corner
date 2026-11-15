"""Round 3 — Edge TTS retry (plain text ONLY; edge-tts 7.3.1 mangles SSML).

Round 1 failed with NoAudioReceived (Microsoft throttling this IP) after
2 early successes. This is ONE quick retry ~1h later: if it still fails,
record and STOP — do not hammer Microsoft.
Same 3 test sentences as rounds 1-2, joined with 0.6s / 0.8s gaps.
Includes the faster-whisper large-v3 word-match check on the PC.
"""
import asyncio
import glob
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_site = os.path.normpath(os.path.join(os.path.dirname(sys.executable), "..", "Lib", "site-packages"))
_torch_lib = os.path.join(_site, "torch", "lib")
if os.path.isdir(_torch_lib):
    os.add_dll_directory(_torch_lib)
for _d in glob.glob(os.path.join(_site, "nvidia", "*", "bin")):
    os.add_dll_directory(_d)

import edge_tts
import numpy as np
import soundfile as sf

OUT = r"C:\Users\w\agentnet-corner\ai-stack\voice_compare"
os.makedirs(OUT, exist_ok=True)

SENTENCES = [
    "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?",
    "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log.",
    "Đăng nhập là ký tên vào sổ log của tàu.",
]
VOICES = ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"]
GAPS = [0.6, 0.8]


async def synth_one(text, voice, path):
    comm = edge_tts.Communicate(text, voice)
    await asyncio.wait_for(comm.save(path), timeout=60)


async def main():
    results = {}
    for voice in VOICES:
        tag = voice.replace("vi-VN-", "").replace("Neural", "").lower()
        wavs = []
        ok = True
        for i, text in enumerate(SENTENCES):
            mp3 = os.path.join(OUT, f"edge_r3_{tag}_s{i+1}.mp3")
            wav = os.path.join(OUT, f"edge_r3_{tag}_s{i+1}.wav")
            try:
                await synth_one(text, voice, mp3)
            except Exception as e:
                print(f"{voice} s{i+1} FAILED: {type(e).__name__}: {e}", flush=True)
                ok = False
                break
            if not os.path.exists(mp3) or os.path.getsize(mp3) == 0:
                print(f"{voice} s{i+1} FAILED: 0-byte mp3", flush=True)
                ok = False
                break
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-i", mp3,
                 "-ar", "16000", "-ac", "1", wav],
                check=True)
            data, sr = sf.read(wav)
            print(f"{voice} s{i+1}: {len(data)/sr:.2f}s, {len(text.split())} words, "
                  f"{len(text.split())/(len(data)/sr)*60:.0f} wpm", flush=True)
            wavs.append((data, sr))
        if not ok:
            results[voice] = None
            continue
        parts = [wavs[0][0]]
        for gap, (data, sr) in zip(GAPS, wavs[1:]):
            parts.append(np.zeros(int(gap * sr), dtype=wavs[0][0].dtype))
            parts.append(data)
        joined = np.concatenate(parts)
        out = os.path.join(OUT, f"edge_r3_{tag}.wav")
        sf.write(out, joined, 16000)
        print(f"{voice} FINAL: {len(joined)/16000:.2f}s -> {out}", flush=True)
        results[voice] = out

    # --- Whisper check for any voice that produced audio ---
    made = [p for p in results.values() if p]
    if not made:
        print("EDGE_R3_NO_AUDIO", flush=True)
        return
    from faster_whisper import WhisperModel

    print("Loading faster-whisper large-v3 ...", flush=True)
    wm = WhisperModel("large-v3", device="cuda", compute_type="float16")

    def tokens(text):
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
        return text.split()

    import difflib
    expected = " ".join(SENTENCES)
    E = tokens(expected)
    for voice, path in results.items():
        if not path:
            continue
        audio, sr = sf.read(path, dtype="float32")
        segments, info = wm.transcribe(audio, language="vi", beam_size=5)
        heard = " ".join(s.text.strip() for s in segments)
        H = tokens(heard)
        sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
        matched = sum(b.size for b in sm.get_matching_blocks())
        matched_idx = set()
        for b in sm.get_matching_blocks():
            matched_idx.update(range(b.a, b.a + b.size))
        missed = [E[i] for i in range(len(E)) if i not in matched_idx]
        print(f"{voice} Whisper: {matched}/{len(E)} = {matched/len(E)*100:.1f}% | "
              f"missed: {missed}", flush=True)
        print(f"{voice} Heard: {heard}", flush=True)
    print("EDGE_R3_DONE", flush=True)


asyncio.run(main())
