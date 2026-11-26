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
import curiosity_music  # noqa: E402
import horror_music  # noqa: E402
import thumbnail as thumb_mod  # noqa: E402
import voice as voice_mod  # noqa: E402
import wuxia_music  # noqa: E402

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


SFX_SYNONYMS = {
    "thi tham": ("whisper", "whispering"),
    "cuoi": ("laugh",),
    "khoc": ("cry", "crying", "weep"),
    "tho": ("breath", "breathing"),
    "bong bong": ("bubble", "bubbles"),
    "song": ("river", "water", "splash", "wave"),
    "cheo": ("oar", "paddle", "rowing"),
    "tom": ("splash", "rock"),
    "cua": ("door", "creak"),
    "vong": ("bed", "creak"),
    "van": ("wood", "creak"),
    "cau": ("wood", "creak"),
    "buoc": ("footstep", "footsteps", "leaves"),
    "la": ("leaves", "rustling", "twig"),
    "gio": ("wind", "leaves"),
    "mua": ("rain", "forest", "light"),
    "sam": ("thunder", "storm"),
    "drone": ("drone",),
    "riser": ("sweep", "terror", "trailer"),
    "impact": ("impact", "hit", "drum"),
    "tim": ("heartbeat", "drum"),
}


def resolve_sfx(item, manifest: dict) -> Path | None:
    """item: dict {"tag": "rain"} hoặc chuỗi mô tả tiếng Việt. Trả về file âm thanh tốt nhất."""
    tag = item.get("tag") if isinstance(item, dict) else None
    desc = item.get("desc", "") if isinstance(item, dict) else str(item)
    cat = tag if tag else category_for(desc)
    if not cat:
        return None
    fdesc = fold(desc)
    words = set(re.findall(r"[a-z0-9]+", fdesc))
    for vi_key, en_words in SFX_SYNONYMS.items():
        if vi_key in fdesc:
            words.update(en_words)
    best, best_key = None, (-1.0, -1.0)
    for entry in manifest.get("sounds", {}).values():
        if entry.get("category") != cat:
            continue
        p = SFX_LIB / entry["file"]
        if not p.is_file():
            continue
        tag_words = set(re.findall(r"[a-z0-9]+", fold(" ".join(entry.get("tags", [])) + " " + entry.get("name", "") + " " + entry["file"])))
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


def _pick_motion(motion_text: str, idx: int) -> str:
    m = fold(motion_text)
    if any(k in m for k in ("zoom ra", "lui may", "pull out", "mo rong")):
        return "zoom_out"
    if any(k in m for k in ("nghieng xuong", "tilt down", "tu mat", "xuong doi tay")):
        return "tilt_down"
    if any(k in m for k in ("sang trai", "pan left", "troi ngang")):
        return "pan_left"
    if any(k in m for k in ("sang phai", "pan right", "lia ngang")):
        return "pan_right"
    if any(k in m for k in ("day cham", "zoom vao", "push in", "can canh")):
        return "zoom_in"
    return ("zoom_in", "tilt_down", "zoom_out", "pan_right", "pan_left")[idx % 5]


