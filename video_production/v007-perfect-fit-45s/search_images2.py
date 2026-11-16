#!/usr/bin/env python3
"""Round-2 search for the n2 wheel image + view deeper candidates."""
import json, time, urllib.request, urllib.parse

BASE = "https://api.openverse.org/v1/images/"
QUERIES = ["train wheel rail", "railway wheel closeup", "wheel flange rail", "tire groove road"]

def search(q, lic):
    params = urllib.parse.urlencode({
        "q": q, "license": lic, "license_type": "commercial", "page_size": 8,
    })
    req = urllib.request.Request(BASE + "?" + params,
                                 headers={"User-Agent": "AgentNet-V007/1.0 (research; contact: local)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

out = []
for q in QUERIES:
    for lic in ("cc0", "by"):
        try:
            data = search(q, lic)
            for r in data.get("results", []):
                out.append({
                    "title": r.get("title"), "url": r.get("url"),
                    "license": r.get("license"), "license_url": r.get("license_url"),
                    "creator": r.get("creator"),
                    "foreign_landing_url": r.get("foreign_landing_url"),
                    "width": r.get("width"), "height": r.get("height"),
                    "filesize": r.get("filesize"), "filetype": r.get("filetype"),
                    "provider": r.get("provider"),
                })
            print(f"q={q!r} lic={lic} -> {len(data.get('results', []))} results", flush=True)
            if data.get("results"):
                break
        except Exception as e:
            print(f"q={q!r} lic={lic} FAILED: {e}", flush=True)
        time.sleep(4)
    time.sleep(2)

with open("img_candidates_n2r2.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"saved {len(out)} n2 round-2 candidates")
for i, c in enumerate(out):
    print(f"{i}: [{c['license']}] {c['width']}x{c['height']} | {c['title']!r} | {c['creator']}")
