#!/usr/bin/env python3
"""Build captions.srt + captions.ass + captions_pc.ass for V014 from the
assembled VieNeu voice timings (v014_voice_timing.json, atempo 0.66,
52.09s, 129 words, speech-only 156.4 wpm, Whisper 86.0%).

Pattern from v011 build_captions.py: max 4 words per caption event, time
split evenly across each unit window. ASS style matches v001/v011: Bold 56,
white + black outline, MarginV 300, alignment 2 (bottom center),
PlayRes 1080x1920. captions_pc.ass = Be Vietnam Pro (burned on the PC).
Caption text uses the script words (correct spelling, e.g. 'giàu').
"""
import json

with open("v014_voice_timing.json", encoding="utf-8") as f:
    TIMING = json.load(f)

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
for u in TIMING["units"]:
    start, end = u["start"], u["end"]
    words = u["text"].split()
    chunks = [" ".join(words[i:i + 4]) for i in range(0, len(words), 4)]
    dur = (end - start) / len(chunks)
    for i, ch in enumerate(chunks):
        events.append((start + i * dur, start + (i + 1) * dur, ch))

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

total_words = sum(u["words"] for u in TIMING["units"])
print(f"{len(events)} caption events, {total_words} words")
for s, e, t in events:
    print(f"  {s:5.2f}-{e:5.2f} {t}")
