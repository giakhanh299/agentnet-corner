#!/usr/bin/env python3
"""Normalize downloaded Core_SFX raws to .ogg:
target integrated -20 LUFS, true peak -1 dBTP, via ffmpeg loudnorm two-pass
(linear gain) + alimiter. Very short clips (<0.5s) where loudnorm cannot
measure fall back to peak normalization to -1 dBTP.
Trims: footsteps/crickets -> 4s beds with fades; bgm_upbeat 160s -> 90s.
Writes normalize_report.json with pre/post measurements.
"""
import json, os, re, subprocess

RAW = "raw"
SFX = "sfx"
MUSIC = "music"
os.makedirs(SFX, exist_ok=True)
os.makedirs(MUSIC, exist_ok=True)

TARGET_I, TARGET_TP, TARGET_LRA = -20, -1, 11

# key -> (out_dir, trim_start_s or None, trim_dur_s or None, fade_in_s, fade_out_s)
PLAN = {
    "whoosh": (SFX, None, None, 0, 0),
    "pop": (SFX, None, None, 0, 0),
    "ding": (SFX, None, None, 0, 0),
    "boom": (SFX, 0.0, 2.5, 0, 0.3),
    "bass_hit": (SFX, None, None, 0, 0),
    "riser": (SFX, None, None, 0, 0),
    "victory": (SFX, None, None, 0, 0),
    "record_scratch": (SFX, None, None, 0, 0),
    "fail": (SFX, None, None, 0, 0),
    "error_buzz": (SFX, None, None, 0, 0),
    "boing": (SFX, None, None, 0, 0),
    "door_knock": (SFX, None, None, 0, 0),
    "footsteps": (SFX, 0.0, 4.0, 0.2, 0.2),
    "laugh": (SFX, None, None, 0, 0),
    "crickets": (SFX, 1.0, 4.0, 0.3, 0.3),
    "suspense_drone": (SFX, None, None, 0, 0),
    "camera_click": (SFX, None, None, 0, 0),
    "transition_swoosh": (SFX, None, None, 0, 0),
    "bgm_calm": (MUSIC, None, None, 2.0, 2.0),
    "bgm_upbeat": (MUSIC, 0.0, 90.0, 2.0, 2.0),
    "bgm_suspense": (MUSIC, None, None, 2.0, 2.0),
    "bgm_comedy": (MUSIC, None, None, 2.0, 2.0),
}

def run(cmd, timeout=180):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

