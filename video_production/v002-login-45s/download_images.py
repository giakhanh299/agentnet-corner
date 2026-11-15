#!/usr/bin/env python3
"""Download chosen V002 image candidates from img_candidates.json."""
import json, urllib.request, os

d = json.load(open("img_candidates.json"))

def pick(key, title_part):
    for r in d[key]:
        if title_part.lower() in (r.get("title") or "").lower():
            return r
    raise SystemExit(f"no match for {key} / {title_part}")

PICKS = [
    ("hook_ship", "Ships Turbulent Sea", "img1a_ship_painting.jpg"),
    ("hook_ship", "Sail Ocean", "img1b_sail_ocean.jpg"),
    ("beat1_rope", "White rope black", "img2a_rope_white.jpg"),
    ("beat1_rope", "Rope Line", "img2b_rope_line.jpg"),
    ("beat2_logbook", "Ye Olde Logbook", "img3a_logbook.jpg"),
    ("beat2_logbook", "Typical page", "img3b_logbook_page.jpg"),
    ("beat3_login", "Facebook Login", "img4_login.jpg"),
]
# rawpixel 3610x2317 with no title: pick by size
for r in d["beat2_logbook"]:
    if r.get("width") == 3610:
        PICKS.append(("beat2_logbook", r["title"] or "", "img3c_rawpixel.jpg"))
        break

os.makedirs("images", exist_ok=True)
for key, title, fname in PICKS:
    r = pick(key, title) if title else None
    if r is None:
        for c in d[key]:
            if c.get("width") == 3610:
                r = c
    url = r["url"]
    req = urllib.request.Request(url, headers={"User-Agent": "AgentNet-V002/1.0 (research; contact: local)"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(f"images/{fname}", "wb") as f:
            data = resp.read()
            f.write(data)
        print(f"{fname}: {len(data)} bytes <- {r['license']} {r['provider']} :: {r.get('title')} :: creator={r.get('creator')} :: landing={r.get('foreign_landing_url')}")
    except Exception as e:
        print(f"{fname}: FAILED {e} (url {url[:80]})")
