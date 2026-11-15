#!/usr/bin/env python3
"""Search Openverse (CC0 only) for the 18 Core SFX + 4 music beds.
Writes candidates to sfx_candidates.json. Anonymous rate limit ~20 req/min,
so sleep 4s between calls. No API key needed.
"""
import json, time, urllib.request, urllib.parse

BASE = "https://api.openverse.org/v1/audio/"

QUERIES = {
    # sfx
    "whoosh": ["whoosh"],
    "pop": ["pop sound effect"],
    "ding": ["ding"],
    "boom": ["boom deep impact"],
    "bass_hit": ["bass hit"],
    "riser": ["riser drum roll"],
    "victory": ["victory fanfare"],
    "record_scratch": ["record scratch"],
    "fail": ["sad trombone fail"],
    "error_buzz": ["error buzzer"],
    "boing": ["boing cartoon"],
    "door_knock": ["door knock"],
    "footsteps": ["footsteps"],
    "laugh": ["laugh laughter"],
    "crickets": ["crickets night"],
    "suspense_drone": ["suspense drone"],
    "camera_click": ["camera shutter"],
    "transition_swoosh": ["swoosh transition"],
    # music
    "music_calm": ["calm inspirational background music"],
    "music_upbeat": ["upbeat background music"],
    "music_suspense": ["suspenseful background music"],
    "music_comedy": ["playful comedy background music"],
}

def search(q):
    params = urllib.parse.urlencode({
        "q": q, "license": "cc0", "license_type": "commercial",
        "page_size": 8,
    })
    req = urllib.request.Request(BASE + "?" + params,
                                 headers={"User-Agent": "AgentNet-CoreSFX/1.0 (research; contact: local)"})
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
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "license": r.get("license"),
                    "license_url": r.get("license_url"),
                    "creator": r.get("creator"),
                    "foreign_landing_url": r.get("foreign_landing_url"),
                    "filesize": r.get("filesize"),
                    "filetype": r.get("filetype"),
                    "duration": r.get("duration"),
                    "bit_rate": r.get("bit_rate"),
                    "sample_rate": r.get("sample_rate"),
                    "provider": r.get("provider"),
                })
            print(f"{key}: q={q!r} -> {len(data.get('results', []))} results")
        except Exception as e:
            print(f"{key}: q={q!r} FAILED: {e}")
        time.sleep(4)
    out[key] = results

with open("sfx_candidates.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved sfx_candidates.json")
for k, v in out.items():
    print(f"{k}: {len(v)} candidates")
