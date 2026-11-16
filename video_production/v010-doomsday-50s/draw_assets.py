#!/usr/bin/env python3
"""Draw V010 own assets (1080x1920): November 2026 calendar (13 circled
red), 1960-forecast hyperbolic graph + zoom, real growth-rate graph,
forecast-vs-actual bars. All data from the verified script sources.
Fonts: Be Vietnam Pro (stickman repo). Background: cream #F6F5F0."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = os.path.expanduser("~/workspace/agentnet-corner/stickman-shorts/src/assets/fonts")
BOLD = os.path.join(FONT_DIR, "BeVietnamPro-Bold.ttf")
REG = os.path.join(FONT_DIR, "BeVietnamPro-Regular.ttf")
for p in (BOLD, REG):
    fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Be Vietnam Pro"
CREAM = "#F6F5F0"
INK = "#141414"
RED = "#D9381E"
NAVY = "#1F3A5F"
TEAL = "#0E7C6B"

os.makedirs("images", exist_ok=True)

# ---------------------------------------------------------------- calendar
W, H = 1080, 1920
im = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(im)
f_title = ImageFont.truetype(BOLD, 92)
f_sub = ImageFont.truetype(BOLD, 54)
f_wd = ImageFont.truetype(BOLD, 44)
f_day = ImageFont.truetype(BOLD, 52)
f_day_red = ImageFont.truetype(BOLD, 56)

d.text((W // 2, 430), "THÁNG 11", font=f_title, fill=INK, anchor="mm")
d.text((W // 2, 530), "NĂM 2026", font=f_sub, fill=RED, anchor="mm")
# November 2026: Nov 1 = Sunday. Sunday-first grid.
wd = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"]
x0, y0 = 70, 700
cw, ch = 134, 140
for i, w in enumerate(wd):
    d.text((x0 + i * cw + cw // 2, y0 + 30), w, font=f_wd, fill=NAVY, anchor="mm")
d.line([(x0, y0 + 70), (x0 + 7 * cw, y0 + 70)], fill=INK, width=3)
# days: 1..30, day 1 in column 0 (Sunday)
for day in range(1, 31):
    col = (day - 1) % 7
    row = (day - 1) // 7
    cx = x0 + col * cw + cw // 2
    cy = y0 + 110 + row * ch + ch // 2
    if day == 13:
        d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], outline=RED, width=10)
        d.text((cx, cy), "13", font=f_day_red, fill=RED, anchor="mm")
    else:
        d.text((cx, cy), str(day), font=f_day, fill=INK, anchor="mm")
# No bottom note: the top of the frame stays clear for the hook label
# (drawtext at y=h*0.09) and the bottom stays clear for captions.
im.save("images/hook_calendar.png")
print("saved images/hook_calendar.png")

# ------------------------------------------------- graph 1: 1960 forecast
# von Foerster hyperbolic: P(t) = k / (2026.87 - t); k set so P(1960)=3.0
k = 3.0 * (2026.87 - 1960.0)
t = np.linspace(1800, 2026.5, 400)
P = k / (2026.87 - t)

def portrait_plot():
    fig = plt.figure(figsize=(10.8, 19.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.16, 0.30, 0.78, 0.52])
    ax.set_facecolor(CREAM)
    return fig, ax

fig, ax = portrait_plot()
ax.plot(t, P, color=RED, lw=5)
ax.axvline(2026.87, color=RED, lw=2, ls="--")
ax.plot([1960], [3.0], "o", color=NAVY, ms=14)
ax.annotate("1960: 3 tỉ", (1960, 3.0), xytext=(1830, 18),
            fontsize=30, color=NAVY, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=2))
ax.annotate("13/11/2026", (2026.87, 45), xytext=(1965, 52),
            fontsize=30, color=RED, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=RED, lw=2))
ax.set_xlim(1800, 2030)
ax.set_ylim(0, 60)
ax.set_xlabel("NĂM", fontsize=30, color=INK)
ax.set_ylabel("DÂN SỐ (TỈ NGƯỜI)", fontsize=30, color=INK)
ax.tick_params(labelsize=26, colors=INK)
for s in ax.spines.values():
    s.set_color(INK)
    s.set_linewidth(2)
fig.text(0.5, 0.88, "CÔNG THỨC 1960:", ha="center", fontsize=44,
         color=INK, fontweight="bold")
fig.text(0.5, 0.84, "DÂN SỐ TĂNG VỌT", ha="center", fontsize=44,
         color=RED, fontweight="bold")
fig.savefig("images/graph_forecast.png")
plt.close(fig)
print("saved images/graph_forecast.png")

# zoom version: 2000-2027, y 0-250 (no data dot: the curve alone shows the explosion)
fig, ax = portrait_plot()
ax.plot(t, P, color=RED, lw=5)
ax.axvline(2026.87, color=RED, lw=2, ls="--")
ax.annotate("VÔ CÙNG?", (2026.87, 200), xytext=(2008, 215),
            fontsize=34, color=RED, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=RED, lw=2))
ax.set_xlim(2000, 2030)
ax.set_ylim(0, 250)
ax.set_xlabel("NĂM", fontsize=30, color=INK)
ax.set_ylabel("DÂN SỐ (TỈ NGƯỜI)", fontsize=30, color=INK)
ax.tick_params(labelsize=26, colors=INK)
for s in ax.spines.values():
    s.set_color(INK)
    s.set_linewidth(2)
fig.text(0.5, 0.88, "CÀNG GẦN 2026,", ha="center", fontsize=44,
         color=INK, fontweight="bold")
fig.text(0.5, 0.84, "CÀNG VỌT LÊN CAO", ha="center", fontsize=44,
         color=RED, fontweight="bold")
fig.savefig("images/graph_forecast_zoom.png")
plt.close(fig)
print("saved images/graph_forecast_zoom.png")

# ------------------------------------------- graph 2: real growth rate
years = np.array([1950, 1955, 1960, 1963, 1970, 1980, 1990, 2000, 2010, 2020, 2023])
rate = np.array([1.8, 1.9, 2.0, 2.2, 2.0, 1.7, 1.5, 1.3, 1.1, 0.95, 0.87])
# Piecewise-linear through the verified points (no smoothing: a rolling
# mean created false dips at both ends of the curve).
xs = np.linspace(1950, 2023, 300)
ys = np.interp(xs, years, rate)

fig, ax = portrait_plot()
ax.plot(xs, ys, color=TEAL, lw=5)
ax.plot([1963], [2.2], "o", color=RED, ms=16)
ax.annotate("ĐỈNH 1963: ~2,2%", (1963, 2.2), xytext=(1968, 2.35),
            fontsize=30, color=RED, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=RED, lw=2))
ax.plot([2023], [0.87], "o", color=NAVY, ms=14)
ax.annotate("2023: 0,87%", (2023, 0.87), xytext=(1988, 0.45),
            fontsize=30, color=NAVY, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=2))
ax.set_xlim(1950, 2025)
ax.set_ylim(0, 2.6)
ax.set_xlabel("NĂM", fontsize=30, color=INK)
ax.set_ylabel("TĂNG TRƯỞNG/NĂM (%)", fontsize=30, color=INK)
ax.tick_params(labelsize=26, colors=INK)
for s in ax.spines.values():
    s.set_color(INK)
    s.set_linewidth(2)
fig.text(0.5, 0.88, "THỰC TẾ: TĂNG CHẬM LẠI", ha="center", fontsize=44,
         color=INK, fontweight="bold")
fig.text(0.5, 0.84, "SAU ĐỈNH 1963", ha="center", fontsize=44,
         color=TEAL, fontweight="bold")
fig.savefig("images/graph_growth_rate.png")
plt.close(fig)
print("saved images/graph_growth_rate.png")

# ------------------------------------------- graph 3: forecast vs actual
# LINEAR scale (a log scale would shrink the 12-25x gap visually).
# Red bar = forecast low end 96 with a whisker up to the high end 205;
# teal bar = actual 8.2. The tiny teal bar IS the point.
fig, ax = portrait_plot()
ax.bar([0], [96], width=0.55, color=RED, edgecolor=INK, lw=2)
ax.errorbar([0], [96], yerr=[[0], [205 - 96]], fmt="none", ecolor=RED,
            elinewidth=4, capsize=18, capthick=4)
ax.bar([1], [8.2], width=0.55, color=TEAL, edgecolor=INK, lw=2)
ax.text(0, 222, "96-205 TỈ", ha="center", fontsize=34, color=RED, fontweight="bold")
ax.text(1, 16, "8,2 TỈ", ha="center", fontsize=34, color=TEAL, fontweight="bold")
ax.set_xticks([0, 1])
ax.set_xticklabels(["DỰ BÁO 1960", "THỰC TẾ 2026"], fontsize=30, color=INK)
ax.set_ylim(0, 250)
ax.set_ylabel("DÂN SỐ (TỈ NGƯỜI)", fontsize=28, color=INK)
ax.tick_params(labelsize=26, colors=INK)
for s in ax.spines.values():
    s.set_color(INK)
    s.set_linewidth(2)
fig.text(0.5, 0.88, "DỰ BÁO vs THỰC TẾ", ha="center", fontsize=44,
         color=INK, fontweight="bold")
fig.text(0.5, 0.84, "CHÊNH NHAU HƠN 10 LẦN", ha="center", fontsize=40,
         color=RED, fontweight="bold")
fig.savefig("images/graph_bars.png")
plt.close(fig)
print("saved images/graph_bars.png")
print("ALL DRAWN")
