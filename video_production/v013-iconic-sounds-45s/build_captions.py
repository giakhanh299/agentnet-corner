#!/usr/bin/env python3
"""Build captions.srt + captions.ass for V013 from unit timings
(v013_units.json — exact VieNeu slowed boundaries) + the SPOKEN script
words (post-probe: "bán bánh mì" instead of "rao bánh mì";
"quay số" instead of "modem quay số"; "chuông trường", "đề nổ",
"cục gạch" kept).

Beats (from the joined voice wav, atempo 0.70):
  hook 0.00-7.35, n5 7.65-12.78, n4 13.18-18.77, n3 19.17-24.29,
  n2 24.69-33.13, n1 33.53-40.94, cta 41.54-45.75
Chunks: max 4 words per caption event, time split evenly across the beat.
ASS style: Be Vietnam Pro Bold 56, white + black outline, MarginV 360
(v005 QC note: 300 sat tight against the #5 row), alignment 2 (bottom
center), PlayRes 1080x1920.
"""
import json
import os

BASE = "/home/hatch/workspace/agentnet-corner/video_production/v013-iconic-sounds-45s"
UNITS = json.load(open(os.path.join(BASE, "v013_units.json")))

# spoken text per unit (post-probe swaps applied)
TEXT = {
    "hook": "Năm âm thanh này, nghe một giây là nhớ ngay. Số một, đảm bảo bạn đã nghe cả trăm lần.",
    "n5": "Số năm: tiếng chuông trường. Tan học là chạy, không cần ai nhắc.",
    "n4": "Số bốn: tiếng xe máy đề nổ. Sáng nào cũng nghe, cả xóm cùng dậy.",
    "n3": "Số ba: tiếng bán bánh mì. Chưa thấy xe đâu, đã thấy đói.",
    "n2": "Số hai: nhạc chuông điện thoại cục gạch. Giai điệu này có từ hơn một trăm năm trước, già hơn cả ông bà bạn.",
    "n1": "Số một: tiếng quay số. Nghe xong mới được lên mạng, mà rớt mạng là quay lại từ đầu.",
    "cta": "Bạn nhớ âm thanh nào nhất? Bình luận số của nó nhé!",
}

by_unit = {u["unit"]: u for u in UNITS}
SEGMENTS = [(by_unit[name]["start"], by_unit[name]["end"], TEXT[name])
            for name in ["hook", "n5", "n4", "n3", "n2", "n1", "cta"]]

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

with open(os.path.join(BASE, "captions.srt"), "w", encoding="utf-8") as f:
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
with open(os.path.join(BASE, "captions.ass"), "w", encoding="utf-8") as f:
    f.write(ass_head)
    for s, e, t in events:
        f.write(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Default,,0,0,0,,{t}\n")

total_words = sum(len(t.split()) for _, _, t in SEGMENTS)
print(f"{len(events)} caption events, {total_words} words (spoken words, post-probe)")
for s, e, t in events:
    print(f"  {s:5.2f}-{e:5.2f} {t}")
