"""Harvest Muse-drawn images & Muse-generated .mp4 video clips from Hub + VPS dropbox -> E:\\MUSE_MEDIA_STUDIO.

- Stores all raw Muse images, Muse .mp4 clips, storyboards, and final renders on E:\\MUSE_MEDIA_STUDIO (1.3 TB free).
- Automatically compresses/cleans heavy .png/.webp/.mp4 from VPS /var/lib/agentnet-media so the 15 GB VPS never fills up.
- Never uses local GPU to draw video scenes (only approved for optional 1-frame cover background + post-production).
"""
import base64
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from PIL import Image

sys.path.insert(0, r"D:\0.1_FACE_BOOK\macro-tool")
from vps_ssh_helper import connect_vps_ssh  # noqa: E402

MEDIA_ROOT = Path(r"E:\MUSE_MEDIA_STUDIO")
REPO_MA = Path(r"D:\AI_AGENT\agentnet-corner-phim-ma\channels")
REPO_K08 = Path(r"D:\AI_AGENT\agentnet-corner-k08\channels\tap-lam-content-k08\episodes")
RAW_MA = "https://raw.githubusercontent.com/giakhanh299/agentnet-corner/feat/phim-ma-dan-gian/channels"
RAW_K08 = "https://raw.githubusercontent.com/giakhanh299/agentnet-corner/feat/tap-lam-content/channels/tap-lam-content-k08/episodes"


def fetch_hub_tasks() -> list[dict]:
    """Query ALL muse_* tasks directly from Hub SQLite (no 200/400-row API truncation!)."""
    remote = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, '/opt/agentnet-corner')
from research_queue import ResearchQueue

def _parse_json(val):
    if isinstance(val, dict):
        return val
    if isinstance(val, str) and val.strip():
        try:
            return json.loads(val)
        except Exception:
            return val
    return {} if val is None else val

rq = ResearchQueue(Path('/opt/agentnet-corner'))
kinds = ('muse_draw_images', 'muse_make_videos', 'muse_write_script', 'muse_fix_script', 'muse_qa_score')
rows = []
with rq.db() as db:
    for r in db.execute(
        "SELECT id, dedup, project, assigned_to, kind, payload, status, created_at, started_at, completed_at, result, lease, lease_until, owner_node "
        "FROM tasks WHERE kind IN ('muse_draw_images', 'muse_make_videos', 'muse_write_script', 'muse_fix_script', 'muse_qa_score') "
        "ORDER BY created_at DESC"
    ).fetchall():
        d = dict(r)
        d['payload'] = _parse_json(d.get('payload'))
        d['result'] = _parse_json(d.get('result'))
        rows.append(d)
print(json.dumps(rows, ensure_ascii=False))
"""
    ssh = connect_vps_ssh(timeout=25)
    try:
        inp, o, _ = ssh.exec_command("python3 -")
        inp.write(remote)
        inp.flush()
        inp.channel.shutdown_write()
        out = o.read().decode("utf-8", "replace").strip()
        return json.loads(out) if out else []
    finally:
        ssh.close()


def enqueue_hub_tasks(tasks: list[dict]) -> int:
    if not tasks:
        return 0
    b64 = base64.b64encode(json.dumps(tasks, ensure_ascii=False).encode("utf-8")).decode("ascii")
    remote = f"""
import base64, json, sys
from pathlib import Path
sys.path.insert(0, '/opt/agentnet-corner')
from research_queue import QueueError, ResearchQueue
tasks = json.loads(base64.b64decode({b64!r}).decode('utf-8'))
rq = ResearchQueue(Path('/opt/agentnet-corner'))
node = {{'id': 'chief-local', 'role': 'controller'}}
added = 0
for s in tasks:
    try:
        rq.post(node, '/tasks', s, False)
        added += 1
    except QueueError:
        pass
