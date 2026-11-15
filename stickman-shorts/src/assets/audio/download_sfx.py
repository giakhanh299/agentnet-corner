#!/usr/bin/env python3
"""Download the 22 selected Core_SFX files (all CC0 via Openverse/Freesound).
Verifies each with ffprobe + volumedetect (not silent). Writes download_report.json.
Sources: Openverse API (license=cc0 filter); files are Freesound HQ previews.
"""
import json, os, subprocess, sys, urllib.request

RAW = "raw"
os.makedirs(RAW, exist_ok=True)

# (key, title, creator, url, landing_url, license, license_url, note)
PICKS = [
 ("whoosh", "Swipe Whoosh", "qubodup",
  "https://cdn.freesound.org/previews/60/60007_71257-hq.mp3",
  "https://freesound.org/people/qubodup/sounds/60007"),
 ("pop", "[Media] game sound sfx (short, generic, menu)", "waveplaySFX",
  "https://cdn.freesound.org/previews/246/246420_1676145-hq.mp3",
  "https://freesound.org/people/waveplaySFX/sounds/246420"),
 ("ding", "Ding 1", "greenvwbeetle",
  "https://cdn.freesound.org/previews/241/241288_3624044-hq.mp3",
  "https://freesound.org/people/greenvwbeetle/sounds/241288"),
 ("boom", "Bass Impact - Ki_01.mp3", "Kievinay",
  "https://cdn.freesound.org/previews/512/512389_3997858-hq.mp3",
  "https://freesound.org/people/Kievinay/sounds/512389"),
 ("bass_hit", "super low bass hit kick drum wAv", "phluidbox",
  "https://cdn.freesound.org/previews/339/339437_2908654-hq.mp3",
  "https://freesound.org/people/phluidbox/sounds/339437"),
 ("riser", "13 drum roll 01.wav", "zuluonedrop",
  "https://cdn.freesound.org/previews/255/255051_3028938-hq.mp3",
  "https://freesound.org/people/zuluonedrop/sounds/255051"),
 ("victory", "game-win.mp3", "mickleness",
  "https://cdn.freesound.org/previews/269/269198_4409114-hq.mp3",
  "https://freesound.org/people/mickleness/sounds/269198"),
 ("record_scratch", "Record Scratch #4", "musicvision31",
  "https://cdn.freesound.org/previews/431/431777_817038-hq.mp3",
  "https://freesound.org/people/musicvision31/sounds/431777"),
 ("fail", "wah wah sad trombone.wav", "kirbydx",
  "https://cdn.freesound.org/previews/175/175409_1326576-hq.mp3",
  "https://freesound.org/people/kirbydx/sounds/175409"),
 ("error_buzz", "buzzer.mp3", "Loyalty_Freak_Music",
  "https://cdn.freesound.org/previews/407/407466_7947620-hq.mp3",
  "https://freesound.org/people/Loyalty_Freak_Music/sounds/407466"),
 ("boing", "Cartoon Boing.wav", "reelworldstudio",
  "https://cdn.freesound.org/previews/161/161122_2750714-hq.mp3",
  "https://freesound.org/people/reelworldstudio/sounds/161122"),
 ("door_knock", "Door Knock - with urgency.wav", "FreqMan",
  "https://cdn.freesound.org/previews/144/144510_92661-hq.mp3",
  "https://freesound.org/people/FreqMan/sounds/144510"),
 ("footsteps", "footstep on wood foley.wav", "martian",
  "https://cdn.freesound.org/previews/19/19292_84709-hq.mp3",
  "https://freesound.org/people/martian/sounds/19292"),
 ("laugh", "Crowd laugh.wav", "deleted_user_2104797",
  "https://cdn.freesound.org/previews/324/324894_2104797-hq.mp3",
  "https://freesound.org/people/deleted_user_2104797/sounds/324894"),
 ("crickets", "crickets night short nice some skyline Montreal, Canada.flac", "kyles",
  "https://cdn.freesound.org/previews/455/455685_612689-hq.mp3",
  "https://freesound.org/people/kyles/sounds/455685"),
 ("suspense_drone", "Drone of suspense.wav", "reacthor",
  "https://cdn.freesound.org/previews/130/130982_2092908-hq.mp3",
  "https://freesound.org/people/reacthor/sounds/130982"),
 ("camera_click", "Camera Shutter", "roachpowder",
  "https://cdn.freesound.org/previews/170/170229_3133582-hq.mp3",
  "https://freesound.org/people/roachpowder/sounds/170229"),
 ("transition_swoosh", "Transition Swoosh", "adh.dreaming",
  "https://cdn.freesound.org/previews/632/632763_12672694-hq.mp3",
  "https://freesound.org/people/adh.dreaming/sounds/632763"),
 ("bgm_calm", "ps Calm Aurorae.flac", "arseniiv",
  "https://cdn.freesound.org/previews/402/402338_1951924-hq.mp3",
  "https://freesound.org/people/arseniiv/sounds/402338"),
 ("bgm_upbeat", "Free Uplifting Music", "Seth_Makes_Sounds",
  "https://cdn.freesound.org/previews/670/670819_13228046-hq.mp3",
  "https://freesound.org/people/Seth_Makes_Sounds/sounds/670819"),
 ("bgm_suspense", "Atmospheric horror music #1", "Magmi.Soundtracks",
  "https://cdn.freesound.org/previews/417/417780_6900479-hq.mp3",
  "https://freesound.org/people/Magmi.Soundtracks/sounds/417780"),
 ("bgm_comedy", "Country Bumpkin", "Beetlemuse",
  "https://cdn.freesound.org/previews/532/532351_10334845-hq.mp3",
  "https://freesound.org/people/Beetlemuse/sounds/532351"),
]

