#!/usr/bin/env python3
"""Build the 7 countdown stage cards for V013 with PIL (1080x1920).

Layout (adapted from v009 build_cards.py): title (top) + photo
(cover-cropped) + Top-5 list (#1 on top, #5 at bottom) + waveform strip
(real RMS envelope of the beat's sound sample) + end card.
Labels match the spoken script post-probe ("bán bánh mì" instead of
"rao"; "quay số" instead of "modem" — on-screen text keeps the real
sound names: "Rao bánh mì", "Modem quay số").
Beat tags (script): n2 "GIAI ĐIỆU 1902 — HƠN 100 NĂM TRƯỚC",
n1 "QUAY SỐ XONG MỚI LÊN MẠNG" (pill overlay on the photo).
"""
import os

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/hatch/workspace/agentnet-corner/video_production/v013-iconic-sounds-45s"
OUT = os.path.join(BASE, "cards")
IMG = os.path.join(BASE, "images")
SND = os.path.join(BASE, "sounds")
FONT_DIR = "/home/hatch/workspace/agentnet-corner/stickman-shorts/src/assets/fonts"

W, H = 1080, 1920
CREAM = (255, 247, 232)
INK = (31, 26, 23)
RED = (217, 56, 30)
GOLD = (232, 161, 0)
GREY = (150, 140, 130)
ROW_HL = (255, 227, 194)
ROW_HL1 = (255, 233, 168)
ROW_BG = (255, 255, 255)

BOLD = os.path.join(FONT_DIR, "BeVietnamPro-Bold.ttf")
REG = os.path.join(FONT_DIR, "BeVietnamPro-Regular.ttf")

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def cover_crop(img, tw, th, y_frac=0.5):
    w, h = img.size
    target = tw / th
    if w / h > target:
        nw = int(h * target)
        x0 = (w - nw) // 2
        box = (x0, 0, x0 + nw, h)
    else:
        nh = int(w / target)
        y0 = int((h - nh) * y_frac)
        box = (0, y0, w, y0 + nh)
    return img.crop(box).resize((tw, th), Image.LANCZOS)

def wave_bars(sample_wav, n_bars=54):
    """RMS envelope of the sample, normalized to 0..1, n_bars values."""
    x, sr = sf.read(sample_wav, dtype="float32")
    if x.ndim > 1:
        x = x[:, 0]
    edges = np.linspace(0, len(x), n_bars + 1).astype(int)
    bars = []
    for i in range(n_bars):
        seg = x[edges[i]:edges[i + 1]]
        bars.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
    m = max(bars) or 1.0
    return [b / m for b in bars]

PHOTOS = {
    5: ("n5_bell.jpg", 0.42),       # bell is centre-frame, slightly high
    4: ("n4_motorbike.jpg", 0.5),
    3: ("n3_banhmi.jpg", 0.45),     # banh mi is centre-frame
    2: ("n2_phone.jpg", 0.5),
    1: ("n1_modem.jpg", 0.5),
}

SAMPLES = {
    5: "sample_bell.wav",
    4: "sample_motorbike.wav",
    3: "sample_vendor.wav",
    2: "sample_ringtone.wav",
    1: "sample_modem.wav",
}

LABELS = {
    5: "Chuông trường",
    4: "Xe máy đề nổ",
    3: "Rao bánh mì",
    2: "Nhạc chuông cục gạch",
    1: "Modem quay số",
}

TAGS = {
    2: "GIAI ĐIỆU 1902 — HƠN 100 NĂM TRƯỚC",
    1: "QUAY SỐ XONG MỚI LÊN MẠNG",
}

def draw_list(draw, revealed, current):
    y0 = 990
    f_num = font(BOLD, 40)
    f_txt = font(BOLD, 40)
    f_dot = font(BOLD, 44)
    for i, n in enumerate([1, 2, 3, 4, 5]):
        y = y0 + i * 146
        x0, x1 = 36, 1044
        if n == current:
            hl = ROW_HL1 if n == 1 else ROW_HL
            draw.rounded_rectangle([x0, y, x1, y + 134], radius=22, fill=hl)
        cx, cy, r = 96, y + 67, 42
        if n in revealed:
            fill = GOLD if n == 1 else RED
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
            txt = f"#{n}"
            tw = draw.textlength(txt, font=f_num)
            draw.text((cx - tw / 2, cy - 30), txt, font=f_num, fill=(255, 255, 255))
        else:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREY, width=4)
            txt = f"#{n}"
            tw = draw.textlength(txt, font=f_num)
            draw.text((cx - tw / 2, cy - 30), txt, font=f_num, fill=GREY)
        tx = 168
        if n in revealed:
            lines = wrap(draw, LABELS[n], f_txt, 860)
            ly = y + 67 - (len(lines) * 48) // 2
            for ln in lines:
                draw.text((tx, ly), ln, font=f_txt, fill=INK)
                ly += 48
        else:
            draw.text((tx, y + 67 - 30), "• • •", font=f_dot, fill=GREY)

