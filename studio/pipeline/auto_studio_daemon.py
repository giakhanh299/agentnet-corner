"""Daemon chạy độc lập 24/7 trên máy Windows — KHÔNG cần AI hay API trả phí can thiệp.

Chu kỳ tự động (mặc định 15 phút/lần):
1. Kéo ảnh 1152x2048 & video .mp4 mới của 15 Muse từ VPS https://muse.alltool.pro về E:\\MUSE_MEDIA_STUDIO.
2. Tự dọn file nặng trên VPS 15GB (luôn giữ trống >4.5 GB) & tự đẩy task muse_make_videos khi đủ 11 ảnh.
3. Tự thu hồi các task bị treo >35 phút hoặc nộp thiếu clip (<11 clip .mp4).
4. Tự chạy hậu kỳ thuần trên PC (VieNeu TTS đa giọng + nhạc + SFX + phụ đề + Logo + Ảnh bìa, KHÔNG AIGC, KHÔNG đăng API) -> xuất vào 02_MOI_RENDER_CHO_XAC_NHAN.
5. Tự kiểm tra nếu trên Hub còn việc QUEUED mà số Muse đang chạy (RUNNING) <= 2 (cách tối thiểu 45 phút) thì tự đánh thức dàn Chrome Muse.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEDIA_ROOT = Path(r"E:\MUSE_MEDIA_STUDIO")
LOG_FILE = MEDIA_ROOT / "daemon.log"
HEARTBEAT_FILE = MEDIA_ROOT / "daemon_heartbeat.json"
PID_FILE = MEDIA_ROOT / "auto_studio_daemon.pid"


def log(msg: str) -> None:
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True)
    return str(pid) in out.stdout


def acquire_single_instance() -> bool:
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    if PID_FILE.is_file():
        try:
            old_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            if old_pid != os.getpid() and pid_alive(old_pid):
                log(f"Đã có auto_studio_daemon đang chạy (PID={old_pid}), thoát bản trùng.")
                return False
        except Exception:
            pass
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    return True


def run_step(script_name: str, timeout_s: int = 1800) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(HERE / script_name)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout_s,
    )
    tail = "\n".join((proc.stdout or "").strip().splitlines()[-8:])
    if proc.returncode != 0:
        err_tail = "\n".join((proc.stderr or "").strip().splitlines()[-6:])
        log(f"WARN {script_name} rc={proc.returncode}: {err_tail}")
    return proc.returncode, tail


def check_hub_activity() -> tuple[int, int]:
    sys.path.insert(0, str(HERE))
    import process_muse_pipeline as pm
    tasks = pm.fetch_hub_tasks()
    queued = sum(1 for t in tasks if t.get("status") == "QUEUED")
    running = sum(1 for t in tasks if t.get("status") == "RUNNING")
    return queued, running


def main() -> int:
    ap = argparse.ArgumentParser(description="Daemon tự động kéo video Muse & hậu kỳ 24/7 không cần AI")
    ap.add_argument("--interval-min", type=float, default=15.0)
    ap.add_argument("--nudge-cooldown-min", type=float, default=45.0)
    ap.add_argument("--initial-delay-min", type=float, default=0.0)
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()

    if not acquire_single_instance():
        return 0

    last_nudge_ts = 0.0
    tick = 0
    log(f"Khởi động auto_studio_daemon (PID={os.getpid()}, interval={args.interval_min}m)")
    if args.initial_delay_min > 0:
        log(f"Đợi khởi động {args.initial_delay_min} phút để tiến trình render hiện tại hoàn tất...")
        time.sleep(args.initial_delay_min * 60.0)

    try:
        while True:
            tick += 1
            t0 = time.time()
            log(f"--- Chu kỳ #{tick} bắt đầu ---")
            try:
                run_step("process_muse_pipeline.py", timeout_s=600)
                run_step("requeue_stalled_and_partial.py", timeout_s=180)
                run_step("prioritize_hub.py", timeout_s=120)
                _, post_tail = run_step("postprod_muse_videos.py", timeout_s=3600)
                queued, running = check_hub_activity()
                log(f"Hub hiện tại: QUEUED={queued}, RUNNING={running}")

                nudged = False
                if queued > 0 and running <= 4 and (time.time() - last_nudge_ts) >= args.nudge_cooldown_min * 60:
                    log("Số Muse đang chạy thấp trong khi còn việc QUEUED -> đánh thức dàn 15 Muse...")
                    run_step("nudge_muses.py", timeout_s=900)
                    last_nudge_ts = time.time()
                    nudged = True

                HEARTBEAT_FILE.write_text(json.dumps({
                    "updated_at": datetime.now().isoformat(),
                    "pid": os.getpid(),
                    "tick": tick,
                    "hub_queued": queued,
                    "hub_running": running,
                    "nudged_this_tick": nudged,
                    "last_postprod_tail": post_tail,
                }, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception as e:
                log(f"ERROR trong chu kỳ #{tick}: {e}\n{traceback.format_exc()[-500:]}")

            if args.once:
                break
            elapsed = time.time() - t0
            sleep_s = max(60.0, args.interval_min * 60.0 - elapsed)
            log(f"--- Chu kỳ #{tick} xong ({elapsed:.1f}s). Ngủ {sleep_s/60:.1f} phút ---")
            time.sleep(sleep_s)
    finally:
        PID_FILE.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
