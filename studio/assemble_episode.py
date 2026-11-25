"""Xào nấu ghép tập phim từ clip Muse gửi về + giọng + nhạc + SFX + phụ đề.

Đầu vào: file episode JSON (mỗi kênh tự viết trong channels/<kênh>/), ví dụ:
{
  "title": "Ma Da Kéo Giò", "seed": 1, "voice": "phonui", "aigc_label": true,
  "music": {"generator": "horror", "gain_db": 0},
  "scenes": [
    {"id": 1, "duration_s": 15, "clip": "scene_01.mp4",          # file trong --clips-dir, URL share, hoặc ảnh .png/.jpg
     "voiceover": "Đêm đó, nước sông Hậu rút cạn…", "vo_at": 0.8, "ghost": false,
     "sfx": [{"tag": "rain", "at": 0, "dur": 15, "gain_db": -24}, "tiếng ếch kêu xa"]}
  ]
}
Xử lý:
 1. Lấy clip từng cảnh (tải link share nếu cần) → cắt/lặp đúng thời lượng → 1080x1920 30fps, BỎ TIẾNG GỐC.
    Ảnh tĩnh → Ken Burns (zoompan) để không đứng hình.
 2. Ghép các cảnh theo thứ tự id.
 3. Giọng (mặc định Góc Nhỏ Phố Núi) đọc lời từng cảnh; câu "ghost": true → giọng ma.
 4. Nhạc nền tự sáng tác (studio/horror_music.py, seed theo tập), tự nhỏ lại khi có lời.
 5. SFX lấy từ assets/sfx/manifest.json (Muse tìm về), thiếu thì dùng kho SFX có sẵn của stickman-shorts.
 6. Phụ đề .ass + nhãn AIGC, chuẩn âm -15 LUFS, xuất H.264 (GPU NVENC nếu có).

python studio/assemble_episode.py --spec channels/phim-ma-dan-gian/ep01_ma_da/episode.json \
       --clips-dir D:/clips/ep01 --out D:/render/ep01.mp4
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import horror_music  # noqa: E402
import voice as voice_mod  # noqa: E402

W, H, FPS = 1080, 1920, 30
SFX_LIB = REPO / "assets" / "sfx"
FALLBACK_SFX_DIR = REPO / "stickman-shorts" / "src" / "assets" / "audio" / "sfx"
FONT_DIR = REPO / "stickman-shorts" / "src" / "assets" / "fonts"
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}

KEYWORD_CATEGORY = [
    (("buoc", "chay", "footstep"), "footsteps"),
    (("mua", "rain", "giot nuoc", "sam"), "rain"),
    (("la ", "la roi", "xao xac", "gio", "luy tre", "leaves", "wind"), "leaves_wind"),
    (("tre keo", "keo ket", "cua go", "vong", "van go", "creak"), "wood_creak"),
    (("nuoc", "song", "cheo", "tom", "bong bong", "water"), "water"),
    (("ech", "de ", "ve sau", "cu keu", "cho", "qua", "ga gay", "con trung"), "night_creatures"),
    (("den dau", "lua", "diem", "nen", "fire"), "fire_lamp"),
    (("thi tham", "cuoi", "tho", "nuc no", "whisper"), "human_eerie"),
    (("drone", "impact", "riser", "whoosh", "trong com", "dan bau", "dan nhi", "stinger", "im lang"), "horror_stinger"),
    (("chuong", "mo ", "chieng", "cong", "go cua", "lon"), "folk_oneshot"),
]
FALLBACK_BY_CATEGORY = {
    "footsteps": "footsteps.ogg",
    "night_creatures": "crickets.ogg",
    "horror_stinger": "suspense_drone.ogg",
    "folk_oneshot": "door_knock.ogg",
    "leaves_wind": "whoosh.ogg",
    "wood_creak": "door_knock.ogg",
}


def fold(text: str) -> str:
    s = unicodedata.normalize("NFKD", (text or "").replace("đ", "d").replace("Đ", "D"))
    return " " + "".join(c for c in s if not unicodedata.combining(c)).lower() + " "


def run(cmd: list[str], cwd: Path | None = None) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode:
        raise RuntimeError(f"Lệnh lỗi: {' '.join(cmd[:6])}…\n{proc.stderr[-1500:]}")


def has_nvenc() -> bool:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)
    return "h264_nvenc" in out.stdout


# ---------- SFX ----------

def category_for(text: str) -> str | None:
    f = fold(text)
    for keys, cat in KEYWORD_CATEGORY:
        if any(k in f for k in keys):
            return cat
    return None


def resolve_sfx(item, manifest: dict) -> Path | None:
    """item: dict {"tag": "rain"} hoặc chuỗi mô tả tiếng Việt. Trả về file âm thanh tốt nhất."""
    tag = item.get("tag") if isinstance(item, dict) else None
    desc = item.get("desc", "") if isinstance(item, dict) else str(item)
    cat = tag if tag else category_for(desc)
    if not cat:
        return None
    words = set(re.findall(r"[a-z0-9]+", fold(desc)))
    best, best_key = None, (-1.0, -1.0)
    for entry in manifest.get("sounds", {}).values():
        if entry.get("category") != cat:
            continue
        p = SFX_LIB / entry["file"]
        if not p.is_file():
            continue
        tag_words = set(re.findall(r"[a-z0-9]+", fold(" ".join(entry.get("tags", [])) + " " + entry.get("name", ""))))
        key = (len(words & tag_words), float(entry.get("score") or 0))
        if key > best_key:
            best, best_key = p, key
    if best:
        return best
    fb = FALLBACK_BY_CATEGORY.get(cat)
    return FALLBACK_SFX_DIR / fb if fb and (FALLBACK_SFX_DIR / fb).is_file() else None


def load_sfx_manifest() -> dict:
    mf = SFX_LIB / "manifest.json"
    return json.loads(mf.read_text(encoding="utf-8")) if mf.is_file() else {"sounds": {}}


# ---------- Clip ----------

def fetch_clip(ref: str, clips_dir: Path | None, work: Path, scene_id: int) -> Path | None:
    if not ref:
        if clips_dir:
            for p in sorted(clips_dir.glob(f"scene_{scene_id:02d}.*")):
                return p
        return None
    parts = urlsplit(ref)
    if parts.scheme in ("http", "https"):
        from urllib.request import Request, urlopen
        ext = Path(parts.path).suffix.lower() or ".mp4"
        dst = work / "downloads" / f"scene_{scene_id:02d}{ext}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.is_file():
            with urlopen(Request(ref, headers={"User-Agent": "AgentNet-Assembler/1.0"}), timeout=120) as r:
                dst.write_bytes(r.read())
        return dst
    p = Path(ref)
    if not p.is_absolute() and clips_dir:
        p = clips_dir / ref
    return p if p.is_file() else None


def render_scene(src: Path | None, dur: float, dst: Path) -> str:
    vf_fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p"
    common = ["-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)]
    if src is None:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x05070a:s={W}x{H}:r={FPS}:d={dur}"] + common)
        return "THIẾU_CLIP→nền đen"
    ext = src.suffix.lower()
    if ext in IMAGE_EXT:
        frames = int(dur * FPS)
        vf = (f"scale={int(W*1.15)}:{int(H*1.15)}:force_original_aspect_ratio=increase,crop={int(W*1.15)}:{int(H*1.15)},"
              f"zoompan=z='min(zoom+0.0007,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
              "format=yuv420p")
        run(["ffmpeg", "-y", "-loop", "1", "-i", str(src), "-t", f"{dur}", "-vf", vf] + common)
        return "ẢNH→Ken Burns"
    run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src), "-t", f"{dur}", "-vf", vf_fit] + common)
    return "CLIP (đã tắt tiếng gốc)"


# ---------- Phụ đề ----------

def wrap_caption(text: str, width: int = 26) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return r"\N".join(lines[:3])


def ass_time(t: float) -> str:
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def write_ass(cues: list[tuple[float, float, str]], path: Path) -> None:
    head = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Be Vietnam Pro,62,&H00F2F2F2,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,2,2,70,70,360,1\n"
        "Style: Ghost,Be Vietnam Pro,62,&H00B8E0FF,&H000000FF,&H00200000,&H64000000,-1,1,0,0,100,100,1,0,1,4,2,2,70,70,360,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    rows = []
    for start, end, text, *style in cues:
        st = style[0] if style else "Default"
        rows.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},{st},,0,0,0,,{wrap_caption(text)}")
    path.write_text(head + "\n".join(rows) + "\n", encoding="utf-8")


# ---------- Ghép ----------

def assemble(spec: dict, clips_dir: Path | None, out: Path, work: Path, voice_override: str | None = None) -> dict:
    work.mkdir(parents=True, exist_ok=True)
    scenes = sorted(spec["scenes"], key=lambda s: s["id"])
    report = {"title": spec.get("title"), "scenes": [], "warnings": []}

    # 1-2. Hình
    seg_list = work / "segments.txt"
    t_cursor = 0.0
    starts = []
    with seg_list.open("w", encoding="utf-8") as f:
        for sc in scenes:
            dur = float(sc["duration_s"])
            src = fetch_clip(sc.get("clip", ""), clips_dir, work, sc["id"])
            seg = work / f"seg_{sc['id']:02d}.mp4"
            how = render_scene(src, dur, seg)
            if how.startswith("THIẾU"):
                report["warnings"].append(f"Cảnh {sc['id']}: thiếu clip, dùng nền đen")
            f.write(f"file '{seg.name}'\n")
            starts.append(t_cursor)
            report["scenes"].append({"id": sc["id"], "start": round(t_cursor, 2), "dur": dur, "video": how})
            t_cursor += dur
    total = t_cursor
    video_silent = work / "video_silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", seg_list.name, "-c", "copy", video_silent.name], cwd=work)

    # 3. Giọng
    vo_items = [(i, sc) for i, sc in enumerate(scenes) if (sc.get("voiceover") or "").strip()]
    voice_name = voice_override or spec.get("voice", "phonui")
    wavs = voice_mod.synth([sc["voiceover"].strip() for _, sc in vo_items], work / "voice", voice=voice_name) if vo_items else []
    vo_tracks, cues = [], []
    for (idx, sc), wav in zip(vo_items, wavs):
        if sc.get("ghost"):
            wav = voice_mod.ghost_fx(wav, work / "voice" / f"ghost_{sc['id']:02d}.wav", float(sc.get("ghost_semitones", -3)))
        at = starts[idx] + float(sc.get("vo_at", 0.6))
        d = voice_mod.duration(wav)
        if at + d > starts[idx] + float(sc["duration_s"]) + 0.05:
            report["warnings"].append(f"Cảnh {sc['id']}: lời dài {d:.1f}s vượt thời lượng cảnh")
        vo_tracks.append((wav, at))
        cues.append((at, at + d, sc.get("caption") or sc["voiceover"], "Ghost" if sc.get("ghost") else "Default"))

    # 4. Nhạc
    music_wav = work / "music.wav"
    horror_music.write_wav(music_wav, horror_music.compose(total, int(spec.get("seed", 1))))

    # 5. SFX
    manifest = load_sfx_manifest()
    sfx_tracks = []
    for idx, sc in enumerate(scenes):
        for item in sc.get("sfx", []):
            p = resolve_sfx(item, manifest)
            label = item if isinstance(item, str) else item.get("tag") or item.get("desc")
            if not p:
                report["warnings"].append(f"Cảnh {sc['id']}: chưa có SFX cho '{label}'")
                continue
            it = item if isinstance(item, dict) else {}
            at = starts[idx] + float(it.get("at", 0))
            dur = float(it.get("dur", sc["duration_s"] - float(it.get("at", 0))))
            gain = float(it.get("gain_db", -22))
            sfx_tracks.append((p, at, dur, gain))
            report["scenes"][idx].setdefault("sfx", []).append(f"{label}→{p.name}")

    # 6. Trộn âm
    inputs, chains = [], []
    n = 0
    vo_labels = []
    for wav, at in vo_tracks:
        inputs += ["-i", str(wav)]
        ms = int(at * 1000)
        chains.append(f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=80,adelay={ms}|{ms}[v{n}]")
        vo_labels.append(f"[v{n}]")
        n += 1
    inputs += ["-i", str(music_wav)]
    mus_idx = n
    n += 1
    fx_labels = []
    for p, at, dur, gain in sfx_tracks:
        inputs += ["-stream_loop", "-1", "-i", str(p)]
        ms = int(at * 1000)
        fo = max(0.0, dur - 0.6)
        chains.append(f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{dur:.2f},asetpts=PTS-STARTPTS,"
                      f"volume={gain}dB,afade=t=in:d=0.3,afade=t=out:st={fo:.2f}:d=0.6,adelay={ms}|{ms}[f{n}]")
        fx_labels.append(f"[f{n}]")
        n += 1
    music_gain = float((spec.get("music") or {}).get("gain_db", 0))
    chains.append(f"[{mus_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={music_gain - 6}dB[mus]")
    if vo_labels:
        chains.append(f"{''.join(vo_labels)}amix=inputs={len(vo_labels)}:normalize=0:duration=longest,apad=whole_dur={total}[vo]")
        chains.append("[vo]asplit=2[vo1][key]")
        chains.append("[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=150:release=600[duck]")
        bus = ["[vo1]", "[duck]"]
    else:
        bus = ["[mus]"]
    if fx_labels:
        chains.append(f"{''.join(fx_labels)}amix=inputs={len(fx_labels)}:normalize=0:duration=longest[fx]")
        bus.append("[fx]")
    chains.append(f"{''.join(bus)}amix=inputs={len(bus)}:normalize=0:duration=first,atrim=0:{total},"
                  "loudnorm=I=-15:TP=-1.5:LRA=11[out]")
    mix_wav = work / "mix.wav"
    run(["ffmpeg", "-y", "-hide_banner"] + inputs + ["-filter_complex", ";".join(chains), "-map", "[out]",
                                                    "-ar", "48000", "-t", f"{total}", str(mix_wav)])

    # 7. Phụ đề + AIGC + xuất
    write_ass(cues, work / "subs.ass")
    fonts = work / "fonts"
    if not fonts.is_dir():
        shutil.copytree(FONT_DIR, fonts)
    vf = "ass=subs.ass:fontsdir=fonts"
    if spec.get("aigc_label", True):
        vf += (",drawtext=fontfile=fonts/BeVietnamPro-Bold.ttf:text='AIGC · Nội dung tạo bởi AI':"
               "fontsize=30:fontcolor=white@0.75:x=w-tw-40:y=h-th-60:box=1:boxcolor=black@0.35:boxborderw=10")
    vcodec = ["-c:v", "h264_nvenc", "-preset", "p5", "-cq", "21"] if has_nvenc() else ["-c:v", "libx264", "-crf", "19"]
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-i", video_silent.name, "-i", mix_wav.name, "-vf", vf] + vcodec +
        ["-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out.resolve())],
        cwd=work)
    report.update({"output": str(out), "duration_s": round(total, 2), "voice": voice_name,
                   "voice_lines": len(vo_tracks), "sfx_used": len(sfx_tracks)})
    (work / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Ghép tập phim từ clip Muse + giọng + nhạc + SFX")
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--clips-dir", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--work", type=Path)
    ap.add_argument("--voice", choices=sorted(voice_mod.VOICES), help="ghi đè giọng trong spec")
    a = ap.parse_args()
    spec = json.loads(a.spec.read_text(encoding="utf-8"))
    work = a.work or a.out.with_suffix("").parent / (a.out.stem + "_work")
    rep = assemble(spec, a.clips_dir, a.out, work, a.voice)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
