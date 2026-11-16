#!/usr/bin/env python3
"""Search Openverse for V007 images (CC0 first, CC BY as fallback)."""
import json, time, urllib.request, urllib.parse

BASE = "https://api.openverse.org/v1/images/"
QUERIES = {
    "n5_key": ["key in door lock", "key turning in lock", "hand inserting key lock door"],
    "n4_hinge": ["door hinge close up", "door hinge", "door closing hinge metal"],
    "n3_stone": ["smooth stone in hand palm", "hand holding pebble", "stone in palm hand"],
    "n2_wheel": ["truck wheel road", "wheel in rail groove", "train wheel track closeup"],
    "n1_latch": ["door latch bolt", "door bolt lock closeup", "door latch close up"],
}

def search(q, lic):
    params = urllib.parse.urlencode({
        "q": q, "license": lic, "license_type": "commercial", "page_size": 8,
    })
    req = urllib.request.Request(BASE + "?" + params,
                                 headers={"User-Agent": "AgentNet-V007/1.0 (research; contact: local)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

out = {}
for key, qs in QUERIES.items():
    results = []
    for q in qs:
        for lic in ("cc0", "by"):
            try:
                data = search(q, lic)
                for r in data.get("results", []):
                    results.append({
                        "title": r.get("title"), "url": r.get("url"),
                        "license": r.get("license"),
                        "license_url": r.get("license_url"),
                        "creator": r.get("creator"),
                        "foreign_landing_url": r.get("foreign_landing_url"),
                        "width": r.get("width"), "height": r.get("height"),
                        "filesize": r.get("filesize"), "filetype": r.get("filetype"),
                        "provider": r.get("provider"),
                    })
                print(f"{key}: q={q!r} lic={lic} -> {len(data.get('results', []))} results", flush=True)
                if data.get("results"):
                    break
            except Exception as e:
                print(f"{key}: q={q!r} lic={lic} FAILED: {e}", flush=True)
            time.sleep(4)
        time.sleep(2)
    out[key] = results

with open("img_candidates.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved img_candidates.json")
for k, v in out.items():
    print(f"{k}: {len(v)} candidates")
