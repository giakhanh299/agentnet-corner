#!/usr/bin/env python3
"""Build the 7 countdown stage cards for V005 with PIL (1080x1920).

Layout: title (top) + photo (cover-cropped) + Top-5 list (#1 on top, #5
at bottom) + end card. Rows show the full spoken quote (wrapped to <=2
lines); unrevealed rows show dots. #1's row gets a warm amber highlight
(emotional payoff, not a "win" look).
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "cards"
IMG = "images"
FONT_DIR = "/home/hatch/workspace/agentnet-corner/stickman-shorts/src/assets/fonts"

W, H = 1080, 1920
CREAM = (255, 247, 232)
INK = (31, 26, 23)
RED = (217, 56, 30)
GOLD = (232, 161, 0)
GREY = (150, 140, 130)
ROW_HL = (255, 227, 194)      # current row highlight
ROW_HL1 = (255, 233, 168)     # #1 row highlight (warm amber)
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
    """Crop img to tw:th aspect, y_frac = vertical centre (0 top, 1 bottom)."""
    w, h = img.size
    target = tw / th
    if w / h > target:  # too wide -> crop width
        nw = int(h * target)
        x0 = (w - nw) // 2
        box = (x0, 0, x0 + nw, h)
    else:  # too tall -> crop height
        nh = int(w / target)
        y0 = int((h - nh) * y_frac)
        box = (0, y0, w, y0 + nh)
    return img.crop(box).resize((tw, th), Image.LANCZOS)

PHOTOS = {
    5: ("n5b_dinner.jpg", 0.5),
    4: ("n4b_alone.jpg", 0.5),
    3: ("n3a_mother_child.jpg", 0.5),
    2: ("n2a_window.jpg", 0.30),  # portrait source: keep the boy's head
    1: ("n1a_family.jpg", 0.5),
}

QUOTES = {
    5: "Ăn cơm đi, nguội hết rồi!",
    4: "Tao nói mày có nghe không?",
    3: "Hồi bằng tuổi mày, mẹ đã biết nấu cơm, giặt đồ.",
    2: "Con nhà người ta…",
    1: "Mẹ không cần gì đâu, con cứ lo cho con đi.",
}

def draw_list(draw, revealed, current):
    """Rows #1..#5 top->bottom, y=990..1720 (5 x 146px)."""
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
        # badge
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
        # quote or dots
        tx = 168
        if n in revealed:
            lines = wrap(draw, QUOTES[n], f_txt, 860)
            ly = y + 67 - (len(lines) * 48) // 2
            for ln in lines:
                draw.text((tx, ly), ln, font=f_txt, fill=INK)
                ly += 48
        else:
            draw.text((tx, y + 67 - 30), "• • •", font=f_dot, fill=GREY)

def draw_title(draw):
    f1 = font(BOLD, 76)
    f2 = font(BOLD, 76)
    t1, t2 = "TOP 5 CÂU NÓI", "HUYỀN THOẠI CỦA MẸ"
    for t, fnt, y in ((t1, f1, 44), (t2, f2, 132)):
        tw = draw.textlength(t, font=fnt)
        draw.text(((W - tw) / 2, y), t, font=fnt, fill=INK)
    # red underline accent
    draw.rounded_rectangle([(W - 220) / 2, 232, (W + 220) / 2, 242], radius=5, fill=RED)

def build_stage(name, photo_file, y_frac, revealed, current):
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw_title(draw)
    ph = Image.open(os.path.join(IMG, photo_file)).convert("RGB")
    ph = cover_crop(ph, 1080, 710, y_frac)
    img.paste(ph, (0, 258))
    draw_list(draw, revealed, current)
    img.save(os.path.join(OUT, name))
    print(f"saved {name}")

def build_endcard():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    ph = Image.open(os.path.join(IMG, "n1a_family.jpg")).convert("RGB")
    ph = cover_crop(ph, 1080, 480, 0.5)
    img.paste(ph, (0, 150))
    # dim overlay on photo bottom for legibility of nothing (kept simple)
    f_big = font(BOLD, 88)
    f_sub = font(BOLD, 58)
    f_q = font(REG, 40)
    lines = ["SỐ 1 CỦA BẠN", "LÀ CÂU NÀO?"]
    y = 720
    for ln in lines:
        tw = draw.textlength(ln, font=f_big)
        draw.text(((W - tw) / 2, y), ln, font=f_big, fill=INK)
        y += 108
    sub = "Bình luận nhé!"
    tw = draw.textlength(sub, font=f_sub)
    draw.text(((W - tw) / 2, 980), sub, font=f_sub, fill=RED)
    q = "“Mẹ không cần gì đâu, con cứ lo cho con đi.”"
    qlines = wrap(draw, q, f_q, 880)
    y = 1150
    for ln in qlines:
        tw = draw.textlength(ln, font=f_q)
        draw.text(((W - tw) / 2, y), ln, font=f_q, fill=(90, 78, 66))
        y += 54
    img.save(os.path.join(OUT, "stage_end.png"))
    print("saved stage_end.png")

os.makedirs(OUT, exist_ok=True)
# (name, photo_num, revealed, current)
STAGES = [
    ("stage_hook.png", 3, {3}, 3),
    ("stage_n5.png", 5, {3, 5}, 5),
    ("stage_n4.png", 4, {3, 5, 4}, 4),
    ("stage_n3.png", 3, {3, 5, 4}, 3),
    ("stage_n2.png", 2, {3, 5, 4, 2}, 2),
    ("stage_n1.png", 1, {3, 5, 4, 2, 1}, 1),
]
for name, num, revealed, current in STAGES:
    f, yf = PHOTOS[num]
    build_stage(name, f, yf, revealed, current)
build_endcard()
print("done")
