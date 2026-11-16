#!/usr/bin/env python3
"""Draw the two full-frame cards for V014 (1080x1920, Be Vietnam Pro Bold).

- card_calendar.png: beat 3 (31.49-42.88s) — '7 VIDEO / TUAN' + 7 day boxes
  (T2..CN, each marked VIDEO) + 'MOT BUOI TOI = MOT VIDEO'.
- card_payoff.png: payoff (43.48-52.09s) — 'MAY LAM HO GIO CUA BAN' +
  CTA 'BAN CHON CACH NAO?' + 'BINH LUAN NHE!'.
All text is baked into the images (drawtext labels are used only on the
screen-record segments). Bottom ~350px is kept clear for the ASS captions.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT = "/home/hatch/workspace/agentnet-corner/video_production/v011-canada-lakes-45s/BeVietnamPro-Bold.ttf"
OUT = "/home/hatch/workspace/agentnet-corner/video_production/v014-no-part-time-job-50s"

NAVY = (13, 27, 48)
NAVY2 = (19, 42, 74)
YELLOW = (255, 209, 102)
LIGHT = (125, 211, 252)
WHITE = (255, 255, 255)
GREY = (180, 195, 210)
GREEN = (74, 222, 128)

def font(size):
    return ImageFont.truetype(FONT, size)

def background():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(NAVY[0] + (NAVY2[0] - NAVY[0]) * t)
        g = int(NAVY[1] + (NAVY2[1] - NAVY[1]) * t)
        b = int(NAVY[2] + (NAVY2[2] - NAVY[2]) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    return img, d

def center_text(d, y, text, fnt, fill):
    w = d.textlength(text, font=fnt)
    d.text(((W - w) / 2, y), text, font=fnt, fill=fill)
    return w

def center_text_in(d, x, y, w, text, fnt, fill):
    tw = d.textlength(text, font=fnt)
    d.text((x + (w - tw) / 2, y), text, font=fnt, fill=fill)

# ---------------- calendar card ----------------
img, d = background()
center_text(d, 220, "7 VIDEO / TUẦN", font(96), WHITE)
center_text(d, 350, "KHÔNG CẦN QUAY PHIM", font(56), YELLOW)
days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
box_w, box_h, gap = 128, 210, 18
x0 = (W - (7 * box_w + 6 * gap)) // 2
y0 = 560
for i, day in enumerate(days):
    x = x0 + i * (box_w + gap)
    d.rounded_rectangle([x, y0, x + box_w, y0 + box_h], radius=18,
                        fill=(28, 58, 96), outline=(90, 130, 180), width=3)
    center_text_in(d, x, y0 + 22, box_w, day, font(52), WHITE)
    # play triangle
    cx, cy = x + box_w // 2, y0 + 105
    d.polygon([(cx - 18, cy - 26), (cx - 18, cy + 26), (cx + 24, cy)], fill=GREEN)
    center_text_in(d, x, y0 + 150, box_w, "VIDEO", font(30), LIGHT)
center_text(d, 900, "MỘT BUỔI TỐI = MỘT VIDEO", font(54), WHITE)
center_text(d, 990, "Một tuần, bạn có bảy video.", font(44), GREY)
img.save(f"{OUT}/card_calendar.png")
print("saved card_calendar.png")

# ---------------- payoff card ----------------
img, d = background()
center_text(d, 620, "MÁY LÀM HỘ", font(124), WHITE)
center_text(d, 760, "GIỜ CỦA BẠN", font(124), YELLOW)
center_text(d, 1020, "BẠN CHỌN CÁCH NÀO?", font(76), WHITE)
center_text(d, 1140, "BÌNH LUẬN NHÉ!", font(56), LIGHT)
img.save(f"{OUT}/card_payoff.png")
print("saved card_payoff.png")
