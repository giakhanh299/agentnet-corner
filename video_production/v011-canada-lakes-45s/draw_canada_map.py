#!/usr/bin/env python3
"""Draw the Canada map for V011 beat 1 (own redraw, no reuse of the original).

Source data: Natural Earth 110m admin_0 countries GeoJSON (public domain),
/tmp/ne110.geojson. Canada polygon in equirectangular projection, red
border, dense lake dots inside the land polygon (point-in-polygon), Great
Lakes as small light-blue ellipses at real lon/lat (drawn BEFORE the
border so the border line crosses them, as in reality). A large faded copy
of the map fills the portrait canvas behind the sharp map so the frame is
not empty navy. Canvas 2160x3840 portrait.
"""
import json, math, random
from PIL import Image, ImageDraw

W, H = 2160, 3840
NAVY = (10, 30, 46)
LAND = (46, 110, 138)
RED = (230, 57, 70)
DOT = (127, 212, 255)
DOT2 = (255, 255, 255)
LAKE = (127, 212, 255)

MX0, MX1 = 40, W - 40
MY0, MY1 = 1180, 2620
LON0, LON1 = -168.5, -52.0
LAT0, LAT1 = 41.5, 83.5
KX = (MX1 - MX0) / ((LON1 - LON0) * math.cos(math.radians(60)))
KY = (MY1 - MY0) / (LAT1 - LAT0)
S = min(KX, KY)
MAP_W = (LON1 - LON0) * math.cos(math.radians(60)) * S
MAP_H = (LAT1 - LAT0) * S
OX = MX0 + (MX1 - MX0 - MAP_W) / 2
OY = MY0 + (MY1 - MY0 - MAP_H) / 2

def proj(lon, lat):
    x = OX + (lon - LON0) * math.cos(math.radians(60)) * S
    y = OY + (LAT1 - lat) * S
    return (x, y)

def point_in_polygon(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

geo = json.load(open("/tmp/ne110.geojson"))
can = None
for f in geo["features"]:
    props = f.get("properties", {})
    if props.get("ADMIN") == "Canada" or props.get("NAME") == "Canada":
        can = f["geometry"]
        break
assert can, "Canada not found in GeoJSON"
print("Canada geometry type:", can["type"])

polys = []
if can["type"] == "Polygon":
    polys = [can["coordinates"]]
elif can["type"] == "MultiPolygon":
    polys = can["coordinates"]

all_polys_xy = []
for poly in polys:
    rings_xy = [[proj(lon, lat) for lon, lat in ring] for ring in poly]
    all_polys_xy.append(rings_xy)

img = Image.new("RGB", (W, H), NAVY)
d = ImageDraw.Draw(img, "RGBA")

# --- faded big background map (fills the portrait canvas) ---
bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
db = ImageDraw.Draw(bg)
for rings_xy in all_polys_xy:
    db.polygon(rings_xy[0], fill=LAND + (38,))
    for hole in rings_xy[1:]:
        db.polygon(hole, fill=(0, 0, 0, 0))
bg_big = bg.resize((int(W * 1.7), int(H * 1.7)), Image.LANCZOS)
img.paste(bg_big, (-int(W * 0.35), -int(H * 0.35)), bg_big)

# faint graticule every 10 deg
for lon in range(-170, -49, 10):
    x0, _ = proj(lon, LAT0)
    d.line([(x0, OY), (x0, OY + MAP_H)], fill=(255, 255, 255, 18), width=2)
for lat in range(50, 84, 10):
    _, y = proj(LON0, lat)
    d.line([(OX, y), (OX + MAP_W, y)], fill=(255, 255, 255, 18), width=2)

# land fill
for rings_xy in all_polys_xy:
    d.polygon(rings_xy[0], fill=LAND)
    for hole in rings_xy[1:]:
        d.polygon(hole, fill=NAVY)

# Great Lakes ellipses at real lon/lat (small, drawn BEFORE the border)
GREAT_LAKES = [
    ("Superior", -87.5, 47.0, 2.6, 1.0),
    ("Huron", -82.0, 44.6, 1.5, 0.9),
    ("Erie", -80.0, 42.2, 1.7, 0.45),
    ("Ontario", -78.5, 43.6, 1.2, 0.45),
]
for name, clon, clat, rx_deg, ry_deg in GREAT_LAKES:
    cx, cy = proj(clon, clat)
    rx = rx_deg * math.cos(math.radians(60)) * S
    ry = ry_deg * S
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=LAKE)

# red border around every ring (drawn after the lakes)
for rings_xy in all_polys_xy:
    for ring in rings_xy:
        d.line(ring + [ring[0]], fill=RED, width=7, joint="curve")

# lake dots: scatter inside land polygons
random.seed(11)
main = max(all_polys_xy, key=lambda rs: len(rs[0]))
main_poly = main[0]
minx = min(p[0] for p in main_poly); maxx = max(p[0] for p in main_poly)
miny = min(p[1] for p in main_poly); maxy = max(p[1] for p in main_poly)
placed = 0
tries = 0
while placed < 260 and tries < 60000:
    tries += 1
    if random.random() < 0.55:
        lon = random.uniform(-95, -75)
        lat = random.uniform(49, 58)
    else:
        lon = random.uniform(LON0, LON1)
        lat = random.uniform(LAT0, LAT1)
    x, y = proj(lon, lat)
    if not (minx <= x <= maxx and miny <= y <= maxy):
        continue
    inside = False
    for rings_xy in all_polys_xy:
        if point_in_polygon(x, y, rings_xy[0]):
            inside = True
            break
    if not inside:
        continue
    r = random.uniform(5, 11)
    col = DOT if random.random() < 0.7 else DOT2
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    placed += 1
print(f"placed {placed} lake dots in {tries} tries")

img.save("images/canada_map.png")
print("saved images/canada_map.png", img.size)
