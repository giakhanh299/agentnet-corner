"""Sync finished AgentNet videos into FB Tool KENH_008 (Tập Làm ConTent) review queue.

Copies verified 1080x1920 MP4 renders (with audio) into:
  D:\\0.1_FACE_BOOK\\videos_upload\\KENH_008_ChiDepDiCau\\02_MOI_RENDER_CHO_XAC_NHAN\\
alongside clean <stem>.caption.txt sidecars so telegram_video_reviewer.py sends them
to the owner for 1-tap approval before scheduled Facebook Reels publishing (11:20 / 17:25 / 20:25).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

MACRO_DIR = pathlib.Path(r"D:\0.1_FACE_BOOK\macro-tool")
KENH_008_DIR = pathlib.Path(r"D:\0.1_FACE_BOOK\videos_upload\KENH_008_ChiDepDiCau")
REVIEW_DIR = KENH_008_DIR / "02_MOI_RENDER_CHO_XAC_NHAN"
MANIFEST_PATH = pathlib.Path(r"D:\AI_AGENT\agentnet_kenh008_sync_manifest.json")
HASHTAGS = "#TapLamConTent #KienThucThuVi #ChuyenHay #reels"

# Exact verified episode titles & hooks from STATUS.md and render artifacts
EPISODE_META: dict[str, tuple[str, str, str]] = {
    "v002": (
        "tai_sao_goi_la_dang_nhap",
        "Mỗi lần bấm ĐĂNG NHẬP, bạn đang dùng mẹo của thủy thủ 500 năm trước?",
        "Bạn đã từng thắc mắc từ 'log in' từ đâu mà ra chưa? Bình luận nhé!",
    ),
    "v003": (
        "cap_thang_may_dut_tang_85",
        "Cáp thang máy đứt ở tầng 85 — nhảy lên ngay lúc chạm đất có sống không?",
        "Nếu gặp tình huống này bạn sẽ làm gì? Bình luận nhé!",
    ),
    "v004": (
        "ong_tu_sua_giay_chi_can_mot_nguoi_dung_lai",
        "Ông Tư sửa giày — Đôi khi chỉ cần một người dừng lại.",
        "Ai là người từng dừng lại lắng nghe bạn? Chia sẻ bên dưới nhé!",
    ),
    "v005": (
        "top_5_cau_noi_huyen_thoai_cua_me",
        "Top 5 câu nói huyền thoại của mẹ mà ai nghe cũng từng giật mình!",
        "Số 1 của bạn là câu nào? Bình luận bên dưới nhé!",
    ),
    "v006": (
        "nuoc_vua_soi_vua_dong_bang",
        "Nước có thể vừa sôi vừa đóng băng cùng một lúc không?",
        "Bạn từng nghe về điểm ba trạng thái này chưa? Bình luận nhé!",
    ),
    "v007": (
        "top_5_thu_vua_khit_hoan_hao",
        "Top 5 khoảnh khắc vừa khít hoàn hảo nhìn là thấy đã mắt!",
        "Khoảnh khắc nào làm bạn thấy thỏa mãn nhất?",
    ),
    "v009": (
        "top_5_su_that_dong_vat",
        "Top 5 sự thật khó tin về thế giới động vật!",
        "Bạn bất ngờ nhất với sự thật nào? Bình luận nhé!",
    ),
    "v010": (
        "bai_bao_1960_du_bao_tan_the",
        "Bài báo năm 1960 từng dự báo ngày tận thế — Sự thật phía sau con số!",
        "Đừng tin mọi phép toán kéo dài vô hạn — bạn nghĩ sao?",
    ),
    "v011": (
        "canada_giu_hon_nua_so_ho_the_gioi",
        "Một quốc gia giữ hơn nửa số hồ tự nhiên trên toàn thế giới?",
        "Bạn đoán được đất nước nào chưa? Bình luận nhé!",
    ),
    "v012": (
        "cho_nha_ban_hieu_bao_nhieu_tu",
        "Chó nhà bạn hiểu được bao nhiêu từ? Gần bằng một em bé 2 tuổi đó!",
        "Chú cún nhà bạn thích nghe hai từ nào nhất?",
    ),
    "v014": (
        "dung_lam_them_gio_nua_ai_video",
        "Đừng làm thêm kiểu cũ nữa — xem máy tự dựng video 45 giây chỉ trong tích tắc!",
        "Làm kiểu cũ đổi giờ lấy tiền hay để máy làm hộ? Bạn chọn cách nào?",
    ),
}


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def probe_valid_video(path: pathlib.Path) -> tuple[bool, str]:
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=codec_type,width,height:format=duration",
                "-of",
                "json",
                str(path),
            ],
            text=True,
            encoding="utf-8",
            timeout=10,
        )
        info = json.loads(out)
        streams = {s.get("codec_type"): s for s in info.get("streams", [])}
        v = streams.get("video")
        a = streams.get("audio")
        dur = float(info.get("format", {}).get("duration", 0) or 0)
        if not v or not a or dur < 10.0:
            return False, f"missing stream or short ({dur:.1f}s)"
        return True, f"{dur:.1f}s {v.get('width')}x{v.get('height')}"
    except Exception as exc:
        return False, str(exc)


def episode_key(path: pathlib.Path) -> str:
    m = re.match(r"^(v\d{3})\b", path.stem, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    m_ep = re.search(r"(ep\d{3})", path.as_posix(), re.IGNORECASE)
    return m_ep.group(1).lower() if m_ep else re.sub(r"[^a-z0-9]+", "_", path.stem.lower()).strip("_")


def build_caption(ep: str, src_path: pathlib.Path) -> tuple[str, str]:
    if ep in EPISODE_META:
        slug, hook, cta = EPISODE_META[ep]
        caption = f"{hook}\n\n{cta}\n\n{HASHTAGS}\n"
        return f"{ep}_{slug}.mp4", caption

    # Fallback: read hook.txt / endcard_cta.txt beside render output if present
    parent = src_path.parent
    hook = ""
    cta = ""
    for fname, target in (("hook.txt", "hook"), ("endcard_cta.txt", "cta")):
        fp = parent / fname
        if fp.is_file():
            txt = " ".join(fp.read_text(encoding="utf-8", errors="ignore").split())
            if target == "hook":
                hook = txt
            else:
                cta = txt
    parts = [p for p in (hook, cta, HASHTAGS) if p]
    if not hook:
        parts.insert(0, "Video kiến thức thú vị mỗi ngày!")
    slug = re.sub(r"[^a-z0-9]+", "_", src_path.stem.lower()).strip("_")
    return f"{ep}_{slug}.mp4" if not slug.startswith(ep) else f"{slug}.mp4", "\n\n".join(parts) + "\n"


def discover_candidates() -> list[pathlib.Path]:
    raw: list[pathlib.Path] = []
    patterns = [
        pathlib.Path(r"C:\Users\w\Downloads").glob("v*.mp4"),
        pathlib.Path(r"C:\Users\w").glob("v*_render/v*.mp4"),
        pathlib.Path(r"D:\AI_AGENT\agentnet-corner\video_production").glob("v*/v*.mp4"),
        pathlib.Path(r"D:\AI_AGENT\agentnet-corner\studio_runs").glob("*/final.mp4"),
    ]
    for it in patterns:
        for p in it:
            low = p.name.lower()
            if not p.is_file() or p.stat().st_size < 500_000:
                continue
            if low.endswith(("_video.mp4", "_raw.mp4")) or low.startswith(("beat", "test_")):
                continue
            raw.append(p)

    # Deduplicate by episode key, preferring *_render over Downloads
    chosen: dict[str, pathlib.Path] = {}
    for p in sorted(raw, key=lambda x: (0 if "_render" in str(x.parent) else 1, x.name)):
        ep = episode_key(p)
        if ep not in chosen:
            chosen[ep] = p
    return [chosen[k] for k in sorted(chosen.keys())]


def load_manifest() -> dict:
    if MANIFEST_PATH.is_file():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"synced_by_sha256": {}, "synced_by_episode": {}}


def existing_stage_shas() -> set[str]:
    shas: set[str] = set()
    for stage in ("01_DA_DANG", "02_MOI_RENDER_CHO_XAC_NHAN", "03_CHUAN_BI_UP", "04_DA_UP", "99_FAILED"):
        d = KENH_008_DIR / stage
        if d.is_dir():
            for mp4 in d.glob("*.mp4"):
                try:
                    shas.add(sha256_file(mp4))
                except OSError:
                    pass
    return shas


def sync_videos(dry_run: bool = False, limit: int = 0, episodes: set[str] | None = None) -> dict:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    known_shas = set(manifest.get("synced_by_sha256", {}).keys()) | existing_stage_shas()
    known_eps = set(manifest.get("synced_by_episode", {}).keys())

    candidates = discover_candidates()
    imported: list[dict] = []
    skipped: list[dict] = []

    for src in candidates:
        ep = episode_key(src)
        if episodes and ep not in episodes:
            continue
        sha = sha256_file(src)
        if sha in known_shas or ep in known_eps:
            skipped.append({"episode": ep, "src": str(src), "reason": "already_synced"})
            continue

        ok, detail = probe_valid_video(src)
        if not ok:
            skipped.append({"episode": ep, "src": str(src), "reason": f"invalid_media:{detail}"})
            continue

        dest_name, caption = build_caption(ep, src)
        dest_mp4 = REVIEW_DIR / dest_name
        dest_cap = dest_mp4.with_suffix(".caption.txt")

        if dest_mp4.exists():
            skipped.append({"episode": ep, "src": str(src), "reason": "dest_exists"})
            continue

        if limit and len(imported) >= limit:
            break

        if not dry_run:
            dest_cap.write_text(caption, encoding="utf-8")
            tmp = REVIEW_DIR / f"{dest_mp4.stem}.sync.tmp"
            shutil.copyfile(str(src), str(tmp))
            os.replace(str(tmp), str(dest_mp4))
            manifest.setdefault("synced_by_sha256", {})[sha] = dest_name
            manifest.setdefault("synced_by_episode", {})[ep] = {
                "file": dest_name,
                "sha256": sha,
                "src": str(src),
                "detail": detail,
            }

        imported.append({"episode": ep, "dest": dest_name, "detail": detail})

    if not dry_run and imported:
        MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"dry_run": dry_run, "imported": imported, "skipped": skipped}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--episodes", default="", help="Comma-separated episode keys, e.g. v006,v007")
    args = ap.parse_args()
    eps = {x.strip().lower() for x in args.episodes.split(",") if x.strip()} or None
    print(json.dumps(sync_videos(dry_run=args.dry_run, limit=args.limit, episodes=eps), ensure_ascii=False, indent=2))
