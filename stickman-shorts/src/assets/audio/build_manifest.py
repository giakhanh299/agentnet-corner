#!/usr/bin/env python3
"""Build sfx_manifest.json from download_report.json + normalize_report.json
plus the framework placement table (production-framework-20261115.md § Core SFX)."""
import json

dl = json.load(open("download_report.json"))
nm = json.load(open("normalize_report.json"))

# key -> (display name, placement, formulas, note)
PLACEMENT = {
    "whoosh": ("Whoosh", "0.1s opening + every scene change", "all", "First SFX layer in the first 3s"),
    "pop": ("Pop", "When text/image/list item appears", "F1, F2, F3, F6", "Second SFX layer in the first 3s"),
    "ding": ("Ding", "When a number / important beat appears", "F2, F3, F7", "Emphasise a keyword"),
    "boom": ("Boom", "Payoff flip", "F2, F4", "Max once per video"),
    "bass_hit": ("Bass Hit", "Strong opening / reveal", "F4, F8", "Use instead of Boom when a lighter hit is needed"),
    "riser": ("Riser (drum roll)", "Before #1 / before payoff", "F3, F6", "Build tension 2-3s before the reveal"),
    "victory": ("Victory sting", "At #1 / final state", "F3, F6", "Short, 1-2s"),
    "record_scratch": ("Record Scratch", "X->Y switch / when caught", "F5, F8", "Sudden music stop = the joke"),
    "fail": ("Fail sting", "End of X vs Y / POV caught", "F5, F8", "Wah-wah style"),
    "error_buzz": ("Error buzz", "Version switch / mistake", "F5", "Short, not harsh"),
    "boing": ("Cartoon boing", "When jelly/object bounces", "F4", "B06: 'It bounces!'"),
    "door_knock": ("Door knock", "0.1s opening", "F4", "B01: the knock is the first beat"),
    "footsteps": ("Footsteps", "When hiding / running", "F8", "Trimmed to a 4s loop; loop with crossfade"),
    "laugh": ("Laugh", "After the punchline", "F3, F5", "Light — never drown the voice"),
    "crickets": ("Crickets", "After a flat joke / silence", "F5", "Only when the awkwardness is intentional"),
    "suspense_drone": ("Suspense drone", "When hiding / before reveal", "F8, F4", "Tense bed, under the voice"),
    "camera_click": ("Camera click", "When a photo / evidence appears", "F2", "Emphasis: 'this is the evidence'"),
    "transition_swoosh": ("Transition swoosh", "Between long beats", "F2, F7", "Softer and longer than Whoosh"),
    "bgm_calm": ("BGM calm / inspirational", "Background bed under the whole video", "F2, F7", "Visual Essay + stickman story"),
    "bgm_upbeat": ("BGM upbeat", "Background bed under the whole video", "F3, F6", "Countdown + transformation"),
    "bgm_suspense": ("BGM suspenseful", "Background bed under the whole video", "F4, F8", "Absurd image + POV"),
    "bgm_comedy": ("BGM light comedy", "Background bed under the whole video", "F5, F3", "X vs Y + countdown"),
}

manifest = {"version": 1, "generated": "2026-11-15",
            "license_policy": "CC0 1.0 only (public domain, commercial use allowed, no attribution required). "
                              "Sources are Freesound HQ preview files found via the Openverse API with license=cc0.",
            "format": "Ogg Vorbis q5 (~160 kbps). Chosen because the repo .gitignore blocks *.wav/*.mp3 "
                      "but not *.ogg, so the library is tracked in git. ffmpeg-decodable everywhere "
                      "assemble.py runs (pass the .ogg path to --music / mix with ffmpeg).",
            "normalization": "Integrated -20 LUFS, true peak <= -1 dBTP (loudnorm two-pass + alimiter 0.85). "
                             "3 sub-0.5s clips used peak normalization (loudnorm cannot measure them).",
            "sfx": [], "music": []}

for key, (name, placement, formulas, note) in PLACEMENT.items():
    d, n = dl[key], nm[key]
    post = n.get("post", {})
    pl = n.get("post_loudnorm") or {}
    pv = n.get("post_volume") or {}
    entry = {
        "name": name,
        "key": key,
        "file": f"{'music' if key.startswith('bgm_') else 'sfx'}/{key}.ogg",
        "source_title": d["title"],
        "creator": d["creator"],
        "source_url": d["source_url"],
        "landing_url": d["landing_url"],
        "license": "CC0 1.0",
        "license_url": d["license_url"],
        "provider": d["provider"],
        "duration_s": post.get("duration_s"),
        "sample_rate": post.get("sample_rate"),
        "channels": post.get("channels"),
        "codec": post.get("codec"),
        "bytes": post.get("bytes"),
        "integrated_lufs": pl.get("input_i"),
        "true_peak_db": pl.get("input_tp", pv.get("max")),
        "normalize_method": n.get("method"),
        "placement": placement,
        "formulas": formulas,
        "note": note,
        "status": "OK" if n.get("status") == "OK" else n.get("status"),
    }
    if key == "footsteps":
        entry["note"] += " | Trimmed 17.0s -> 4.0s (0-4s, regular steps, 0.2s fades)"
    if key == "crickets":
        entry["note"] += " | Trimmed 16.9s -> 4.0s (1-5s, continuous, 0.3s fades)"
    if key == "boom":
        entry["note"] += " | Trimmed 3.9s -> 2.5s (dead tail after 2.2s removed, 0.3s fade-out)"
    if key == "bgm_upbeat":
        entry["note"] += " | Trimmed 160s -> 90s (0-90s, 2s fades)"
    if key in ("bgm_calm", "bgm_suspense", "bgm_comedy"):
        entry["note"] += " | 2s fade in/out"
    if key == "boing":
        entry["note"] += " | Source file is quiet (max -25 dB); loudnorm applied ~+25 dB gain, some mp3 noise floor audible if soloed — masked under voice"
    (manifest["music"] if key.startswith("bgm_") else manifest["sfx"]).append(entry)

with open("sfx_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"SFX: {len(manifest['sfx'])}, music: {len(manifest['music'])}")
missing = [e for e in manifest["sfx"] + manifest["music"] if e["status"] != "OK"]
print("MISSING:", missing if missing else "none")
total = sum(e["bytes"] or 0 for e in manifest["sfx"] + manifest["music"])
print(f"total size: {total/1e6:.2f} MB")