print(added)
"""
    ssh = connect_vps_ssh(timeout=25)
    try:
        inp, o, e = ssh.exec_command("python3 -")
        inp.write(remote)
        inp.flush()
        inp.channel.shutdown_write()
        out = o.read().decode("utf-8", "replace").strip()
        er = e.read().decode("utf-8", "replace").strip()
        if er:
            print("ENQUEUE_ERR:", er, flush=True)
        return int(out) if out.isdigit() else 0
    finally:
        ssh.close()


def find_spec(slug: str) -> tuple[str, Path, str] | None:
    for ch in ("tien-va-doi-srt", "phim-ma-dan-gian", "kiem-hiep-co-trang"):
        p = REPO_MA / ch / slug / "episode.json"
        if p.is_file():
            return ch, p, f"{RAW_MA}/{ch}/{slug}/episode.json"
    p = REPO_K08 / slug / "episode.json"
    if p.is_file():
        return "tap-lam-content", p, f"{RAW_K08}/{slug}/episode.json"
    return None


def extract_json_block(summary) -> dict | None:
    if isinstance(summary, dict):
        return summary
    if not isinstance(summary, str):
        return None
    for m in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", summary, re.S):
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    start, end = summary.find("{"), summary.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(summary[start:end + 1])
        except Exception:
            pass
    return None


def download_file(url: str, dst: Path, timeout: int = 60) -> bool:
    try:
        jar = http.cookiejar.CookieJar()
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        with op.open(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
            ct = (r.headers.get("Content-Type") or "").lower()
            data = r.read()
        if "text/html" in ct and "tmpfiles.org" in url:
            html_s = data.decode("utf-8", "replace")
            m = re.search(r"https://tmpfiles\.org/dl/[^\x22\x27\s<>]+", html_s)
            if m:
                with op.open(urllib.request.Request(m.group(0), headers=headers), timeout=timeout) as r2:
                    data = r2.read()
        if len(data) < 4096:
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.suffix.lower() in (".jpg", ".jpeg"):
            tmp = dst.with_suffix(".raw")
            tmp.write_bytes(data)
            try:
                with Image.open(tmp) as im:
                    im.convert("RGB").save(dst, "JPEG", quality=92)
            finally:
                tmp.unlink(missing_ok=True)
        else:
            dst.write_bytes(data)
        return True
    except Exception:
        return False


def make_storyboard(img_paths: list[Path], out_path: Path) -> None:
    cols = 4
    rows = (len(img_paths) + cols - 1) // cols
    tw, th = 270, 480
    canvas = Image.new("RGB", (cols * tw, rows * th), (15, 15, 18))
    for i, p in enumerate(img_paths):
        im = Image.open(p).convert("RGB").resize((tw, th))
        canvas.paste(im, ((i % cols) * tw, (i // cols) * th))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=88)


def is_fake_zoompan_mp4(p: Path) -> tuple[bool, str]:
    """Phát hiện clip ăn gian bằng ffmpeg zoompan / Ken Burns (chỉ phóng to/dịch ảnh tĩnh, không có chuyển động AI thật)."""
    try:
        import cv2  # noqa: WPS433
        import numpy as np  # noqa: WPS433
    except Exception:
        return False, "no_cv2"
    cap = cv2.VideoCapture(str(p))
    try:
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if w <= 0 or h <= 0 or n < 10:
            return False, "short"
        idxs = [max(0, int(n * f)) for f in (0.15, 0.50, 0.85)]
        frames = []
        th = max(120, int(360 * h / max(w, 1)))
        for idx in idxs:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, fr = cap.read()
            if ok:
                frames.append(cv2.resize(fr, (360, th)))
    finally:
        cap.release()
    if len(frames) < 3:
        return False, "few_frames"
    orb = cv2.ORB_create(800)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    residuals: list[float] = []
    inliers: list[float] = []
    for a, b in ((frames[0], frames[1]), (frames[1], frames[2]), (frames[0], frames[2])):
        ga = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
        gb = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
        kp1, d1 = orb.detectAndCompute(ga, None)
        kp2, d2 = orb.detectAndCompute(gb, None)
        if d1 is None or d2 is None or len(kp1) < 12 or len(kp2) < 12:
            residuals.append(99.0)
            inliers.append(0.0)
            continue
        matches = sorted(bf.match(d1, d2), key=lambda m: m.distance)[:200]
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        M, mask = cv2.estimateAffinePartial2D(pts1, pts2, method=cv2.RANSAC, ransacReprojThreshold=2.5)
        if M is None or mask is None:
            residuals.append(99.0)
            inliers.append(0.0)
            continue
        inliers.append(float(mask.mean()))
        warped = cv2.warpAffine(ga, M, (gb.shape[1], gb.shape[0]))
        valid = cv2.warpAffine(np.ones_like(ga) * 255, M, (gb.shape[1], gb.shape[0])) > 200
        valid = cv2.erode(valid.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        if int(valid.sum()) < 1000:
            residuals.append(99.0)
        else:
            diff = np.abs(warped.astype(np.float32) - gb.astype(np.float32))[valid]
            residuals.append(float(np.percentile(diff, 90)))
    med_res = float(np.median(residuals))
    med_inl = float(np.median(inliers))
    is_fake = (med_inl > 0.85) or (med_res < 25.0 and med_inl > 0.72) or (med_res < 12.0)
    return is_fake, f"p90_res={med_res:.1f},inlier={med_inl:.2f}"


def is_mismatched_source_mp4(p: Path) -> tuple[bool, str]:
    """Phát hiện clip bị lẫn từ tập khác (cross-episode leak) bằng đối chiếu ảnh gốc 01_muse_images/scene_XX.jpg."""
    try:
        jpg = p.parent.parent / "01_muse_images" / f"{p.stem}.jpg"
        if not jpg.is_file():
            return False, "no_src_jpg"
        import cv2  # noqa: WPS433
        import numpy as np  # noqa: WPS433
        src = cv2.imread(str(jpg))
        if src is None:
            return False, "unreadable_jpg"
        a = cv2.resize(src, (64, 112)).astype(np.float32).ravel()
        a -= a.mean()
        na = float(np.linalg.norm(a))
        if na <= 1e-6:
            return False, "flat_jpg"
        cap = cv2.VideoCapture(str(p))
        best = -1.0
        try:
            for fi in (0, 5, 15):
                cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
                ok, fr = cap.read()
                if not ok or fr is None:
                    continue
                b = cv2.resize(fr, (64, 112)).astype(np.float32).ravel()
                b -= b.mean()
                nb = float(np.linalg.norm(b))
                if nb > 1e-6:
                    best = max(best, float(np.dot(a, b) / (na * nb)))
        finally:
            cap.release()
        if best < -0.5:
            return False, "no_frames"
        return best < 0.25, f"src_corr={best:.3f}"
    except Exception:
        return False, "err"


def verify_mp4(p: Path, check_motion: bool = True) -> dict | None:
    if not p.is_file() or p.stat().st_size < 16384:
        return None
    pr = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate:format=duration",
         "-of", "json", str(p)],
        capture_output=True, text=True,
    )
    if pr.returncode != 0:
        return None
    try:
        info = json.loads(pr.stdout or "{}")
        st = (info.get("streams") or [{}])[0]
        dur = float((info.get("format") or {}).get("duration") or 0)
        if int(st.get("width") or 0) >= 300 and dur >= 1.0:
            if check_motion:
                fake, detail = is_fake_zoompan_mp4(p)
                if fake:
                    print(f"REJECT_FAKE_ZOOMPAN {p.name}: {detail}", flush=True)
                    return None
                mismatched, mdetail = is_mismatched_source_mp4(p)
                if mismatched:
                    print(f"REJECT_WRONG_EPISODE_CLIP {p.name}: {mdetail}", flush=True)
                    return None
            return {"w": st.get("width"), "h": st.get("height"), "dur": round(dur, 2)}
    except Exception:
        pass
    return None


def sync_vps_media_to_E() -> dict:
    """Pull all files uploaded to /var/lib/agentnet-media/<slug>/ into E:\\MUSE_MEDIA_STUDIO,
    replace heavy .png/.webp on VPS with light .jpg (~200KB), and remove .mp4 from VPS after verified on E:."""
    ssh = connect_vps_ssh(timeout=30)
    pulled = {}
    cleaned_mb = 0.0
    try:
        _, o, _ = ssh.exec_command("find /var/lib/agentnet-media -maxdepth 2 -type f -printf '%P\\t%s\\n' 2>/dev/null")
        lines = [ln.strip() for ln in o.read().decode("utf-8", "replace").splitlines() if "\t" in ln]
        sftp = ssh.open_sftp()
        by_slug: dict[str, list[tuple[str, int]]] = {}
        for ln in lines:
            rel, sz = ln.rsplit("\t", 1)
            if "/" not in rel:
                continue
            slug, fname = rel.split("/", 1)
            by_slug.setdefault(slug, []).append((fname, int(sz)))

        for slug, flist in sorted(by_slug.items()):
            found = find_spec(slug)
            if not found:
                continue
            ch_key, _, _ = found
            ep_dir = MEDIA_ROOT / ch_key / slug
            img_dir = ep_dir / "01_muse_images"
            clip_dir = ep_dir / "02_muse_clips"
            img_dir.mkdir(parents=True, exist_ok=True)
            clip_dir.mkdir(parents=True, exist_ok=True)

            imgs_pulled, clips_pulled = 0, 0
            # Sort so .jpg processed before .png/.webp, and .mp4 pulled directly
            for fname, sz in sorted(flist):
                remote_path = f"/var/lib/agentnet-media/{slug}/{fname}"
                low = fname.lower()
                m_sc = re.search(r"(?:scene[_-]?|s)(\d{1,2})", low)
                sc = int(m_sc.group(1)) if m_sc else 0
                if low.endswith(".mp4") and sc >= 1:
                    dst = clip_dir / f"scene_{sc:02d}.mp4"
                    if not verify_mp4(dst):
                        sftp.get(remote_path, str(dst))
                    if verify_mp4(dst):
                        clips_pulled += 1
                        # Free heavy .mp4 from 15GB VPS immediately once verified on E:!
                        try:
                            sftp.remove(remote_path)
                            cleaned_mb += sz / (1024 * 1024)
                        except Exception:
                            pass
                elif low.endswith((".jpg", ".jpeg", ".png", ".webp")) and sc >= 1:
                    dst = img_dir / f"scene_{sc:02d}.jpg"
                    if not dst.is_file() or dst.stat().st_size < 4096:
                        raw_tmp = img_dir / f"_tmp_{fname}"
                        sftp.get(remote_path, str(raw_tmp))
                        try:
                            with Image.open(raw_tmp) as im:
                                im.convert("RGB").save(dst, "JPEG", quality=92)
                            imgs_pulled += 1
                        finally:
                            raw_tmp.unlink(missing_ok=True)
                    else:
                        imgs_pulled += 1
                    # If VPS has heavy .png or .webp (>500KB), replace with light .jpg (~200KB) on VPS to save 15GB disk!
                    if low.endswith((".png", ".webp")) and dst.is_file():
                        jpg_remote = f"/var/lib/agentnet-media/{slug}/scene_{sc:02d}.jpg"
                        if not any(f == f"scene_{sc:02d}.jpg" for f, _ in flist):
                            sftp.put(str(dst), jpg_remote)
                        try:
                            sftp.remove(remote_path)
                            cleaned_mb += sz / (1024 * 1024)
                        except Exception:
                            pass

            # Build storyboard if we have >=8 images locally
            local_imgs = sorted(img_dir.glob("scene_*.jpg"))
            if len(local_imgs) >= 8 and not (ep_dir / "storyboard_muse.jpg").is_file():
                make_storyboard(local_imgs, ep_dir / "storyboard_muse.jpg")

            # Delete scene_* clips/images once ALL expected clips (e.g. 36 for movies, 11 for Reels) are on E:
            local_clips = [p for p in sorted(clip_dir.glob("scene_*.mp4")) if verify_mp4(p)]
            n_exp_clean = 11
            if found:
                try:
                    n_exp_clean = len(json.loads(found[1].read_text(encoding="utf-8")).get("scenes", [])) or 11
                except Exception:
                    n_exp_clean = 11
            if len(local_clips) >= n_exp_clean:
                if (ep_dir / "03_final_v2" / "qa_scorecard.json").is_file():
                    _, o2, _ = ssh.exec_command(f"rm -rf /var/lib/agentnet-media/{slug}")
                else:
                    _, o2, _ = ssh.exec_command(f"rm -f /var/lib/agentnet-media/{slug}/scene_*")
                o2.read()

            pulled[slug] = {
                "channel": ch_key,
                "local_imgs": len(local_imgs),
                "local_clips": len(local_clips),
            }
        sftp.close()
        _, o3, _ = ssh.exec_command("chown -R agentnet-corner:agentnet-corner /var/lib/agentnet-media 2>/dev/null; df -h / | tail -n 1")
        df_line = o3.read().decode("utf-8", "replace").strip()
    finally:
        ssh.close()
    return {"synced_slugs": pulled, "vps_cleaned_mb": round(cleaned_mb, 1), "vps_df": df_line}


def main():
    vps_sync = sync_vps_media_to_E()
    tasks = fetch_hub_tasks()
    draw_done = [t for t in tasks if t.get("kind") == "muse_draw_images" and t.get("status") == "SUBMITTED"]
    vid_tasks = [t for t in tasks if t.get("kind") == "muse_make_videos"]
    existing_vid_dedups = {t.get("dedup") for t in vid_tasks}

    new_vid_tasks = []
    ready_for_postprod = []

    # Check SUBMITTED draw tasks, VPS-synced slugs, AND any slug landed directly on E: via croc!
    candidate_slugs = set(vps_sync["synced_slugs"].keys())
    for ch_dir in MEDIA_ROOT.iterdir() if MEDIA_ROOT.is_dir() else []:
        if ch_dir.is_dir():
            for ep_d in ch_dir.iterdir():
                if ep_d.is_dir() and ((ep_d / "01_muse_images").is_dir() or (ep_d / "02_muse_clips").is_dir()):
                    candidate_slugs.add(ep_d.name)
    inv_path = Path(os.environ.get("LOCALAPPDATA", "")) / "MuseLoginHelper" / "hub_invite.txt"
    inv_tok = inv_path.read_text(encoding="utf-8").strip() if inv_path.is_file() else ""
    for t in draw_done:
        res = t.get("result") or {}
        obj_txt = (t.get("payload") or {}).get("objective", "")
        m = re.match(r"\[([a-z0-9_]+)\]", obj_txt)
        parsed = extract_json_block(res.get("summary", ""))
        slug = (parsed or {}).get("slug") or (m.group(1) if m else None)
        if not slug:
            continue
        candidate_slugs.add(slug)
        found = find_spec(slug)
        if not found:
            continue
        ch_key, _, _ = found
        ep_dir = MEDIA_ROOT / ch_key / slug
        img_dir = ep_dir / "01_muse_images"
        clip_dir = ep_dir / "02_muse_clips"
        # Download any external URLs (e.g. tmpfiles.org) if not already on E:
        for item in ((parsed or {}).get("images") or []):
            if not isinstance(item, dict):
                continue
            sc = int(item.get("scene") or 0)
            url = (item.get("url") or "").strip()
            if sc >= 1 and url.startswith("http"):
                dst = img_dir / f"scene_{sc:02d}.jpg"
                if not dst.is_file() or dst.stat().st_size < 4096:
                    download_file(url, dst)
        for item in ((parsed or {}).get("videos") or []):
            if not isinstance(item, dict):
                continue
            sc = int(item.get("scene") or 0)
            url = (item.get("url") or "").strip()
            if sc >= 1 and url.startswith("http"):
                dst = clip_dir / f"scene_{sc:02d}.mp4"
                if not verify_mp4(dst):
                    download_file(url, dst, timeout=90)

    # Enqueue muse_make_videos (in 9-10 scene Acts for 36-40 scene movies, or single batch for 11-scene Reels!)
    for slug in sorted(candidate_slugs):
        found = find_spec(slug)
        if not found:
            continue
        ch_key, spec_path, spec_url = found
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        n_scenes = len(spec.get("scenes", [])) or 11
        # Skip retired short (<32 scene) specs on movie channels so Muses focus 100% on 4-Act (36-40 scene) movies!
        if ch_key in ("phim-ma-dan-gian", "kiem-hiep-co-trang") and n_scenes < 32:
            continue
        ep_dir = MEDIA_ROOT / ch_key / slug
        img_dir = ep_dir / "01_muse_images"
        clip_dir = ep_dir / "02_muse_clips"
        local_imgs = sorted(img_dir.glob("scene_*.jpg"))
        local_clips = [
            clip_dir / f"scene_{sid:02d}.mp4"
            for sid in range(1, n_scenes + 1)
            if verify_mp4(clip_dir / f"scene_{sid:02d}.mp4")
        ]

        if len(local_imgs) >= min(n_scenes, 10) and not (ep_dir / "storyboard_muse.jpg").is_file():
            make_storyboard(local_imgs[:16], ep_dir / "storyboard_muse.jpg")

        if len(local_clips) >= n_scenes:
            ready_for_postprod.append({"channel": ch_key, "slug": slug, "clips": len(local_clips), "expected": n_scenes})
            continue

        title = spec.get("title", slug)
        series = spec.get("series", ch_key)
        # QUAN TRỌNG: Giới hạn đúng 6 clip/lô vì Muse chỉ cho tạo tối đa 6 video AI thật mỗi lượt chat!
        missing_all = [
            sid for sid in range(1, n_scenes + 1)
            if (img_dir / f"scene_{sid:02d}.jpg").is_file() and not verify_mp4(clip_dir / f"scene_{sid:02d}.mp4")
        ]
        if not missing_all:
            continue
        batches = [missing_all[i:i + 6] for i in range(0, len(missing_all), 6)]
        # Dùng trực tiếp URL trên alltool.pro (luôn có sẵn, không bao giờ dính 404 GitHub!)
        vps_spec_url = f"https://muse.alltool.pro/media/{slug}/episode.json"

        for b_idx, sc_ids in enumerate(batches, 1):
            dedup = f"musevid6-s{sc_ids[0]:02d}_{sc_ids[-1]:02d}-{slug}"
            if dedup in existing_vid_dedups:
                continue
            act_label = f"Batch {b_idx}/{len(batches)} (scenes {sc_ids[0]:02d}-{sc_ids[-1]:02d})"
            sc_hint = ", ".join(f"scene_{sid:02d}.jpg" for sid in sc_ids)
            out_hint = ", ".join(f"scene_{sid:02d}.mp4" for sid in sc_ids)
            criteria = (
                f"Animation brief for {act_label} of '{title}' ({series}, slug={slug}). "
                f"Reference storyboard JSON: {vps_spec_url} . "
                f"Source frames directory: https://muse.alltool.pro/media/{slug}/ ({sc_hint}). "
                f"Use genuine AI Image-to-Video generation to produce EXACTLY {len(sc_ids)} vertical 9:16 video clips ({out_hint}) "
                f"with real living character, fabric, water, fire, and atmospheric motion (NEVER static image zoompan or Ken Burns slideshows). "
                f"Keep clips clean without text or watermarks, deliver via your studio upload workflow, submit JSON on /portal, then STOP (do not claim a second batch in the same chat turn)."
            )
            new_vid_tasks.append({
                "dedup": dedup,
                "assigned_to": "animator",
                "kind": "muse_make_videos",
                "payload": {
                    "objective": f"[{slug}] {act_label} — Animate {len(sc_ids)} real AI clips ({sc_ids[0]:02d}-{sc_ids[-1]:02d}) for '{title}'",
                    "acceptance_criteria": criteria,
                },
            })

    enqueued = enqueue_hub_tasks(new_vid_tasks)
    print(json.dumps({
        "media_root": str(MEDIA_ROOT),
        "vps_sync": vps_sync,
        "draw_submitted_on_hub": len(draw_done),
        "enqueued_muse_make_videos": enqueued,
        "ready_for_postprod": ready_for_postprod,
    }, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
