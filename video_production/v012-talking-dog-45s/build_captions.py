#!/usr/bin/env python3
"""Build captions.srt + captions.ass + captions_pc.ass for V012 from the
VieNeu TTS unit timings (v012_units.json, run 3: 55.47s, 121 words,
speech-only 151 wpm, Whisper large-v3 89.3%).

Captions use the script's own words (v001/v002 method), timed by the
measured clause windows. Chunks: max 4 words per caption event, time
split evenly across the clause window. Last event clamped to the voice
total (55.47s) - the last unit end (55.56s) overshoots by 0.09s
(atempo rounding).
ASS style matches v001/v002/v003/v006/v011: Bold 56, white + black
outline, MarginV 300, alignment 2 (bottom center), PlayRes 1080x1920.
captions.ass = Noto Sans (VPS copy); captions_pc.ass = Be Vietnam Pro
(the font burned on the PC - this is the one used in the render).
"""
import json

with open("v012_units.json") as f:
    meta = json.load(f)
units = meta["units"]
TOTAL = meta["total"]


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ass_time(t):
    ms = int(round(t * 100))
    h, ms = divmod(ms, 360000)
    m, ms = divmod(ms, 6000)
    s, ms = divmod(ms, 100)
    return f"{h}:{m:02d}:{s:02d}.{ms:02d}"


events = []  # (start, end, text)
for u in units:
    start, end = u["start"], min(u["end"], TOTAL)
    words = u["clause"].split()
    chunks = [" ".join(words[i:i + 4]) for i in range(0, len(words), 4)]
    dur = (end - start) / len(chunks)
    for i, ch in enumerate(chunks):
        s = start + i * dur
        e = start + (i + 1) * dur
        events.append((s, e, ch))

with open("captions.srt", "w", encoding="utf-8") as f:
    for i, (s, e, t) in enumerate(events, 1):
        f.write(f"{i}\n{srt_time(s)} --> {srt_time(e)}\n{t}\n\n")


def ass_doc(fontname):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{fontname},56,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,40,40,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    body = "".join(
        f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Default,,0,0,0,,{t}\n"
        for s, e, t in events
    )
    return head + body


with open("captions.ass", "w", encoding="utf-8") as f:
    f.write(ass_doc("Noto Sans"))
with open("captions_pc.ass", "w", encoding="utf-8") as f:
    f.write(ass_doc("Be Vietnam Pro"))

total_words = sum(len(u["clause"].split()) for u in units)
print(f"{len(events)} caption events, {total_words} words, total {TOTAL}s")
for s, e, t in events:
    print(f"  {s:5.2f}-{e:5.2f} {t}")
