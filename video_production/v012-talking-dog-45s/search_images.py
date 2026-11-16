#!/usr/bin/env python3
"""Search Openverse for V012 dog images (CC0 first, CC BY as fallback)."""
import json, time, urllib.request, urllib.parse

BASE = "https://api.openverse.org/v1/images/"
QUERIES = {
    "hook_smile": ["dog smiling", "happy dog portrait", "dog smile close up"],
    "b1_door": ["dog waiting at door", "dog sitting front door", "dog waiting door"],
    "b2a_morning": ["dog lying down floor", "dog sleeping floor", "dog lying carpet"],
    "b2b_noon": ["dog looking out window", "dog window waiting", "dog looking window"],
    "b2c_evening": ["dog owner phone", "dog looking at camera", "dog staring camera"],
    "b3_run": ["dog running towards camera", "happy dog running", "dog jumping joy"],
}

def search(q, lic):
    params = urllib.parse.urlencode({
        "q": q, "license": lic, "license_type": "commercial", "page_size": 8,
    })
    req = urllib.request.Request(BASE + "?" + params,
                                 headers={"User-Agent": "AgentNet-V012/1.0 (research; contact: local)"})
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
