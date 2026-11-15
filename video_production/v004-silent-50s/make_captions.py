#!/usr/bin/env python3
"""v004 captions: build captions.srt from the MEASURED MMS clause timings
(from the PC TTS log, round 2) and the script text (with the "quay nho"
swap). Chunks of 3-5 words, time split proportionally by word count.
Then convert to .ass via tools/assemble.py (PlayRes 1080x1920).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# (start_s, end_s, text) — clause durations measured on the PC (round 2).
CLAUSES = [
    (0.00, 3.28, "Mỗi ngày, hàng trăm người đi qua góc phố này."),
    (3.58, 7.52, "Ông Tư sửa giày ở góc phố này đã ba mươi năm."),
    (7.82, 10.38, "Người ta lướt qua mỗi ngày,"),
    (10.53, 12.59, "không ai dừng lại,"),
    (12.74, 14.88, "không ai hỏi tên ông,"),
    (15.03, 16.92, "không ai nhớ mặt ông."),
    (17.22, 20.42, "Tối nào ông cũng đánh bóng một đôi giày nhỏ,"),
    (20.57, 25.64, "của một người khách bỏ quên từ lâu, không bao giờ quay lại lấy."),
    (25.94, 30.39, "Ông để đôi giày trên quầy nhỏ, như đang đợi ai đó."),
    (30.69, 33.33, "Một chiều, một bé gái dừng lại,"),
    (33.48, 35.62, "chỉ vào đôi giày nhỏ:"),
    (35.77, 37.61, "Của ai vậy ông?"),
    (37.91, 39.81, "Hôm sau, bé quay lại,"),
    (39.96, 41.91, "tay cầm một bức vẽ:"),
    (42.06, 45.52, "ông Tư ngồi sửa giày dưới ánh đèn vàng."),
    (46.03, 49.77, "Ông cười, lần đầu sau bao năm, có người nhìn thấy ông."),
    (50.07, 52.36, "Chỉ cần một người dừng lại."),
]


def split_chunk(words, max_words=5):
    """Split a word list into chunks of <= max_words, as even as possible."""
    n = len(words)
    if n <= max_words:
        return [words]
    n_chunks = (n + max_words - 1) // max_words
    base, rem = divmod(n, n_chunks)
    out, i = [], 0
    for c in range(n_chunks):
        size = base + (1 if c < rem else 0)
        out.append(words[i:i + size])
        i += size
    return out


def fmt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


events = []
for start, end, text in CLAUSES:
    words = text.split()
    chunks = split_chunk(words)
    dur = end - start
    t = start
    for chunk in chunks:
        frac = len(chunk) / len(words)
        chunk_end = t + dur * frac
        # last chunk ends exactly at the clause end
        if chunk is chunks[-1]:
            chunk_end = end
        events.append((t, chunk_end, " ".join(chunk)))
        t = chunk_end

srt_path = os.path.join(HERE, "captions.srt")
with open(srt_path, "w", encoding="utf-8") as f:
    for i, (s, e, txt) in enumerate(events, 1):
        f.write(f"{i}\n{fmt(s)} --> {fmt(e)}\n{txt}\n\n")

n_words = sum(len(t.split()) for _, _, t in events)
print(f"wrote {srt_path}: {len(events)} events, {n_words} words")
assert n_words == 131, f"word count {n_words} != 131"

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "stickman-shorts", "tools"))
from assemble import srt_to_ass
ass_path = srt_to_ass(srt_path)
print(f"wrote {ass_path}")
