"""Tạo ảnh bìa dọc 9:16 (cover_9x16.jpg) có LOGO kênh chuẩn (KHÔNG nhãn AIGC), tiêu đề/caption đúng hashtag từng kênh và contact_sheet.png."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FONT_DIR = REPO / "stickman-shorts" / "src" / "assets" / "fonts"
FONT_BOLD = FONT_DIR / "BeVietnamPro-Bold.ttf"
FONT_REG = FONT_DIR / "BeVietnamPro-Regular.ttf"
W, H = 1080, 1920

K1_AVATAR_CANDIDATES = [
    Path(r"D:\0.1_FACE_BOOK\videos_upload\KENH_001_TienVaDoi\branding\anh_dai_dien_tien_va_doi.png"),
    Path(r"D:\02_CONG_CU\Youtubei-Muti-Channel\Kien-Thuc- Tai-Chinh\anh dai dien.png"),
]
K1_AVATAR = next((p for p in K1_AVATAR_CANDIDATES if p.is_file()), None)

CHANNEL_BRANDS = {
    "KENH_005": {
        "name": "Vũ Trụ Cày Phim",
        "tag": "@VuTruCayPhim",
        "hashtags": ["#VuTruCayPhim", "#MePhim", "#ReviewPhim", "#TomTatPhim", "#PhimHay", "#PhimDienAnh", "#reels"],
        "avatar": None,
        "mode": "movie",
    },
    "KENH_002": {
        "name": "Bật Phim Lên",
        "tag": "@BatPhimLen",
        "hashtags": ["#BatPhimLen", "#MePhim", "#ReviewPhim", "#TomTatPhim", "#PhimHay", "#PhimDienAnh", "#reels"],
        "avatar": None,
        "mode": "movie",
    },
    "KENH_008": {
        "name": "Tập Làm Content",
        "tag": "@TapLamContent",
        "hashtags": ["#TapLamContent", "#KienThucThuVi", "#KhamPha", "#KhoaHoc", "#SuThatThuVi", "#reels"],
        "avatar": None,
        "mode": "knowledge",
    },
    "KENH_001": {
        "name": "Tiền Và Đời",
        "tag": "@TienVaDoi",
        "hashtags": ["#TienVaDoi", "#TaiChinh", "#KienThucTaiChinh", "#TuDuyTaiChinh", "#reels"],
        "avatar": K1_AVATAR,
        "mode": "finance",
    },
}


def resolve_brand(spec: dict) -> dict:
    cid = str(spec.get("target_channel") or "").upper().strip()
    if cid in CHANNEL_BRANDS:
        return CHANNEL_BRANDS[cid]
    s = str(spec.get("series") or "").lower()
    if "tiền" in s or "tài chính" in s:
        return CHANNEL_BRANDS["KENH_001"]
    if "content" in s or "kiến thức" in s:
        return CHANNEL_BRANDS["KENH_008"]
    if "bật phim" in s:
        return CHANNEL_BRANDS["KENH_002"]
    return CHANNEL_BRANDS["KENH_005"]


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.is_file():
        return ImageFont.truetype(str(path), size)
    for fb in (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if Path(fb).is_file():
            return ImageFont.truetype(fb, size)
    return ImageFont.load_default()


def _wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int, max_lines: int = 3) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if draw.textbbox((0, 0), cand, font=font)[2] <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:max_lines]


def extract_hero_frame(video: Path, dst: Path, at_s: float = 3.0) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{at_s:.2f}",
         "-i", str(video), "-frames:v", "1", "-q:v", "2", str(dst)],
        check=True,
    )
    if not dst.is_file():
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", str(video), "-frames:v", "1", "-q:v", "2", str(dst)],
            check=True,
        )
    return dst


def make_contact_sheet(video: Path, dst: Path, cols: int = 3, rows: int = 2) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dur_out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    dur = max(1.0, float(dur_out or 10.0))
    n = cols * rows
    fps = n / dur
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video),
         "-vf", f"fps={fps:.4f},scale=360:640,tile={cols}x{rows}:padding=6:color=black",
         "-frames:v", "1", str(dst)],
        check=True,
    )
    return dst


def _paste_circle_avatar(base: Image.Image, avatar_path: Path, x: int, y: int, size: int) -> None:
    try:
        av = Image.open(avatar_path).convert("RGBA")
        av = ImageOps.fit(av, (size, size), Image.Resampling.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
        base.paste(av, (x, y), mask)
    except Exception:
        pass


def render_cover(bg_image: Path, spec: dict, dst: Path) -> Path:
    """Vẽ ảnh bìa dọc 1080x1920 sắc nét + LOGO kênh chuẩn (KHÔNG gắn nhãn AIGC)."""
    brand = resolve_brand(spec)
    img = Image.open(bg_image).convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - W) // 2, (nh - H) // 2
    img = img.crop((left, top, left + W, top + H))
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Color(img).enhance(0.98)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, 440):
        alpha = int(195 * (1 - y / 440) ** 1.6)
        od.line([(0, y), (W, y)], fill=(5, 8, 14, alpha))
    for y in range(H - 860, H):
        t = (y - (H - 860)) / 860
        alpha = int(235 * (t ** 1.35))
        od.line([(0, y), (W, y)], fill=(5, 7, 12, alpha))

    base = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(base)

    theme = str(spec.get("cover_theme") or "horror").lower()
    if theme == "knowledge" or brand["mode"] in ("knowledge", "finance"):
        badge_outline, badge_fill, badge_text_col, accent_bar_col = (56, 212, 232, 235), (10, 26, 38, 215), (255, 224, 112, 255), (255, 196, 46, 245)
    elif theme == "wuxia":
        badge_outline, badge_fill, badge_text_col, accent_bar_col = (232, 196, 112, 235), (20, 16, 12, 215), (248, 224, 152, 255), (204, 158, 62, 245)
    else:
        badge_outline, badge_fill, badge_text_col, accent_bar_col = (245, 166, 35, 225), (14, 18, 26, 210), (248, 190, 72, 255), (220, 62, 46, 240)

    # Top Channel Logo Badge (replaces generic episode text & AIGC label)
    logo_label = f"{brand['name'].upper()}  ·  {brand['tag']}"
    f_badge = _font(FONT_BOLD, 34)
    bx0, by0, bx1, by1 = draw.textbbox((0, 0), logo_label, font=f_badge)
    bw, bh = bx1 - bx0, by1 - by0
    av_path = brand.get("avatar")
    av_w = 56 if (av_path and Path(av_path).is_file()) else 0
    pad_x, pad_y = 30, 16
    total_w = bw + (av_w + 16 if av_w else 0)
    rx0 = (W - total_w) // 2 - pad_x
    ry0 = 96
    box_h = max(bh + pad_y * 2, av_w + 16)
    draw.rounded_rectangle([rx0, ry0, rx0 + total_w + pad_x * 2, ry0 + box_h],
                           radius=box_h // 2, fill=badge_fill, outline=badge_outline, width=3)
    tx = rx0 + pad_x
    if av_w:
        _paste_circle_avatar(base, Path(av_path), tx, ry0 + (box_h - av_w) // 2, av_w)
        draw = ImageDraw.Draw(base)
        tx += av_w + 16
    draw.text((tx, ry0 + (box_h - bh) // 2 - 3), logo_label, font=f_badge, fill=badge_text_col)

    # Main dramatic title
    ep_num = int(spec.get("episode") or 1)
    cover_title = str(spec.get("cover_title") or spec.get("title") or f"Tập {ep_num}").upper()
    f_title = _font(FONT_BOLD, 106)
    lines = _wrap_lines(draw, cover_title, f_title, W - 120, max_lines=3)
    if len(lines) >= 3:
        f_title = _font(FONT_BOLD, 88)
        lines = _wrap_lines(draw, cover_title, f_title, W - 120, max_lines=3)

    hook = str(spec.get("cover_hook") or "").strip()
    if not hook:
        scenes = sorted(spec.get("scenes") or [], key=lambda s: s.get("id", 0))
        first_vo = (scenes[0].get("voiceover") or "").strip() if scenes else ""
        hook = first_vo[:76] + ("…" if len(first_vo) > 76 else "")
    f_hook = _font(FONT_REG, 40)
    hook_lines = _wrap_lines(draw, hook, f_hook, W - 140, max_lines=2) if hook else []

    title_line_h = int(f_title.size * 1.18)
    hook_line_h = int(f_hook.size * 1.32)
    block_h = len(lines) * title_line_h + 26 + len(hook_lines) * hook_line_h
    y = H - 190 - block_h

    draw.rounded_rectangle([(W - 140) // 2, y - 34, (W + 140) // 2, y - 24], radius=5, fill=accent_bar_col)

    for ln in lines:
        bb = draw.textbbox((0, 0), ln, font=f_title)
        lw = bb[2] - bb[0]
        x = (W - lw) // 2
        draw.text((x + 4, y + 6), ln, font=f_title, fill=(0, 0, 0, 215))
        draw.text((x, y), ln, font=f_title, fill=(250, 242, 224, 255))
        y += title_line_h

    y += 18
    for hl in hook_lines:
        bb = draw.textbbox((0, 0), hl, font=f_hook)
        lw = bb[2] - bb[0]
        x = (W - lw) // 2
        draw.text((x + 2, y + 3), hl, font=f_hook, fill=(0, 0, 0, 200))
        draw.text((x, y), hl, font=f_hook, fill=(224, 232, 242, 240))
        y += hook_line_h

    # Subtle bottom channel watermark (ZERO AIGC text!)
    f_wm = _font(FONT_BOLD, 28)
    wm_txt = f"{brand['name']} · {brand['tag']}"
    bb = draw.textbbox((0, 0), wm_txt, font=f_wm)
    draw.text((W - (bb[2] - bb[0]) - 42, H - 74), wm_txt, font=f_wm, fill=(255, 255, 255, 175))

    dst.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(dst, "JPEG", quality=93, optimize=True)
    return dst


def build_metadata(spec: dict, video_path: Path, cover_path: Path) -> dict:
    brand = resolve_brand(spec)
    ep = int(spec.get("episode") or 1)
    title_core = str(spec.get("title") or f"Tập {ep}").strip()
    scenes = sorted(spec.get("scenes") or [], key=lambda s: s.get("id", 0))
    hook = str(spec.get("cover_hook") or (scenes[0].get("voiceover") if scenes else "") or "").strip()
    hashtags = brand["hashtags"]
    tag_line = " ".join(hashtags)

    if brand["mode"] == "movie":
        publish_title = f"🎬 {title_core.upper()} 🔥"
        desc = (
            f"{hook} Cùng theo dõi để khám phá những tình tiết bất ngờ của câu chuyện này nhé! 🍿\n\n"
            f"🎬 Phim hay thì kể, phim dở cũng tám!\n"
            f"👀 Vào {brand['name']} coi có gì vui!\n\n"
            f"{tag_line}"
        )
    elif brand["mode"] == "finance":
        publish_title = title_core
        desc = f"{hook}\n\n{tag_line}"
    else:
        publish_title = f"💡 {title_core}"
        desc = f"{hook}\n\nTheo dõi {brand['name']} mỗi ngày để khám phá thêm nhiều sự thật thú vị!\n\n{tag_line}"

    return {
        "episode": ep,
        "channel_name": brand["name"],
        "channel_tag": brand["tag"],
        "title": title_core,
        "publish_title": publish_title,
        "cover_title": str(spec.get("cover_title") or title_core).upper(),
        "cover_hook": hook,
        "description": desc,
        "hashtags": hashtags,
        "video_file": video_path.name,
        "cover_file": cover_path.name,
    }


def render_video_logo_overlay(spec: dict, dst: Path) -> Path:
    """Tạo lớp phủ RGBA 1080x1920 chứa Logo kênh góc phải trên + watermark chìm góc dưới (KHÔNG AIGC)."""
    brand = resolve_brand(spec)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    mode = brand["mode"]
    if mode in ("knowledge", "finance"):
        outline_col, fill_col, title_col = (240, 198, 92, 195), (8, 18, 30, 160), (255, 246, 224, 235)
    else:
        outline_col, fill_col, title_col = (235, 168, 52, 185), (12, 14, 20, 155), (255, 244, 226, 230)

    f_name = _font(FONT_BOLD, 28)
    f_tag = _font(FONT_REG, 21)
    nb = draw.textbbox((0, 0), brand["name"], font=f_name)
    tb = draw.textbbox((0, 0), brand["tag"], font=f_tag)
    text_w = max(nb[2] - nb[0], tb[2] - tb[0])
    text_h = (nb[3] - nb[1]) + 6 + (tb[3] - tb[1])

    av_path = brand.get("avatar")
    has_av = bool(av_path and Path(av_path).is_file())
    av_sz = 58 if has_av else 0
    pad_x, pad_y = 22, 12
    inner_w = text_w + (av_sz + 14 if has_av else 0)
    box_w = inner_w + pad_x * 2
    box_h = max(text_h + pad_y * 2, av_sz + 14)

    x0 = W - box_w - 36
    y0 = 54
    draw.rounded_rectangle([x0, y0, x0 + box_w, y0 + box_h], radius=box_h // 2,
                           fill=fill_col, outline=outline_col, width=2)
    tx = x0 + pad_x
    if has_av:
        _paste_circle_avatar(canvas, Path(av_path), tx, y0 + (box_h - av_sz) // 2, av_sz)
        draw = ImageDraw.Draw(canvas)
        tx += av_sz + 14
    ty = y0 + (box_h - text_h) // 2 - 2
    draw.text((tx, ty), brand["name"], font=f_name, fill=title_col)
    draw.text((tx, ty + (nb[3] - nb[1]) + 4), brand["tag"], font=f_tag, fill=(214, 224, 238, 195))

    # Subtle bottom-right handle watermark (replaces AIGC completely)
    f_wm = _font(FONT_BOLD, 24)
    wm = brand["tag"]
    wb = draw.textbbox((0, 0), wm, font=f_wm)
    wx = W - (wb[2] - wb[0]) - 38
    wy = H - 68
    draw.text((wx + 2, wy + 2), wm, font=f_wm, fill=(0, 0, 0, 120))
    draw.text((wx, wy), wm, font=f_wm, fill=(255, 255, 255, 130))

    dst.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dst, "PNG")
    return dst


def build_package(spec: dict, video_path: Path, work_dir: Path, hero_image: Path | None = None,
                  pre_rendered_cover: Path | None = None) -> dict:
    out_dir = video_path.parent
    stem = video_path.stem
    cover_path = out_dir / f"{stem}_cover_9x16.jpg"
    if pre_rendered_cover and Path(pre_rendered_cover).is_file():
        if Path(pre_rendered_cover).resolve() != cover_path.resolve():
            import shutil
            shutil.copy2(pre_rendered_cover, cover_path)
    else:
        if hero_image and Path(hero_image).is_file():
            bg = Path(hero_image)
        else:
            at_s = float(spec.get("cover_at_s") or 3.5)
            bg = extract_hero_frame(video_path, work_dir / "hero_frame.jpg", at_s=at_s)
        render_cover(bg, spec, cover_path)

    meta = build_metadata(spec, video_path, cover_path)
    meta_path = out_dir / f"{stem}_metadata.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    title_txt = out_dir / f"{stem}_title.txt"
    title_txt.write_text(
        f"TIÊU ĐỀ ĐĂNG:\n{meta['publish_title']}\n\nCHỮ BÌA 9:16:\n{meta['cover_title']}\n\nMÔ TẢ & HASHTAG:\n{meta['description']}\n",
        encoding="utf-8",
    )

    sheet_path = out_dir / f"{stem}_contact_sheet.png"
    make_contact_sheet(video_path, sheet_path)

    return {
        "cover_path": str(cover_path),
        "metadata_path": str(meta_path),
        "title_path": str(title_txt),
        "contact_sheet_path": str(sheet_path),
        "publish_title": meta["publish_title"],
    }
