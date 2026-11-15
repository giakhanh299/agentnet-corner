#!/usr/bin/env python3
"""Fallback Openverse CC0 searches for the 3 items with 0 candidates."""
import json, time, urllib.request, urllib.parse

BASE = "https://api.openverse.org/v1/audio/"
QUERIES = {
    "riser": ["drum roll", "riser", "build up crescendo"],
    "music_calm": ["calm piano", "relaxing piano music", "peaceful ambient music"],
    "music_comedy": ["playful background music", "whimsical music", "funny background music"],
}

def search(q):
    params = urllib.parse.urlencode({
        "q": q, "license": "cc0", "license_type": "commercial", "page_size": 8,
    })
    req = urllib.request.Request(BASE + "?" + params,
                                 headers={"User-Agent": "AgentNet-CoreSFX/1.0 (research)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

out = {}
for key, qs in QUERIES.items():
    results = []
    for q in qs:
        try:
            data = search(q)
            for r in data.get("results", []):
                results.append({
                    "title": r.get("title"), "url": r.get("url"),
                    "license": r.get("license"), "license_url": r.get("license_url"),
                    "creator": r.get("creator"),
                    "foreign_landing_url": r.get("foreign_landing_url"),
                    "filesize": r.get("filesize"), "filetype": r.get("filetype"),
                    "duration": r.get("duration"), "provider": r.get("provider"),
                })
            print(f"{key}: q={q!r} -> {len(data.get('results', []))} results")
        except Exception as e:
            print(f"{key}: q={q!r} FAILED: {e}")
        time.sleep(4)
    out[key] = results

with open("sfx_candidates_fallback.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved sfx_candidates_fallback.json")
for k, v in out.items():
    print(f"{k}: {len(v)} candidates")