def loudnorm_measure(path):
    """Returns dict of measured_* values, or {} if not measurable."""
    r = run(["ffmpeg", "-i", path, "-af",
             f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json",
             "-f", "null", "-"])
    m = re.search(r"\{[^}]*\"input_i\"[^}]*\}", r.stderr, re.S)
    if not m:
        return {}
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}
    try:
        vals = {k: float(d[k]) for k in
                ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")}
    except (KeyError, ValueError):
        return {}
    if vals["input_i"] in (float("inf"), float("-inf")) or vals["input_i"] < -70:
        return {}
    return vals

def volumedetect(path):
    r = run(["ffmpeg", "-i", path, "-af", "volumedetect", "-f", "null", "-"])
    vals = {}
    for line in r.stderr.splitlines():
        if "mean_volume" in line:
            vals["mean"] = float(line.split(":")[-1].strip().replace(" dB", ""))
        if "max_volume" in line:
            vals["max"] = float(line.split(":")[-1].strip().replace(" dB", ""))
    return vals

def ffprobe(path):
    r = run(["ffprobe", "-v", "error", "-show_entries",
             "format=duration,size,bit_rate",
             "-show_entries", "stream=codec_name,sample_rate,channels",
             "-of", "json", path])
    d = json.loads(r.stdout)
    fmt, st = d.get("format", {}), (d.get("streams") or [{}])[0]
    return {"duration_s": round(float(fmt.get("duration", 0)), 3),
            "bytes": int(fmt.get("size", 0)),
            "codec": st.get("codec_name"),
            "sample_rate": int(st.get("sample_rate", 0)),
            "channels": int(st.get("channels", 0))}

report = {}
for key, (outdir, t0, tdur, fade_in, fade_out) in PLAN.items():
    src = os.path.join(RAW, key + ".mp3")
    dst = os.path.join(outdir, key + ".ogg")
    entry = {"method": None, "status": "pending"}
    if not os.path.exists(src):
        entry.update(status="MISSING", reason="raw download missing")
        report[key] = entry
        print(f"MISSING {key}: raw not found")
        continue
    # Stage 1: trim (+fades) to a temp wav if needed
    stage = src
    tmp = os.path.join(RAW, key + "_trim.wav")
    if t0 is not None and tdur is not None:
        af = f"atrim=start={t0}:duration={tdur},asetpts=PTS-STARTPTS"
        if fade_in:
            af += f",afade=t=in:st=0:d={fade_in}"
        if fade_out:
            af += f",afade=t=out:st={tdur - fade_out}:d={fade_out}"
        r = run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, tmp])
        if r.returncode != 0:
            entry.update(status="FAILED", reason=f"trim failed: {r.stderr[-300:]}")
            report[key] = entry
            print(f"FAIL {key}: trim failed")
            continue
        stage = tmp
    elif fade_in or fade_out:  # music beds: fade in/out without trimming
        dur = ffprobe(src)["duration_s"]
        parts = []
        if fade_in:
            parts.append(f"afade=t=in:st=0:d={fade_in}")
        if fade_out:
            parts.append(f"afade=t=out:st={max(0, dur - fade_out)}:d={fade_out}")
        af = ",".join(parts)
        r = run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, tmp])
        if r.returncode != 0:
            entry.update(status="FAILED", reason=f"fade failed: {r.stderr[-300:]}")
            report[key] = entry
            print(f"FAIL {key}: fade failed")
            continue
        stage = tmp
    # Stage 2: loudnorm two-pass
    meas = loudnorm_measure(stage)
    if meas:
        af = (f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:"
              f"measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
              f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:"
              f"offset={meas['target_offset']}:linear=true,"
              f"alimiter=limit=0.85:level=false,aresample=48000")
        method = "loudnorm_two_pass"
    else:
        vol = volumedetect(stage)
        if "max" not in vol:
            entry.update(status="FAILED", reason="no volume measurable")
            report[key] = entry
            print(f"FAIL {key}: no volume")
            continue
        gain = TARGET_TP - vol["max"]  # bring peak to -1 dBTP
        af = f"volume={gain:.2f}dB,alimiter=limit=0.85:level=false,aresample=48000"
        method = "peak_fallback"
        meas = {"input_max_db": vol["max"], "gain_db": round(gain, 2)}
    r = run(["ffmpeg", "-y", "-v", "error", "-i", stage, "-af", af,
             "-c:a", "libvorbis", "-q:a", "5", dst])
    if r.returncode != 0:
        entry.update(status="FAILED", reason=f"encode failed: {r.stderr[-300:]}")
        report[key] = entry
        print(f"FAIL {key}: encode failed")
        continue
    post = ffprobe(dst)
    post_meas = loudnorm_measure(dst)
    post_vol = volumedetect(dst)
    entry.update(status="OK", method=method, pre_measure=meas,
                 post=post, post_loudnorm=post_meas, post_volume=post_vol)
    print(f"OK  {key:18s} {method:18s} {post['duration_s']:6.2f}s "
          f"{post['bytes']:7d}B I={post_meas.get('input_i', '?')} "
          f"TP={post_meas.get('input_tp', '?')}")
    report[key] = entry

with open("normalize_report.json", "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
ok = sum(1 for e in report.values() if e.get("status") == "OK")
print(f"\n{ok}/{len(report)} normalized OK")
