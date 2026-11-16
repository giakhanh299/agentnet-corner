#!/usr/bin/env python3
"""Search Openverse for V006 images (CC0 first, CC BY as fallback)."""
import json, time, urllib.request, urllib.parse

BASE = "https://api.openverse.org/v1/images/"
QUERIES = {
    "hook_boiling_ice": ["boiling water ice glass", "water boiling pot ice", "ice cubes boiling water"],
    "beat1_pressure": ["pressure gauge", "barometer pressure", "steam pressure gauge"],
    "beat2_mountain": ["cooking mountain altitude", "mountain lake hiker", "mountain cooking stove"],
    "beat3_lab": ["laboratory glass flask", "vacuum chamber experiment", "science laboratory beaker"],
    "payoff_water": ["water drop macro", "ice water glass", "water splash blue"],
}

def search(q, lic):
    params = urllib.parse.urlencode({
        "q": q, "license": lic, "license_type": "commercial", "page_size": 8,
    })
    req = urllib.request.Request(BASE + "?" + params,
                                 headers={"User-Agent": "AgentNet-V006/1.0 (research; contact: local)"})
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
        time.sleep(4)
    out[key] = results

with open("img_candidates.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved img_candidates.json")
for k, v in out.items():
    print(f"{k}: {len(v)} candidates")