def ffprobe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size,bit_rate",
         "-show_entries", "stream=codec_name,sample_rate,channels",
         "-of", "json", path],
        capture_output=True, text=True, timeout=60)
    return json.loads(out.stdout)

def volumedetect(path):
    out = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, timeout=60)
    vals = {}
    for line in out.stderr.splitlines():
        if "mean_volume" in line:
            vals["mean_volume"] = float(line.split(":")[-1].strip().replace(" dB", ""))
        if "max_volume" in line:
            vals["max_volume"] = float(line.split(":")[-1].strip().replace(" dB", ""))
    return vals

report = {}
for key, title, creator, url, landing in PICKS:
    dest = os.path.join(RAW, key + ".mp3")
    entry = {"title": title, "creator": creator, "source_url": url,
             "landing_url": landing, "license": "CC0 1.0",
             "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
             "provider": "Freesound via Openverse (license=cc0)"}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgentNet-CoreSFX/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            f.write(r.read())
        probe = ffprobe(dest)
        fmt = probe.get("format", {})
        stream = (probe.get("streams") or [{}])[0]
        vol = volumedetect(dest)
        entry.update({
            "status": "downloaded",
            "bytes": os.path.getsize(dest),
            "duration_s": round(float(fmt.get("duration", 0)), 3),
            "codec": stream.get("codec_name"),
            "sample_rate": int(stream.get("sample_rate", 0)),
            "channels": int(stream.get("channels", 0)),
            "mean_volume_db": vol.get("mean_volume"),
            "max_volume_db": vol.get("max_volume"),
            "silent": vol.get("mean_volume") is not None and vol["mean_volume"] < -60,
        })
        print(f"OK  {key:18s} {entry['duration_s']:7.2f}s {entry['bytes']:8d}B "
              f"mean={vol.get('mean_volume')}dB max={vol.get('max_volume')}dB")
    except Exception as e:
        entry.update({"status": "FAILED", "error": str(e)})
        print(f"FAIL {key}: {e}")
    report[key] = entry

with open("download_report.json", "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
ok = sum(1 for e in report.values() if e["status"] == "downloaded")
print(f"\n{ok}/{len(report)} downloaded")
