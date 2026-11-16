#!/usr/bin/env python3
"""Download top 4 candidates per slot and build a contact sheet for V009."""
import json, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

CANDS = json.load(open("img_candidates.json"))
OUT = "cand_thumbs"
os.makedirs(OUT, exist_ok=True)

def fetch(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as f:
        f.write(r.read())

FONT_DIR = "/home/hatch/workspace/agentnet-corner/stickman-shorts/src/assets/fonts"
BOLD = os.path.join(FONT_DIR, "BeVietnamPro-Bold.ttf")
REG = os.path.join(FONT_DIR, "BeVietnamPro-Regular.ttf")

SLOTS = ["n5_dolphin", "n4_grasshopper", "n3_ant", "n2_flyingfish", "n1_octopus"]
tiles = []
for slot in SLOTS:
    for i, c in enumerate(CANDS[slot][:4]):
        name = f"{slot}_{i}.jpg"
        path = os.path.join(OUT, name)
        if not os.path.exists(path):
            try:
                fetch(c["url"], path)
                print(f"ok {name} {c.get('license')} {c.get('width')}x{c.get('height')} {c.get('title','')[:60]}")
            except Exception as e:
                print(f"FAIL {name}: {e}")
                continue
        try:
            im = Image.open(path).convert("RGB")
        except Exception as e:
            print(f"OPEN FAIL {name}: {e}")
            continue
        im.thumbnail((520, 340))
        tiles.append((slot, i, c, im))

# contact sheet: 4 cols x 5 rows
CW, CH = 540, 420
sheet = Image.new("RGB", (CW * 4, CH * 5), (255, 255, 255))
d = ImageDraw.Draw(sheet)
fb = ImageFont.truetype(BOLD, 26)
fr = ImageFont.truetype(REG, 20)
for idx, (slot, i, c, im) in enumerate(tiles):
    r, col = divmod(idx, 4)
    x0, y0 = col * CW + 10, r * CH + 10
    sheet.paste(im, (x0, y0 + 60))
    d.text((x0, y0), f"{slot} #{i} [{c.get('license')}] {c.get('width')}x{c.get('height')}", font=fb, fill=(0, 0, 0))
    d.text((x0, y0 + 30), (c.get("title") or "")[:70], font=fr, fill=(80, 80, 80))
sheet.save("cand_sheet.jpg", quality=82)
print(f"sheet saved: {len(tiles)} tiles")
