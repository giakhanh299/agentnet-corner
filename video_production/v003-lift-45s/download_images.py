#!/usr/bin/env python3
"""Download top Openverse candidates for V003 (first 3 per category)."""
import json, os, urllib.request

with open("img_candidates.json") as f:
    cands = json.load(f)

os.makedirs("images", exist_ok=True)
picked = {}
for key, results in cands.items():
    seen = []
    for r in results:
        if r["url"] in seen:
            continue
        seen.append(r["url"])
        if len(seen) > 3:
            break
    picked[key] = seen
    for i, url in enumerate(seen):
        ext = ".jpg"
        if url.lower().endswith(".png"):
            ext = ".png"
        fname = f"images/{key}_{i+1}{ext}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AgentNet-V003/1.0 (research)"})
            with urllib.request.urlopen(req, timeout=60) as resp, open(fname, "wb") as out:
                out.write(resp.read())
            print(f"{fname}: {os.path.getsize(fname)} bytes <- {url[:80]}", flush=True)
        except Exception as e:
            print(f"{fname}: FAILED {e} <- {url[:80]}", flush=True)

with open("images/picked.json", "w") as f:
    json.dump(picked, f, indent=2)
print("done")