def draw_title(draw):
    f1 = font(BOLD, 76)
    t1, t2 = "TOP 5 ÂM THANH", "NGHE LÀ NHỚ NGAY"
    for t, y in ((t1, 44), (t2, 132)):
        tw = draw.textlength(t, font=f1)
        draw.text(((W - tw) / 2, y), t, font=f1, fill=INK)
    draw.rounded_rectangle([(W - 220) / 2, 232, (W + 220) / 2, 242], radius=5, fill=RED)

def draw_wave(draw, bars, color, y_top=1744, height=72):
    """54 vertical bars across x=36..1044, bottom-aligned."""
    x0, x1 = 36, 1044
    bw = (x1 - x0) / len(bars)
    for i, b in enumerate(bars):
        bh = max(4, int(b * height))
        x = x0 + i * bw
        draw.rounded_rectangle([x + 2, y_top + height - bh, x + bw - 2, y_top + height],
                               radius=3, fill=color)

def build_stage(name, photo_num, y_frac, revealed, current, tag=None, wave_color=RED):
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw_title(draw)
    ph = Image.open(os.path.join(IMG, PHOTOS[photo_num][0])).convert("RGB")
    ph = cover_crop(ph, 1080, 710, y_frac)
    img.paste(ph, (0, 258))
    if tag:
        # dark pill overlay on the photo bottom edge
        overlay = Image.new("RGBA", (1080, 76), (0, 0, 0, 160))
        img.paste(overlay, (0, 892), overlay)
        d2 = ImageDraw.Draw(img)
        f_tag = font(BOLD, 38)
        tw = d2.textlength(tag, font=f_tag)
        d2.text(((W - tw) / 2, 908), tag, font=f_tag, fill=(255, 255, 255))
    draw_list(draw, revealed, current)
    bars = wave_bars(os.path.join(SND, SAMPLES[photo_num]))
    draw_wave(draw, bars, wave_color)
    img.save(os.path.join(OUT, name))
    print(f"saved {name}")

def build_endcard():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    ph = Image.open(os.path.join(IMG, "n1_modem.jpg")).convert("RGB")
    ph = cover_crop(ph, 1080, 480, 0.5)
    img.paste(ph, (0, 150))
    f_big = font(BOLD, 84)
    f_sub = font(BOLD, 56)
    f_q = font(REG, 40)
    lines = ["BẠN NHỚ ÂM THANH", "NÀO NHẤT?"]
    y = 700
    for ln in lines:
        tw = draw.textlength(ln, font=f_big)
        draw.text(((W - tw) / 2, y), ln, font=f_big, fill=INK)
        y += 104
    sub = "Bình luận số của nó nhé!"
    tw = draw.textlength(sub, font=f_sub)
    draw.text(((W - tw) / 2, 950), sub, font=f_sub, fill=RED)
    q = "Chuông trường · Xe máy · Rao bánh mì · Nhạc chuông · Modem"
    qlines = wrap(draw, q, f_q, 880)
    y = 1120
    for ln in qlines:
        tw = draw.textlength(ln, font=f_q)
        draw.text(((W - tw) / 2, y), ln, font=f_q, fill=(90, 78, 66))
        y += 54
    img.save(os.path.join(OUT, "stage_end.png"))
    print("saved stage_end.png")

os.makedirs(OUT, exist_ok=True)
# (name, photo_num, revealed, current, tag, wave_color)
STAGES = [
    ("stage_hook.png", 5, set(), 5, None, GREY),
    ("stage_n5.png", 5, {5}, 5, None, RED),
    ("stage_n4.png", 4, {5, 4}, 4, None, RED),
    ("stage_n3.png", 3, {5, 4, 3}, 3, None, RED),
    ("stage_n2.png", 2, {5, 4, 3, 2}, 2, TAGS[2], RED),
    ("stage_n1.png", 1, {5, 4, 3, 2, 1}, 1, TAGS[1], GOLD),
]
for name, num, revealed, current, tag, wc in STAGES:
    _, yf = PHOTOS[num]
    build_stage(name, num, yf, revealed, current, tag, wc)
build_endcard()
print("done")