def render_scene(src: Path | None, dur: float, dst: Path, motion: str = "", idx: int = 0) -> str:
    vf_fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p"
    common = ["-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)]
    if src is None:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x05070a:s={W}x{H}:r={FPS}:d={dur}"] + common)
        return "THIẾU_CLIP→nền đen"
    ext = src.suffix.lower()
    if ext in IMAGE_EXT:
        frames = max(1, int(round(dur * FPS)))
        mode = _pick_motion(motion, idx)
        sw, sh = int(W * 1.18), int(H * 1.18)
        t = f"(on/{frames})"
        if mode == "zoom_out":
            zp = f"zoompan=z='1.12-0.10*{t}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}"
        elif mode == "pan_left":
            zp = f"zoompan=z='1.10':x='(iw-iw/zoom)*(1-{t})':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}"
        elif mode == "pan_right":
            zp = f"zoompan=z='1.10':x='(iw-iw/zoom)*{t}':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}"
        elif mode == "tilt_down":
            zp = f"zoompan=z='1.10':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*{t}':d={frames}:s={W}x{H}:fps={FPS}"
        else:
            zp = f"zoompan=z='1.00+0.10*{t}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}"
        vf = (f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={sw}:{sh},"
              f"{zp},vignette=PI/6,format=yuv420p")
        run(["ffmpeg", "-y", "-loop", "1", "-i", str(src), "-t", f"{dur}", "-vf", vf] + common)
        return f"ẢNH→{mode}"
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


def split_caption_chunks(text: str, start: float, end: float, max_words: int = 12) -> list[tuple[float, float, str]]:
    """Tách câu dài thành từng cụm phụ đề 1-2 dòng theo tỷ lệ số từ để không bị cắt mất chữ."""
    words = text.split()
    if len(words) <= max_words:
        return [(start, end, text)]
    parts = [p.strip() for p in re.split(r"(?<=[.!?…])\s+", text.strip()) if p.strip()]
    chunks: list[str] = []
    for p in parts:
        pw = p.split()
        if len(pw) <= max_words:
            chunks.append(p)
        else:
            for i in range(0, len(pw), max_words):
                chunks.append(" ".join(pw[i:i + max_words]))
    total_w = max(1, sum(len(c.split()) for c in chunks))
    dur = max(0.2, end - start)
    cur = start
    out = []
    for c in chunks:
        seg = dur * (len(c.split()) / total_w)
        out.append((cur, cur + seg, c))
        cur += seg
    return out


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
        for cs, ce, ct in split_caption_chunks(text, start, end):
            rows.append(f"Dialogue: 0,{ass_time(cs)},{ass_time(ce)},{st},,0,0,0,,{wrap_caption(ct)}")
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
        for i, sc in enumerate(scenes):
            dur = float(sc["duration_s"])
            src = fetch_clip(sc.get("clip", ""), clips_dir, work, sc["id"])
            seg = work / f"seg_{sc['id']:02d}.mp4"
            how = render_scene(src, dur, seg, motion=str(sc.get("motion") or ""), idx=i)
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
    cover_intro_s = float(spec.get("cover_intro_s", 0.85))
    vo_items = [(i, sc) for i, sc in enumerate(scenes) if (sc.get("voiceover") or "").strip()]
    cid = str(spec.get("target_channel") or "").upper().strip()
    default_voice = (
        "tienvadoi" if cid == "KENH_001"
        else "taplamcontent" if cid == "KENH_008"
        else "phimma"
    )
    raw_spec_voice = str(spec.get("voice") or "").strip().lower()
    if voice_override:
        voice_name = voice_override
    elif raw_spec_voice in ("", "phonui") and cid in ("KENH_005", "KENH_002"):
        voice_name = "phimma"
    elif raw_spec_voice in ("", "maianh") and cid == "KENH_008":
        voice_name = "taplamcontent"
    elif raw_spec_voice == "" and cid == "KENH_001":
        voice_name = "tienvadoi"
    else:
        voice_name = raw_spec_voice or default_voice

    wavs = voice_mod.synth([sc["voiceover"].strip() for _, sc in vo_items], work / "voice", voice=voice_name) if vo_items else []
    vo_tracks, cues = [], []
    for (idx, sc), wav in zip(vo_items, wavs):
        if sc.get("ghost"):
            wav = voice_mod.ghost_fx(wav, work / "voice" / f"ghost_{sc['id']:02d}.wav", float(sc.get("ghost_semitones", -3)))
        base_vo_at = float(sc.get("vo_at", 0.45))
        if idx == 0 and cover_intro_s > 0:
            base_vo_at = max(base_vo_at, cover_intro_s + 0.05)
        sc_dur = float(sc["duration_s"])
        d = voice_mod.duration(wav)
        avail = max(0.8, sc_dur - base_vo_at - 0.08)
        if d > avail and d / avail <= 1.38:
            fit_wav = work / "voice" / f"fit_{sc['id']:02d}.wav"
            ratio = min(1.38, max(1.02, (d / avail) * 1.02))
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                 "-af", f"atempo={ratio:.3f}", "-ar", "48000", str(fit_wav)])
            wav = fit_wav
            d = voice_mod.duration(wav)
        at = starts[idx] + base_vo_at
        if at + d > starts[idx] + sc_dur + 0.08:
            report["warnings"].append(f"Cảnh {sc['id']}: lời dài {d:.1f}s vượt thời lượng cảnh")
        vo_tracks.append((wav, at))
        cues.append((at, at + d, sc.get("caption") or sc["voiceover"], "Ghost" if sc.get("ghost") else "Default"))

    # 4. Nhạc
    music_wav = work / "music.wav"
    mus_cfg = spec.get("music") or {}
    mus_gen = str(mus_cfg.get("generator", "horror")).lower()
    mus_file = mus_cfg.get("file")
    if not mus_file and (mus_gen == "finance" or cid == "KENH_001"):
        k1_music_dir = Path(r"D:\02_CONG_CU\Youtubei-Muti-Channel\Kien-Thuc- Tai-Chinh\templates\music")
        cands = sorted(k1_music_dir.glob("bg_*.mp3")) if k1_music_dir.is_dir() else []
        if not cands:
            fb_bgm = Path(r"D:\0.1_FACE_BOOK\Triet Ly Co Nhan\assets\bgm\tinh_dao_bgm.mp3")
            cands = [fb_bgm] if fb_bgm.is_file() else []
        if cands:
            mus_file = str(cands[int(spec.get("seed", 1)) % len(cands)])

    if mus_file and Path(mus_file).is_file():
        fo = max(0.0, total - 1.5)
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stream_loop", "-1", "-i", str(mus_file),
             "-t", f"{total:.2f}", "-af", f"aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:d=0.6,afade=t=out:st={fo:.2f}:d=1.5",
             str(music_wav)])
    elif mus_gen == "curiosity":
        curiosity_music.write_wav(music_wav, curiosity_music.compose(total, int(spec.get("seed", 1))))
    elif mus_gen == "wuxia":
        wuxia_music.write_wav(music_wav, wuxia_music.compose(total, int(spec.get("seed", 1))))
    else:
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

    # 7. Ảnh bìa 9:16 + Logo kênh chuẩn (ĐÃ XÓA NHÃN AIGC) + Đồng màu + Phụ đề + xuất
    write_ass(cues, work / "subs.ass")
    fonts = work / "fonts"
    if not fonts.is_dir():
        shutil.copytree(FONT_DIR, fonts)

    hero_img = None
    if spec.get("cover_image"):
        cand = fetch_clip(spec["cover_image"], clips_dir, work, 0)
        if cand and cand.suffix.lower() in IMAGE_EXT:
            hero_img = cand
    if hero_img is None and clips_dir:
        cov_sc = int(spec.get("cover_scene") or 1)
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            p_cov = clips_dir / f"scene_{cov_sc:02d}{ext}"
            if p_cov.is_file():
                hero_img = p_cov
                break
    if hero_img is None:
        at_s = float(spec.get("cover_at_s") or 3.5)
        hero_img = thumb_mod.extract_hero_frame(video_silent, work / "hero_frame.jpg", at_s=at_s)

    pre_cover = work / "cover_9x16.jpg"
    thumb_mod.render_cover(hero_img, spec, pre_cover)
    logo_png = work / "logo_overlay.png"
    thumb_mod.render_video_logo_overlay(spec, logo_png)

    vf_parts = []
    grade = spec.get("color_grade", "folk_horror")
    if grade == "folk_horror":
        vf_parts.append(
            "eq=contrast=1.06:saturation=0.92:brightness=-0.02,"
            "colorbalance=rs=0.02:gs=0.0:bs=0.05:rm=0.03:gm=0.0:bm=-0.02,"
            "noise=alls=3:allf=t+u"
        )
    elif grade == "vivid_doc":
        vf_parts.append("eq=contrast=1.06:saturation=1.10:brightness=0.01")
    elif grade == "wuxia":
        vf_parts.append(
            "eq=contrast=1.08:saturation=0.95:brightness=-0.01,"
            "colorbalance=rs=0.04:gs=0.01:bs=-0.02:rm=0.02:gm=0.01:bm=0.03,"
            "noise=alls=2:allf=t+u"
        )
    vf_parts.append("ass=subs.ass:fontsdir=fonts")
    base_vf = ",".join(vf_parts)

    fc_steps = [f"[0:v]{base_vf}[vsub]"]
    extra_inputs = ["-i", logo_png.name]
    if cover_intro_s > 0.05:
        extra_inputs += ["-i", pre_cover.name]
        fc_steps.append(f"[vsub][2:v]overlay=0:0:eof_action=repeat:enable='gte(t,{cover_intro_s:.2f})'[vlogo]")
        fc_steps.append(f"[vlogo][3:v]overlay=0:0:eof_action=repeat:enable='lt(t,{cover_intro_s:.2f})'[vout]")
    else:
        fc_steps.append("[vsub][2:v]overlay=0:0:eof_action=repeat[vout]")

    vcodec = ["-c:v", "h264_nvenc", "-preset", "p5", "-cq", "21"] if has_nvenc() else ["-c:v", "libx264", "-crf", "19"]
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-i", video_silent.name, "-i", mix_wav.name] + extra_inputs +
        ["-filter_complex", ";".join(fc_steps), "-map", "[vout]", "-map", "1:a"] + vcodec +
        ["-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.2f}", "-movflags", "+faststart", str(out.resolve())],
        cwd=work)

    # 8. Đóng gói ảnh bìa 9:16 + tiêu đề + metadata + contact sheet QC
    pkg = thumb_mod.build_package(spec, out.resolve(), work, hero_image=hero_img, pre_rendered_cover=pre_cover)
    report.update({"output": str(out), "duration_s": round(total, 2), "voice": voice_name,
                   "voice_lines": len(vo_tracks), "sfx_used": len(sfx_tracks),
                   "cover": pkg["cover_path"], "publish_title": pkg["publish_title"],
                   "contact_sheet": pkg["contact_sheet_path"]})
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
