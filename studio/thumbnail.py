"""Tạo ảnh bìa dọc 9:16 (cover_9x16.jpg), tiêu đề/mô tả (title.txt, metadata.json) và contact_sheet.png cho mỗi tập."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FONT_DIR = REPO / "stickman-shorts" / "src" / "assets" / "fonts"
FONT_BOLD = FONT_DIR / "BeVietnamPro-Bold.ttf"
FONT_REG = FONT_DIR / "BeVietnamPro-Regular.ttf"
W, H = 1080, 1920


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


def render_cover(bg_image: Path, spec: dict, dst: Path) -> Path:
    """Vẽ ảnh bìa dọc 1080x1920 chuyên nghiệp từ khung hình đẹp nhất + tiêu đề tiếng Việt có dấu."""
    img = Image.open(bg_image).convert("RGB")
    # Center-crop to 9:16
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - W) // 2, (nh - H) // 2
    img = img.crop((left, top, left + W, top + H))
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Color(img).enhance(0.95)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Top scrim for series badge
    for y in range(0, 460):
        alpha = int(200 * (1 - y / 460) ** 1.6)
        od.line([(0, y), (W, y)], fill=(5, 8, 14, alpha))
    # Bottom scrim for big title + hook
    for y in range(H - 860, H):
        t = (y - (H - 860)) / 860
        alpha = int(235 * (t ** 1.35))
        od.line([(0, y), (W, y)], fill=(5, 7, 12, alpha))

    base = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(base)

    theme = str(spec.get("cover_theme") or "horror").lower()
    is_know = theme == "knowledge"
    badge_outline = (56, 212, 232, 235) if is_know else (245, 166, 35, 220)
    badge_fill = (10, 26, 38, 210) if is_know else (14, 18, 26, 195)
    badge_text_col = (120, 240, 255, 255) if is_know else (248, 190, 72, 255)
    accent_bar_col = (255, 196, 46, 245) if is_know else (220, 62, 46, 240)

    series = str(spec.get("series") or "Phim Ma Dân Gian Việt Nam").upper()
    ep_num = int(spec.get("episode") or 1)
    badge_text = f"{series}  ·  TẬP {ep_num:02d}"
    f_badge = _font(FONT_BOLD, 34)
    bx0, by0, bx1, by1 = draw.textbbox((0, 0), badge_text, font=f_badge)
    bw, bh = bx1 - bx0, by1 - by0
    pad_x, pad_y = 32, 16
    rx0 = (W - bw) // 2 - pad_x
    ry0 = 110
    draw.rounded_rectangle([rx0, ry0, rx0 + bw + pad_x * 2, ry0 + bh + pad_y * 2],
                           radius=14, fill=badge_fill, outline=badge_outline, width=3)
    draw.text(((W - bw) // 2, ry0 + pad_y - 3), badge_text, font=f_badge, fill=badge_text_col)

    # Main dramatic title
    cover_title = str(spec.get("cover_title") or spec.get("title") or f"Tập {ep_num}").upper()
    f_title = _font(FONT_BOLD, 108)
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
    y = H - 220 - block_h

    # Accent bar above title
    draw.rounded_rectangle([(W - 140) // 2, y - 34, (W + 140) // 2, y - 24], radius=5, fill=accent_bar_col)

    for ln in lines:
        bb = draw.textbbox((0, 0), ln, font=f_title)
        lw = bb[2] - bb[0]
        x = (W - lw) // 2
        draw.text((x + 4, y + 6), ln, font=f_title, fill=(0, 0, 0, 210))
        draw.text((x, y), ln, font=f_title, fill=(250, 242, 224, 255))
        y += title_line_h

    y += 18
    for hl in hook_lines:
        bb = draw.textbbox((0, 0), hl, font=f_hook)
        lw = bb[2] - bb[0]
        x = (W - lw) // 2
        draw.text((x + 2, y + 3), hl, font=f_hook, fill=(0, 0, 0, 200))
        draw.text((x, y), hl, font=f_hook, fill=(224, 232, 242, 235))
        y += hook_line_h

    if spec.get("aigc_label", True):
        f_ai = _font(FONT_BOLD, 28)
        ai_txt = "AIGC · Nội dung tạo bởi AI"
        bb = draw.textbbox((0, 0), ai_txt, font=f_ai)
        draw.text((W - (bb[2] - bb[0]) - 42, H - 78), ai_txt, font=f_ai, fill=(255, 255, 255, 175))

    dst.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(dst, "JPEG", quality=92, optimize=True)
    return dst


def build_metadata(spec: dict, video_path: Path, cover_path: Path) -> dict:
    ep = int(spec.get("episode") or 1)
    series = str(spec.get("series") or "Phim Ma Dân Gian Việt Nam")
    title_core = str(spec.get("title") or f"Tập {ep}")
    scenes = sorted(spec.get("scenes") or [], key=lambda s: s.get("id", 0))
    hook = str(spec.get("cover_hook") or (scenes[0].get("voiceover") if scenes else "") or "").strip()
    publish_title = str(spec.get("publish_title") or f"{title_core} | {series} – Tập {ep:02d}")
    hashtags = spec.get("hashtags") or [
        "#PhimMaDanGian", "#ChuyenMaVietNam", "#TruyenThuyetDanGian",
        "#GocNhoPhoNui", "#ShortHorror", "#AIGC",
    ]
    cta = str(spec.get("cta") or "Bạn đã từng nghe người lớn kể chuyện này ở quê chưa? Bình luận bên dưới nhé!")
    desc = str(spec.get("description") or (
        f"{hook}\n\n"
        f"{series} – Tập {ep:02d}: {title_core}.\n"
        f"{cta}\n\n"
        "Lưu ý: Video minh họa dân gian được dàn dựng bằng AI (AIGC) phục vụ giải trí & kể chuyện.\n"
        + " ".join(hashtags)
    ))
    return {
        "episode": ep,
        "series": series,
        "title": title_core,
        "publish_title": publish_title,
        "cover_title": str(spec.get("cover_title") or title_core).upper(),
        "cover_hook": hook,
        "description": desc,
        "cta": cta,
        "hashtags": hashtags,
        "aigc_label": bool(spec.get("aigc_label", True)),
        "video_path": str(video_path),
        "cover_path": str(cover_path),
    }


def build_package(spec: dict, video_path: Path, work_dir: Path, hero_image: Path | None = None) -> dict:
    out_dir = video_path.parent
    stem = video_path.stem
    cover_path = out_dir / f"{stem}_cover_9x16.jpg"
    sheet_path = out_dir / f"{stem}_contact_sheet.png"
    meta_path = out_dir / f"{stem}_metadata.json"
    title_path = out_dir / f"{stem}_title.txt"

    bg = hero_image if (hero_image and hero_image.is_file()) else extract_hero_frame(video_path, work_dir / "hero_frame.jpg", at_s=3.5)
    render_cover(bg, spec, cover_path)
    make_contact_sheet(video_path, sheet_path)
    meta = build_metadata(spec, video_path, cover_path)
    meta["contact_sheet_path"] = str(sheet_path)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    title_path.write_text(
        f"TIÊU ĐỀ:\n{meta['publish_title']}\n\n"
        f"CHỮ TRÊN ẢNH BÌA:\n{meta['cover_title']}\n{meta['cover_hook']}\n\n"
        f"MÔ TẢ & HASHTAG:\n{meta['description']}\n",
        encoding="utf-8",
    )
    return meta
