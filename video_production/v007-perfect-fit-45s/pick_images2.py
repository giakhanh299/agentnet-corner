#!/usr/bin/env python3
"""Contact sheet 2: deeper candidates for n5/n4/n2."""
import json, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

FONT = "/home/hatch/workspace/agentnet-corner/stickman-shorts/src/assets/fonts/BeVietnamPro-Bold.ttf"
os.makedirs("cand_thumbs2", exist_ok=True)
d1 = json.load(open("img_candidates.json"))
d2 = json.load(open("img_candidates_n2r2.json"))
PICKS = [
    ("n5_key", [d1["n5_key"][4], d1["n5_key"][9], d1["n5_key"][13], d1["n5_key"][16]]),
    ("n4_hinge", [d1["n4_hinge"][8], d1["n4_hinge"][9], d1["n4_hinge"][10], d1["n4_hinge"][13]]),
    ("n2_wheel", [d1["n2_wheel"][9], d2[12], d2[3], d2[16]]),
]
TW, TH = 360, 270
LABEL_H = 34

def fetch(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AgentNet-V007/1.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        with open(path, "wb") as f:
            f.write(r.read())

rows = []
for g, cands in PICKS:
    thumbs = []
    for i, c in enumerate(cands):
        fn = f"cand_thumbs2/{g}_{i}.jpg"
        try:
            if not os.path.exists(fn):
                fetch(c["url"], fn)
            im = Image.open(fn).convert("RGB")
            w, h = im.size
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

W = 4 * TW
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
sheet.save("cand_sheet2.jpg", quality=85)
print("saved cand_sheet2.jpg", sheet.size)
for g, thumbs in rows:
    for label, im, c in thumbs:
        print(f"{label} | {c['title']!r} | {c['creator']} | {c['foreign_landing_url']}")
