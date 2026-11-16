#!/usr/bin/env python3
"""Download picked V010 images (CC0/CC BY) + alternates, with UA + proxy env."""
import json, os, urllib.request

OUT = "images"
os.makedirs(OUT, exist_ok=True)
d = json.load(open("img_candidates.json"))

PICKS = {
    # (key, index, filename)
    ("beat1_magazine", 4, "beat1_science_invention_1928.jpg"),   # CC0, 1275x1744
    ("beat1_magazine", 16, "beat1b_popular_science_1940.jpg"),   # CC BY, 722x1024
    ("beat1_magazine", 8, "beat1_alt_1960_post.jpg"),            # CC0, 1024x817 (alt)
    ("hook_calendar", 5, "hook_alt_november_page.jpg"),          # CC0, 3108x4498 (alt)
    ("payoff_dark", 3, "payoff_night_sky.jpg"),                  # CC0, 6000x4000
    ("payoff_dark", 4, "payoff_stars_galaxy.jpg"),               # CC0, 5616x3744 (alt)
}

for key, idx, fname in PICKS:
    r = d[key][idx]
    url = r["url"]
    print(f"{fname}: {r['license']} {r['width']}x{r['height']} {r['provider']} - {r['title']}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(os.path.join(OUT, fname), "wb") as f:
            f.write(resp.read())
        print(f"  OK {os.path.getsize(os.path.join(OUT, fname))} bytes")
    except Exception as e:
        print(f"  FAILED: {e}")
print("done")
