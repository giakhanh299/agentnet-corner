#!/usr/bin/env python3
"""Download V011 image shortlist + build a contact sheet for picking."""
import json, os, urllib.request

PICKS = {
    "hook_earth1": "https://upload.wikimedia.org/wikipedia/commons/a/ae/First_Color_Photograph_of_Earth_from_Space.jpg",
    "hook_earth2": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pd36-1-gsfc_20171208_archive_e002130.jpg",
    "beat1_nunavut": "https://images.rawpixel.com/image_1300/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvcGQzNi0xLXBpYTEzOTYzLmpwZw.jpg",
    "beat2_glacier1": "https://upload.wikimedia.org/wikipedia/commons/a/ad/Hardangerj%C3%B8kulen%2C_luftfoto.jpg",
    "beat2_glacier2": "https://upload.wikimedia.org/wikipedia/commons/4/41/Mount_Chudleigh.jpg",
    "beat3_lakes_space": "https://upload.wikimedia.org/wikipedia/commons/7/76/Great_Lakes_from_space-ES-Grandes_Lagos_Norteamerica.png",
    "beat3_superior": "https://live.staticflickr.com/7461/16077159158_7f211bb8e6_b.jpg",
    "payoff_moraine1": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Moraine_Lake%2C_Canada_%28Unsplash_tbix9lcZ8lw%29.jpg",
    "payoff_moraine2": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Moraine_Lake%2C_Canada_%28Unsplash_O1lz53oVK2M%29.jpg",
    "payoff_moraine3": "https://upload.wikimedia.org/wikipedia/commons/6/65/Moraine_Lake_%28Unsplash%29.jpg",
}

os.makedirs("images", exist_ok=True)
ok = []
for name, url in PICKS.items():
    ext = ".png" if url.lower().endswith(".png") else ".jpg"
    path = f"images/{name}{ext}"
    if os.path.exists(path):
        print(f"skip {name} (exists)")
        ok.append(path)
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgentNet-V011/1.0 (research; contact: local)"})
        with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
            f.write(r.read())
        print(f"OK {name}: {os.path.getsize(path)} bytes")
        ok.append(path)
    except Exception as e:
        print(f"FAIL {name}: {e}")

# contact sheet with PIL
from PIL import Image, ImageDraw
CELL = (360, 640)
cols = 3
rows = (len(ok) + cols - 1) // cols
sheet = Image.new("RGB", (cols * CELL[0], rows * CELL[1]), "black")
d = ImageDraw.Draw(sheet)
for i, p in enumerate(ok):
    try:
        im = Image.open(p).convert("RGB")
        im.thumbnail(CELL)
        x, y = (i % cols) * CELL[0], (i // cols) * CELL[1]
        sheet.paste(im, (x + (CELL[0] - im.width) // 2, y + (CELL[1] - im.height) // 2))
        d.text((x + 8, y + 8), os.path.basename(p), fill="yellow")
    except Exception as e:
        print(f"sheet FAIL {p}: {e}")
sheet.save("contact_sheet.jpg", quality=88)
print(f"saved contact_sheet.jpg {sheet.size}")
