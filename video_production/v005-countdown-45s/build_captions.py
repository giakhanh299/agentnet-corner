#!/usr/bin/env python3
"""Build captions.srt + captions.ass for V005 from unit timings
(v005_units.json — exact synthesis boundaries) + the SPOKEN script words
(post-probe: 'nặng nề' instead of 'trĩu'; '…' and '—' kept as in script
where the voice matches them).

Beats (start/end from the joined voice wav):
  hook 0.00-3.18, n5 3.48-10.92, n4 11.32-19.24, n3 19.64-28.10,
  n2 28.50-37.08, n1 37.68-45.47, cta 45.87-49.95
Chunks: max 4 words per caption event, time split evenly across the beat.
ASS style matches v001/v002: Noto Sans Bold 56, white + black outline,
MarginV 300, alignment 2 (bottom center), PlayRes 1080x1920.
"""
import json

UNITS = json.load(open("v005_units.json"))

# group units into beats
BEATS = [
    ("hook", ["hook"]),
    ("n5", ["n5a", "n5b"]),
    ("n4", ["n4a", "n4b"]),
    ("n3", ["n3a", "n3b"]),
    ("n2", ["n2a", "n2b"]),
    ("n1", ["n1a", "n1b"]),
    ("cta", ["cta"]),
]

# spoken text per beat (post-probe swaps applied)
TEXT = {
    "hook": "Top năm câu nói huyền thoại của mẹ!",
    "n5": "Số năm: Ăn cơm đi, nguội hết rồi! Mẹ nói câu này ba lần một bữa, lần nào cũng vậy.",
    "n4": "Số bốn: Tao nói mày có nghe không? Câu này mà vang lên là cả nhà im phăng phắc.",
    "n3": "Số ba: Hồi bằng tuổi mày, mẹ đã biết nấu cơm, giặt đồ. Câu này mẹ kể từ lúc con lên năm.",
    "n2": "Số hai: Con nhà người ta… Chỉ ba chữ thôi mà đủ làm con thấy mình thua cả xóm.",
    "n1": "Số một: Mẹ không cần gì đâu, con cứ lo cho con đi. Nghe thì nhẹ, mà tim con nặng nề.",
    "cta": "Số một của bạn là câu nào? Bình luận nhé!",
}

by_unit = {u["unit"]: u for u in UNITS}
SEGMENTS = []
for beat, units in BEATS:
    start = by_unit[units[0]]["start"]
    end = by_unit[units[-1]]["end"]
    SEGMENTS.append((start, end, TEXT[beat]))

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

events = []
for (start, end, sent) in SEGMENTS:
    words = sent.split()
    chunks = [" ".join(words[i:i + 4]) for i in range(0, len(words), 4)]
    dur = (end - start) / len(chunks)
    for i, ch in enumerate(chunks):
        s = start + i * dur
        e = start + (i + 1) * dur
        events.append((s, e, ch))

with open("captions.srt", "w", encoding="utf-8") as f:
    for i, (s, e, t) in enumerate(events, 1):
        f.write(f"{i}\n{srt_time(s)} --> {srt_time(e)}\n{t}\n\n")

ass_head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans,56,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,40,40,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open("captions.ass", "w", encoding="utf-8") as f:
    f.write(ass_head)
    for s, e, t in events:
        f.write(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Default,,0,0,0,,{t}\n")

total_words = sum(len(t.split()) for _, _, t in SEGMENTS)
print(f"{len(events)} caption events, {total_words} words (spoken words, post-probe)")
for s, e, t in events:
    print(f"  {s:5.2f}-{e:5.2f} {t}")
