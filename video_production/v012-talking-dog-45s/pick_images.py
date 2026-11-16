#!/usr/bin/env python3
"""Download top candidates per slot for V012 and build contact sheets."""
import json, os, subprocess, urllib.request

os.makedirs("images", exist_ok=True)
with open("img_candidates.json") as f:
    cands = json.load(f)

picked = {}
for slot, results in cands.items():
    # prefer wide images >= 1200px, jpg/png
    good = [r for r in results if (r.get("width") or 0) >= 1200 and r.get("filetype") in ("jpg", "png", "jpeg")]
    pool = good[:3] if good else results[:3]
    files = []
    for i, r in enumerate(pool):
        ext = "jpg" if r.get("filetype") in ("jpg", "jpeg") else "png"
        path = f"images/{slot}_{i}.{ext}"
        if not os.path.exists(path):
            req = urllib.request.Request(r["url"], headers={"User-Agent": "AgentNet-V012/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp, open(path, "wb") as out:
                    out.write(resp.read())
                print(f"{slot}_{i}: downloaded {r.get('width')}x{r.get('height')} {r.get('license')} {r.get('creator')}")
            except Exception as e:
                print(f"{slot}_{i}: FAILED {e}")
                continue
        files.append(path)
        picked.setdefault(slot, []).append({**r, "local": path})
    if len(files) >= 2:
        sheet = f"{slot}_sheet.jpg"
        inputs = []
        for p in files:
            inputs += ["-i", p]
        filt = f"scale=360:640:force_original_aspect_ratio=decrease,pad=360:640:(ow-iw)/2:(oh-ih)/2,tile={len(files)}x1"
        subprocess.run(["ffmpeg", "-y", "-v", "error"] + inputs +
                       ["-filter_complex", filt, sheet], check=False)
        print(f"{slot}: sheet {sheet} ({len(files)} imgs)")
    elif len(files) == 1:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", files[0],
                        "-vf", "scale=360:640:force_original_aspect_ratio=decrease,pad=360:640:(ow-iw)/2:(oh-ih)/2",
                        f"{slot}_sheet.jpg"], check=False)

with open("picked.json", "w") as f:
    json.dump(picked, f, indent=2, ensure_ascii=False)
print("saved picked.json")
