#!/usr/bin/env python3
"""Build captions.srt + captions.ass for V007 from unit timings
(v007_units.json — exact synthesis boundaries) + the SPOKEN script words
(post-probe: "cắm vào ổ khóa" instead of "tra vào ổ"; "chạy đúng vào
khe" instead of "lăn đúng vào rãnh"; "milimét" dropped; "—" restored
in hook/n1b captions as in the script).

Beats (start/end from the joined voice wav):
  hook 0.00-5.76, n5 6.06-14.58, n4 14.98-21.64, n3 22.04-29.17,
  n2 29.57-35.87, n1 36.47-44.64, cta 45.04-48.40
Chunks: max 4 words per caption event, time split evenly across the beat.
ASS style: Be Vietnam Pro Bold 56, white + black outline, MarginV 360
(v005 QC note: 300 sat tight against the #5 row), alignment 2 (bottom
center), PlayRes 1080x1920.
"""
import json

UNITS = json.load(open("v007_units.json"))

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

# spoken text per beat (post-probe swaps applied; "—" as in script)
TEXT = {
    "hook": "Mọi thứ sinh ra để vừa khít với nhau — xem mà đã cái tay!",
    "n5": "Số năm: chìa khóa cắm vào ổ khóa, xoay một cái là mở. Nghe tiếng cạch mà sướng cả người.",
    "n4": "Số bốn: bản lề cửa khép lại vừa khít, không hở một khe nào. Nhìn thôi đã thấy gọn.",
    "n3": "Số ba: hòn đá vừa đúng lòng bàn tay. Cầm lên là muốn cầm mãi, không muốn bỏ xuống.",
    "n2": "Số hai: bánh xe tải chạy đúng vào khe. Như thể cái khe sinh ra cho nó.",
    "n1": "Số một: chốt cửa sập vào đúng lỗ. Một tiếng cạch duy nhất — cả video chỉ chờ khoảnh khắc này.",
    "cta": "Cái nào vừa khít nhất? Bình luận nhé!",
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
Style: Default,Be Vietnam Pro,56,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,40,40,360,1

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
