#!/usr/bin/env python3
"""Download top-4 candidates per item from img_candidates.json, build a
labeled contact sheet for visual selection. Skips files that fail."""
import json, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

FONT = "/home/hatch/workspace/agentnet-corner/stickman-shorts/src/assets/fonts/BeVietnamPro-Bold.ttf"
os.makedirs("cand_thumbs", exist_ok=True)
data = json.load(open("img_candidates.json"))
GROUPS = ["n5_key", "n4_hinge", "n3_stone", "n2_wheel", "n1_latch"]
PER = 4
TW, TH = 360, 270
LABEL_H = 34

def fetch(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AgentNet-V007/1.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        with open(path, "wb") as f:
            f.write(r.read())

rows = []
for g in GROUPS:
    thumbs = []
    for i, c in enumerate(data[g][:PER]):
        fn = f"cand_thumbs/{g}_{i}.jpg"
        try:
            if not os.path.exists(fn):
                fetch(c["url"], fn)
            im = Image.open(fn).convert("RGB")
            w, h = im.size
            # cover crop to TW:TH
            tgt = TW / TH
            if w / h > tgt:
                nw = int(h * tgt); x0 = (w - nw) // 2; im = im.crop((x0, 0, x0 + nw, h))
            else:
                nh = int(w / tgt); y0 = (h - nh) // 2; im = im.crop((0, y0, w, y0 + nh))
            im = im.resize((TW, TH), Image.LANCZOS)
            thumbs.append((f"{g}_{i} {c['license']} {w}x{h}", im, c))
        except Exception as e:
            print(f"FAIL {g}_{i}: {e}")
    rows.append((g, thumbs))

W = PER * TW
H = len(rows) * (TH + LABEL_H)
sheet = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(sheet)
fnt = ImageFont.truetype(FONT, 20)
for ri, (g, thumbs) in enumerate(rows):
    y0 = ri * (TH + LABEL_H)
    for ci, (label, im, c) in enumerate(thumbs):
        x0 = ci * TW
        sheet.paste(im, (x0, y0 + LABEL_H))
        d.text((x0 + 4, y0 + 6), label, font=fnt, fill=(0, 0, 0))
    # group label on the right of empty slots handled above
print(f"rows: {[(g, len(t)) for g, t in rows]}")
sheet.save("cand_sheet.jpg", quality=85)
print("saved cand_sheet.jpg", sheet.size)
# dump candidate metadata for the record
for g, thumbs in rows:
    for label, im, c in thumbs:
        print(f"{label} | {c['title']!r} | {c['creator']} | {c['foreign_landing_url']}")
