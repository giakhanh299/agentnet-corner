"""Hậu kỳ thuần trên PC cho các tập đã đủ 11/11 clip .mp4 từ Muse trong E:\\MUSE_MEDIA_STUDIO.

- TUYỆT ĐỐI KHÔNG vẽ ảnh cảnh bằng GPU máy nhà, KHÔNG đăng bài bằng Graph API.
- Dùng đúng 11 clip .mp4 của Muse (02_muse_clips/scene_01..11.mp4) để ghép phim 1080x1920 @ 30fps.
- Dùng ảnh 1152x2048 sắc nét của Muse (01_muse_images/) làm nền cho ảnh bìa 9:16 + mở đầu 0.85s + Logo kênh chuẩn.
- ĐÃ XÓA HOÀN TOÀN nhãn AIGC và hashtag #AIGC; dùng đúng giọng và hashtag chuẩn từng kênh.
- Xếp vào 02_MOI_RENDER_CHO_XAC_NHAN của đúng kênh để người dùng duyệt & đăng theo lịch trình duyệt.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_CORE = Path(r"D:\AI_AGENT\agentnet-corner-core")
REPO_MA = Path(r"D:\AI_AGENT\agentnet-corner-phim-ma\channels")
REPO_K08 = Path(r"D:\AI_AGENT\agentnet-corner-k08\channels\tap-lam-content-k08\episodes")
MEDIA_ROOT = Path(r"E:\MUSE_MEDIA_STUDIO")
FB_ROOT = Path(r"D:\0.1_FACE_BOOK\videos_upload")

sys.path.insert(0, str(REPO_CORE / "studio"))
import assemble_episode as ae  # noqa: E402

FB_STAGE_DIRS = {
    "KENH_001": FB_ROOT / "KENH_001_TienVaDoi" / "02_MOI_RENDER_CHO_XAC_NHAN",
    "KENH_002": FB_ROOT / "KENH_002_BatPhimLen" / "02_MOI_RENDER_CHO_XAC_NHAN",
    "KENH_005": FB_ROOT / "KENH_005_VuTruCayPhim" / "02_MOI_RENDER_CHO_XAC_NHAN",
    "KENH_008": FB_ROOT / "KENH_008_ChiDepDiCau" / "02_MOI_RENDER_CHO_XAC_NHAN",
}

CHANNEL_ROUTING = {
    "phim-ma-dan-gian": ("KENH_005", "phim_ma"),
    "tap-lam-content": ("KENH_008", ""),
    "tien-va-doi-srt": ("KENH_001", ""),
    "kiem-hiep-co-trang": ("KENH_005", "kiem_hiep"),
}


def measure_qc(mp4: Path) -> dict:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_name,width,height,r_frame_rate",
         "-of", "json", str(mp4)],
        capture_output=True, text=True, encoding="utf-8",
    )
    info = json.loads(p.stdout or "{}")
    eb = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    lufs = re.findall(r"I:\s*([-\d.]+)\s*LUFS", eb.stderr)
    peak = re.findall(r"Peak:\s*([-\d.]+)\s*dBFS", eb.stderr)
    v = next((s for s in info.get("streams", []) if s.get("width")), {})
    return {
        "duration_s": round(float((info.get("format") or {}).get("duration") or 0), 2),
        "size_mb": round(int((info.get("format") or {}).get("size") or 0) / (1024 * 1024), 2),
        "res": f"{v.get('width')}x{v.get('height')}",
        "fps": v.get("r_frame_rate"),
        "lufs": float(lufs[-1]) if lufs else None,
        "peak_dbfs": float(peak[-1]) if peak else None,
    }


def stage_to_fb(cid: str, prefix: str, slug: str, final_dir: Path) -> str:
    fb_dir = FB_STAGE_DIRS[cid]
    fb_dir.mkdir(parents=True, exist_ok=True)
    src_mp4 = final_dir / f"{slug}.mp4"
    src_cov = final_dir / f"{slug}_cover_9x16.jpg"
    meta = json.loads((final_dir / f"{slug}_metadata.json").read_text(encoding="utf-8"))
    fname = f"{prefix}_{slug}" if prefix else slug
    dst_mp4 = fb_dir / f"{fname}.mp4"
    dst_cov = fb_dir / f"{fname}_cover.jpg"
    dst_thumb = fb_dir / f"{fname}_thumbnail.jpg"
    dst_cap = dst_mp4.with_suffix(".caption.txt")
    shutil.copy2(src_mp4, dst_mp4)
    if src_cov.is_file():
        shutil.copy2(src_cov, dst_cov)
        shutil.copy2(src_cov, dst_thumb)
    caption = f"{meta['publish_title']}\n\n{meta['description']}".strip() + "\n"
    dst_cap.write_text(caption, encoding="utf-8")
    return str(dst_mp4)


def find_spec(ch_key: str, slug: str) -> Path | None:
    if ch_key == "tap-lam-content":
        p = REPO_K08 / slug / "episode.json"
    else:
        p = REPO_MA / ch_key / slug / "episode.json"
    return p if p.is_file() else None


def main() -> None:
    rendered = []
    skipped = 0
    errors = []

    for ch_key, (cid, prefix) in CHANNEL_ROUTING.items():
        ch_dir = MEDIA_ROOT / ch_key
        if not ch_dir.is_dir():
            continue
        fb_dir = FB_STAGE_DIRS[cid]
        for ep_dir in sorted(ch_dir.iterdir()):
            if not ep_dir.is_dir():
                continue
            slug = ep_dir.name
            fname = f"{prefix}_{slug}" if prefix else slug
            if (fb_dir / f"{fname}.mp4").is_file() and (fb_dir / f"{fname}.caption.txt").is_file():
                skipped += 1
                continue
            clip_dir = ep_dir / "02_muse_clips"
            img_dir = ep_dir / "01_muse_images"
            final_dir = ep_dir / "03_final_v2"
            out_mp4 = final_dir / f"{slug}.mp4"
            if out_mp4.is_file() and (final_dir / "qc_report_v2.json").is_file():
                skipped += 1
                continue
            spec_path = find_spec(ch_key, slug)
            if not spec_path:
                continue
            spec_peek = json.loads(spec_path.read_text(encoding="utf-8"))
            n_expected = len(spec_peek.get("scenes", [])) or 11
            # Kênh phim cốt truyện (Phim Ma & Kiếm Hiệp -> KENH_005): CẤM TUYỆT ĐỐI xuất phim ngắn < 32 cảnh (< 4 phút)!
            if ch_key in ("phim-ma-dan-gian", "kiem-hiep-co-trang") and n_expected < 32:
                continue
            clips = [
                clip_dir / f"scene_{sid:02d}.mp4"
                for sid in range(1, n_expected + 1)
                if (clip_dir / f"scene_{sid:02d}.mp4").is_file() and (clip_dir / f"scene_{sid:02d}.mp4").stat().st_size > 20_000
            ] if clip_dir.is_dir() else []
            if len(clips) < n_expected:
                continue
            final_dir.mkdir(parents=True, exist_ok=True)
            print(f"POSTPROD_V2 {ch_key}/{slug} -> {cid} ({len(clips)}/{n_expected} Muse .mp4 clips)...", flush=True)
            try:
                spec = spec_peek
                spec["target_channel"] = cid
                spec["aigc_label"] = False
                spec["hashtags"] = [h for h in (spec.get("hashtags") or []) if "aigc" not in str(h).lower()]
                if img_dir.is_dir():
                    cov_idx = int(spec.get("cover_scene") or 1)
                    cand = img_dir / f"scene_{cov_idx:02d}.jpg"
                    if not cand.is_file():
                        imgs = sorted(img_dir.glob("scene_*.jpg"))
                        cand = imgs[0] if imgs else None
                    if cand and cand.is_file():
                        spec["cover_image"] = str(cand)
                for sc in spec.get("scenes", []):
                    sid = int(sc["id"])
                    mp4_c = clip_dir / f"scene_{sid:02d}.mp4"
                    if mp4_c.is_file() and mp4_c.stat().st_size > 20_000:
                        sc["clip"] = str(mp4_c)

                work_dir = ep_dir / "03_work_v2"
                if work_dir.is_dir():
                    shutil.rmtree(work_dir)
                rep = ae.assemble(spec, clip_dir, out_mp4, work_dir)
                qc = measure_qc(out_mp4)
                if ch_key in ("phim-ma-dan-gian", "kiem-hiep-co-trang") and qc["duration_s"] < 240.0:
                    raise RuntimeError(f"CHẶN PHIM NGẮN: {slug} chỉ dài {qc['duration_s']}s (< 240s tối thiểu cho phim cốt truyện!)")
                staged = stage_to_fb(cid, prefix, slug, final_dir)
                rec = {"channel": ch_key, "slug": slug, "fb_channel": cid, "voice": rep["voice"], "qc": qc, "staged": staged}
                (final_dir / "qc_report_v2.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
                rendered.append(rec)
                print(f"  OK {slug} -> {cid}/02_MOI_RENDER_CHO_XAC_NHAN | {qc['duration_s']}s {qc['res']} {qc['lufs']} LUFS", flush=True)
            except Exception as e:
                errors.append({"channel": ch_key, "slug": slug, "err": str(e)[:300]})
                print(f"  ERR {slug}: {e}", flush=True)

    print(json.dumps({
        "newly_rendered": len(rendered),
        "already_done": skipped,
        "errors": errors,
        "rendered": rendered,
    }, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
