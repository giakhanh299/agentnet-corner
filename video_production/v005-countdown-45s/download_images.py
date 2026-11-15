#!/usr/bin/env python3
"""Download shortlisted V005 image candidates from img_candidates.json."""
import json, urllib.request, os

d = json.load(open("img_candidates.json"))

def pick(key, title_part):
    for r in d[key]:
        if title_part.lower() in (r.get("title") or "").lower():
            return r
    return None

PICKS = [
    ("n5_meal", "Deepawali Celebration", "n5a_dinner.jpg"),
    ("n5_meal", "Pre-Race Dinner", "n5b_dinner.jpg"),
    ("n5_meal", "Chicken Pra Ram", "n5c_food.jpg"),
    ("n4_silence", "P1010025", "n4a_quiet.jpg"),
    ("n4_silence", "Friday night", "n4b_alone.jpg"),
    ("n4_silence", "Matt Cat", "n4c_quiet.jpg"),
    ("n3_cooking", "Mother Child", "n3a_mother_child.jpg"),
    ("n3_cooking", "Christmas Baking", "n3b_baking.jpg"),
    ("n2_neighbor", "Boy Looking Out Window", "n2a_window.jpg"),
    ("n2_neighbor", "Of trains", "n2b_train.jpg"),
    ("n2_neighbor", "a.y.f.k.m. look", "n2c_look.jpg"),
    ("n1_mother", "Family Portrait", "n1a_family.jpg"),
    ("n1_mother", "Black Family", "n1b_family.jpg"),
    ("n1_mother", "WHATTTTT", "n1c_surprised.jpg"),
]

os.makedirs("images", exist_ok=True)
chosen = []
for key, title, fname in PICKS:
    r = pick(key, title)
    if r is None:
        print(f"{fname}: NO MATCH for {key} / {title}")
        continue
    url = r["url"]
    req = urllib.request.Request(url, headers={"User-Agent": "AgentNet-V005/1.0 (research; contact: local)"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(f"images/{fname}", "wb") as f:
            data = resp.read()
            f.write(data)
        print(f"{fname}: {len(data)} bytes {r.get('width')}x{r.get('height')} <- {r['license']} {r['provider']} :: {r.get('title')} :: creator={r.get('creator')} :: landing={r.get('foreign_landing_url')}")
        chosen.append({"file": fname, "key": key, "title": r.get("title"), "license": r.get("license"),
                       "license_url": r.get("license_url"), "creator": r.get("creator"),
                       "landing": r.get("foreign_landing_url"), "url": url,
                       "width": r.get("width"), "height": r.get("height"), "provider": r.get("provider")})
    except Exception as e:
        print(f"{fname}: FAILED {e} (url {url[:80]})")

with open("images/shortlist.json", "w") as f:
    json.dump(chosen, f, indent=2, ensure_ascii=False)
print(f"downloaded {len(chosen)}/{len(PICKS)}")
