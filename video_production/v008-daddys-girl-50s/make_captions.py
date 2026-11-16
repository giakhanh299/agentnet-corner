#!/usr/bin/env python3
"""v008 captions: build captions.srt from the MEASURED MMS clause timings
(timing.json from the PC TTS run 3, the file of record) and the FINAL
spoken text (with the two probe swaps: "met lam" and "buoc vao that khe"
— captions match what is SPOKEN, as in v004 with "quay nho").
Chunks of 3-5 words, time split proportionally by word count.
Then convert to .ass via tools/assemble.py (PlayRes 1080x1920).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "timing.json"), encoding="utf-8") as f:
    timing = json.load(f)

CLAUSES = [
    (c["start_s"], c["end_s"], c["text"])
    for c in timing[-1]["clauses"]
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
assert n_words == 127, f"word count {n_words} != 127"

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "stickman-shorts", "tools"))
from assemble import srt_to_ass
ass_path = srt_to_ass(srt_path)
print(f"wrote {ass_path}")
