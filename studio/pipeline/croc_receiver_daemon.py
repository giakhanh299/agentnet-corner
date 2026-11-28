"""Luồng nhận file trực tiếp P2P qua croc từ Ubuntu của Muse thẳng về ổ E:\\MUSE_MEDIA_STUDIO.

- Poll https://muse.alltool.pro/croc-offers mỗi 2.5 giây (nhận đồng thời tối đa 4 luồng song song).
- Gọi D:\\02_CONG_CU\\croc\\croc.exe kéo thẳng file .zip / .mp4 / .jpg về E:\\MUSE_MEDIA_STUDIO\\<kênh>\\<slug>\\.
- Với bộ ảnh (01_muse_images), tự đồng bộ bản .jpg nhẹ (~180KB) lên /var/lib/agentnet-media/<slug>/ để Muse làm bước tạo video sau đó có link ảnh đầu vào; còn file video .mp4 nặng đi thẳng 100% về ổ E: không tốn 1 byte ổ cứng VPS!
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import process_muse_pipeline as pm  # noqa: E402

CROC_EXE = Path(r"D:\02_CONG_CU\croc\croc.exe")
MEDIA_ROOT = Path(r"E:\MUSE_MEDIA_STUDIO")
LOG_FILE = MEDIA_ROOT / "croc_receiver.log"
PID_FILE = MEDIA_ROOT / "croc_receiver.pid"
HUB_BASE = "https://muse.alltool.pro"


def log(msg: str) -> None:
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_invite_token() -> str:
    p = Path(os.environ["LOCALAPPDATA"]) / "MuseLoginHelper" / "hub_invite.txt"
    return p.read_text(encoding="utf-8").strip()


def hub_json(method: str, path: str, token: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        f"{HUB_BASE}{path}",
        data=data,
        headers={
            "X-Invite-Token": token,
            "Content-Type": "application/json",
            "User-Agent": "AgentNet-CrocReceiver/1.0",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def _canonical_channel(slug: str, fallback: str) -> str:
    low = slug.lower()
    if low.startswith("kh"):
        return "kiem-hiep-co-trang"
    if low.startswith("ep"):
        return "phim-ma-dan-gian"
    if low.startswith("k1_"):
        return "tien-va-doi-srt"
    if low.startswith("v0"):
        return "tap-lam-content"
    return fallback


def ingest_received_files(slug: str, src_dir: Path) -> tuple[int, int]:
    found = pm.find_spec(slug)
    ch_key = _canonical_channel(slug, found[0] if found else "misc")
    ep_dir = MEDIA_ROOT / ch_key / slug
    img_dir = ep_dir / "01_muse_images"
    clip_dir = ep_dir / "02_muse_clips"
    img_dir.mkdir(parents=True, exist_ok=True)
    clip_dir.mkdir(parents=True, exist_ok=True)

    # Extract any zip archives inside src_dir first
    for zp in list(src_dir.rglob("*.zip")):
        try:
            with zipfile.ZipFile(zp, "r") as zf:
                zf.extractall(src_dir / f"_unz_{zp.stem}")
        except Exception as e:
            log(f"WARN zip extract {zp.name}: {e}")
        zp.unlink(missing_ok=True)

    imgs_saved: list[Path] = []
    clips_saved = 0
    for f in sorted(src_dir.rglob("*")):
        if not f.is_file():
            continue
        low = f.name.lower()
        if low == "episode.json":
            try:
                spec_obj = json.loads(f.read_text(encoding="utf-8"))
                ch_hint = _canonical_channel(slug, str(spec_obj.get("channel") or ch_key))
                if ch_hint in ("phim-ma-dan-gian", "kiem-hiep-co-trang", "tien-va-doi-srt", "tap-lam-content"):
                    ch_key = ch_hint
                    ep_dir = MEDIA_ROOT / ch_key / slug
                    ep_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, ep_dir / "episode.json")
                if ch_key == "tap-lam-content":
                    repo_ep = pm.REPO_K08 / slug / "episode.json"
                else:
                    repo_ep = pm.REPO_MA / (ch_key if ch_key != "misc" else "phim-ma-dan-gian") / slug / "episode.json"
                repo_ep.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, repo_ep)
                log(f"NEW_SCRIPT_INGESTED slug={slug} ch={ch_key} -> kích hoạt tự động chia 4 Hồi vẽ ảnh!")
                subprocess.Popen(
                    [sys.executable, str(HERE / "auto_refill_100_pipeline.py")],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                log(f"WARN ingest episode.json for {slug}: {e}")
            continue
        m_sc = re.search(r"(?:scene[_-]?|clip[_-]?|s)(\d{1,2})", low)
        sc = int(m_sc.group(1)) if m_sc else 0
        if sc < 1:
            continue
        if low.endswith((".mp4", ".mov", ".webm")):
            dst = clip_dir / f"scene_{sc:02d}.mp4"
            shutil.copy2(f, dst)
            if pm.verify_mp4(dst):
                clips_saved += 1
            else:
                log(f"REJECT_FAKE_ZOOMPAN_OR_INVALID slug={slug} file={dst.name} -> đã xóa (chỉ chấp nhận video AI có chuyển động thật!)")
                dst.unlink(missing_ok=True)
        elif low.endswith((".jpg", ".jpeg", ".png", ".webp")):
            dst = img_dir / f"scene_{sc:02d}.jpg"
            try:
                with Image.open(f) as im:
                    im.convert("RGB").save(dst, "JPEG", quality=92)
                imgs_saved.append(dst)
            except Exception:
                pass

    # If images arrived via croc and <11 clips exist yet, mirror light .jpgs to VPS so video Muses have source URLs
    local_clips = [p for p in clip_dir.glob("scene_*.mp4") if pm.verify_mp4(p)]
    if imgs_saved and len(local_clips) < 11:
        try:
            ssh = pm.connect_vps_ssh(timeout=20)
            try:
                ssh.exec_command(f"mkdir -p /var/lib/agentnet-media/{slug}")[1].read()
                sftp = ssh.open_sftp()
                for jp in imgs_saved:
                    # Nén nhẹ bản gương trên VPS về 720x1280 (~70KB) để giữ >4.3GB trống VPS (bản gốc 1152x2048 giữ nguyên trên ổ E:)
                    tmp_vps = jp.with_suffix(".vps_mirror.jpg")
                    try:
                        with Image.open(jp) as im:
                            im = im.convert("RGB")
                            if im.width > 720 or im.height > 1280:
                                im.thumbnail((720, 1280), Image.Resampling.LANCZOS)
                            im.save(tmp_vps, "JPEG", quality=80, optimize=True)
                        sftp.put(str(tmp_vps), f"/var/lib/agentnet-media/{slug}/{jp.name}")
                    finally:
                        tmp_vps.unlink(missing_ok=True)
                sftp.close()
                ssh.exec_command(f"chown -R agentnet-corner:agentnet-corner /var/lib/agentnet-media/{slug}")[1].read()
            finally:
                ssh.close()
        except Exception as e:
            log(f"WARN mirror light jpgs for {slug}: {e}")

    return len(imgs_saved), clips_saved


def handle_offer(offer: dict, token: str) -> None:
    oid = offer["id"]
    slug = offer["slug"]
    code = offer["croc_code"]
    log(f"Bắt đầu nhận croc offer={oid} slug={slug} -> E:\\MUSE_MEDIA_STUDIO...")
    status = "FAILED"
    try:
        with tempfile.TemporaryDirectory(dir=str(MEDIA_ROOT)) as td:
            env = os.environ.copy()
            env["CROC_SECRET"] = code
            td_path = Path(td)
            for attempt in range(3):
                proc = subprocess.run(
                    [str(CROC_EXE), "--yes", "--overwrite"],
                    cwd=td, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90,
                )
                if any(td_path.iterdir()):
                    break
                time.sleep(1.8)
            if proc.returncode == 0 and any(td_path.iterdir()):
                n_img, n_clip = ingest_received_files(slug, td_path)
                log(f"NHẬN CROC THÀNH CÔNG slug={slug}: +{n_img} ảnh, +{n_clip} clip .mp4 thẳng vào ổ E:!")
                status = "DONE"
            else:
                log(f"ERR croc rc={proc.returncode} slug={slug}: {(proc.stderr or proc.stdout)[-240:]}")
    except Exception as e:
        log(f"ERR handle_offer {slug}: {e}")
    finally:
        try:
            hub_json("POST", "/croc-ack", token, {"id": oid, "status": status})
        except Exception:
            pass


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True)
    return str(pid) in out.stdout


def main() -> int:
    if not CROC_EXE.is_file():
        raise FileNotFoundError(f"Chưa cài croc.exe tại {CROC_EXE}")
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    if PID_FILE.is_file():
        try:
            old = int(PID_FILE.read_text(encoding="utf-8").strip())
            if old != os.getpid() and pid_alive(old):
                log(f"Đã có croc_receiver_daemon đang chạy (PID={old}), thoát bản trùng.")
                return 0
        except Exception:
            pass
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    log(f"Khởi động croc_receiver_daemon (PID={os.getpid()}) -> lắng nghe P2P thẳng về E:\\MUSE_MEDIA_STUDIO")

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    try:
        while True:
            try:
                tok = get_invite_token()
                res = hub_json("GET", "/croc-offers", tok)
                for off in res.get("offers", []):
                    pool.submit(handle_offer, off, tok)
            except Exception as e:
                log(f"WARN poll croc-offers: {e}")
                time.sleep(5.0)
            time.sleep(2.5)
    finally:
        PID_FILE.unlink(missing_ok=True)
        pool.shutdown(wait=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
