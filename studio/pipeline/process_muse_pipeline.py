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
    remote = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, '/opt/agentnet-corner')
from research_queue import ResearchQueue
rq = ResearchQueue(Path('/opt/agentnet-corner'))
res = rq.get({'id': 'chief-local', 'role': 'controller'}, '/tasks')
data = res[1] if isinstance(res, tuple) and len(res) >= 2 else res
if isinstance(data, (bytes, str)):
    data = json.loads(data)
rows = [r for r in (data.get('tasks', []) if isinstance(data, dict) else data) if r.get('kind') in ('muse_draw_images', 'muse_make_videos', 'muse_write_script', 'muse_fix_script', 'muse_qa_score')]
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
from research_queue import ResearchQueue
tasks = json.loads(base64.b64decode({b64!r}).decode('utf-8'))
rq = ResearchQueue(Path('/opt/agentnet-corner'))
node = {{'id': 'chief-local', 'role': 'controller'}}
res = [rq.post(node, '/tasks', s, False) for s in tasks]
print(len(res))
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


def verify_mp4(p: Path) -> dict | None:
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
            sc = int(item.get("scene") or 0)
            url = (item.get("url") or "").strip()
            if sc >= 1 and url.startswith("http"):
                dst = img_dir / f"scene_{sc:02d}.jpg"
                if not dst.is_file() or dst.stat().st_size < 4096:
                    download_file(url, dst)
        for item in ((parsed or {}).get("videos") or []):
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
        chunk_sz = 9 if n_scenes >= 32 else n_scenes
        acts = [list(range(s, min(s + chunk_sz, n_scenes + 1))) for s in range(1, n_scenes + 1, chunk_sz)]

        for act_idx, sc_ids in enumerate(acts, 1):
            have_act_imgs = all((img_dir / f"scene_{sid:02d}.jpg").is_file() for sid in sc_ids)
            if not have_act_imgs:
                continue
            missing = [sid for sid in sc_ids if not verify_mp4(clip_dir / f"scene_{sid:02d}.mp4")]
            if not missing:
                continue
            dedup = (
                f"musevid-act{act_idx}-{ch_key}-{slug}"
                if len(acts) > 1
                else f"musevid-20261126-{ch_key}-{slug}"
            )
            if dedup in existing_vid_dedups:
                continue
            act_label = f"HỒI {act_idx}/{len(acts)} (cảnh {sc_ids[0]:02d}..{sc_ids[-1]:02d})" if len(acts) > 1 else f"cảnh 01..{n_scenes:02d}"
            sc_hint = ", ".join(f"scene_{sid:02d}.jpg" for sid in missing)
            zip_glob = " ".join(f"scene_{sid:02d}.mp4" for sid in missing)
            croc_step = (
                f"BƯỚC 4 (ĐẨY THẲNG TỪ UBUNTU QUA CẦU CROC VỀ Ổ E: — KHÔNG DÙNG BROWSER UPLOAD, KHÔNG HỎI XÁC NHẬN): Trong Ubuntu chạy ngay: "
                f"zip -j /tmp/{slug}_act{act_idx}.zip {zip_glob} && curl -fsSL -X POST \"https://muse.alltool.pro/media-upload?token={inv_tok}&slug={slug}&json=1\" -F \"file=@/tmp/{slug}_act{act_idx}.zip\" "
                f"(tự chuyển thẳng qua croc về ổ E: trong 2 giây!). "
            ) if inv_tok else (
                f"BƯỚC 4: Nén các clip .mp4 thành .zip rồi upload tại https://muse.alltool.pro/media-upload?slug={slug}. "
            )
            criteria = (
                f"VAI TRÒ: MUSE TẠO CLIP VIDEO (Image-to-Video) cho {act_label} tập '{title}' (kênh {series}, mã {slug}). "
                f"BƯỚC 1: Đọc kịch bản tại {spec_url} để xem chuyển động của {act_label}. "
                f"BƯỚC 2: Tải đúng {len(missing)} ảnh 9:16 của Hồi này từ kho riêng: https://muse.alltool.pro/media/{slug}/ ({sc_hint}). "
                f"BƯỚC 3: Dùng công cụ TẠO VIDEO TỪ ẢNH (Image-to-Video) của chính Muse biến {len(missing)} ảnh đó thành {len(missing)} clip video dọc 9:16 (đặt tên đúng scene_{missing[0]:02d}.mp4 .. scene_{missing[-1]:02d}.mp4, 5s/clip, chuyển động điện ảnh mượt mà, KHÔNG biến dạng mặt/tay, KHÔNG chữ/watermark). "
                f"{croc_step}"
                f"BƯỚC 5 (NỘP): Dán JSON hợp lệ trong summary: {{\"channel\":\"{ch_key}\",\"slug\":\"{slug}\",\"act\":{act_idx},\"delivery\":\"croc_E\"}}. Nếu hết hạn mức video, chọn outcome=BLOCKED!"
            )
            new_vid_tasks.append({
                "dedup": dedup,
                "assigned_to": "animator",
                "kind": "muse_make_videos",
                "payload": {
                    "objective": f"[{slug}] {act_label} — TẠO {len(missing)} CLIP 9:16: '{title}' ({series})",
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
