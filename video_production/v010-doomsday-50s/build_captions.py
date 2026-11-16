#!/usr/bin/env python3
"""Build captions.srt + captions.ass + captions_pc.ass for V010 from TTS
beat timings (take 3, the accepted take: 54.53s, 137 words, speech-only
160 wpm, Whisper 83.9%) + the script's own words (v001/v002 method:
captions use script words, timed by speech windows).

Beat windows (from v010_beat_timing.txt, take 3 on PC):
  hook   0.00-6.59, beat1 6.89-19.31, beat2 19.71-32.86,
  beat3 33.26-47.34, payoff 47.94-54.53
Chunks: max 4 words per caption event, time split evenly across the beat.
ASS style matches v001/v002/v003/v006: Bold 56, white + black outline,
MarginV 300, alignment 2 (bottom center), PlayRes 1080x1920.
captions.ass = Noto Sans (VPS copy); captions_pc.ass = Be Vietnam Pro
(the font burned on the PC - this is the one used in the render).
"""
import re

SEGMENTS = [
    (0.00, 6.59),
    (6.89, 19.31),
    (19.71, 32.86),
    (33.26, 47.34),
    (47.94, 54.53),
]
lines = [l.strip() for l in open("script_text.txt", encoding="utf-8") if l.strip()]
assert len(lines) == len(SEGMENTS), f"{len(lines)} lines vs {len(SEGMENTS)} segments"

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
for (start, end), sent in zip(SEGMENTS, lines):
    words = sent.split()
    # chunk into <=4 words
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

total_words = sum(len(l.split()) for l in lines)
print(f"{len(events)} caption events, {total_words} words")
for s, e, t in events:
    print(f"  {s:5.2f}-{e:5.2f} {t}")
