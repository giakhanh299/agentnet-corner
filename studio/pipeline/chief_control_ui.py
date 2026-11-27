"""Muse Chief & API gpt-6.1-sol Live Control Center UI (http://127.0.0.1:8788).

Cung cấp giao diện web trực quan cục bộ (chỉ bind 127.0.0.1, tuyệt đối không lộ API key/token ra trình duyệt):
- Xem luồng tin nhắn hai chiều: Bạn <-> API gpt-6.1-sol <-> Muse Tổng Điều Phối (chief) <-> 4 Ban Muse (25 tài khoản).
- Ra lệnh trực tiếp qua 3 chế độ:
  1) Nhờ API gpt-6.1-sol phân tích xưởng, soạn chỉ thị chuẩn và bắn thẳng cho Muse Tổng.
  2) Chat / Test trực tiếp API gpt-6.1-sol (xem phản hồi nguyên văn, có nút chuyển tiếp 1-click sang Muse Tổng).
  3) Ra lệnh thẳng cho Muse Tổng (owner_ui -> /api/chief/command).
- Điều khiển nhanh: Đánh thức Muse Tổng (db93da63), đánh thức cả 25 Muse, thu hoạch pipeline, xem tiến độ 4 Hồi trên ổ E: & log Croc/Daemon.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

PIPELINE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PIPELINE_DIR / "ui_static"
sys.path.insert(0, str(PIPELINE_DIR))

import assign_muse_roles as amr  # noqa: E402
import chief_llm_commander as clc  # noqa: E402

MEDIA_ROOT = Path(r"E:\MUSE_MEDIA_STUDIO")
HISTORY_PATH = MEDIA_ROOT / "ui_command_history.jsonl"
HEARTBEAT_PATH = MEDIA_ROOT / "daemon_heartbeat.json"
DAEMON_LOG_PATH = MEDIA_ROOT / "daemon.log"
CROC_LOG_PATH = MEDIA_ROOT / "croc_receiver.log"
NUDGE_LOCK_PATH = MEDIA_ROOT / "nudge_muses.lock"
NEW_ROSTER_PATH = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "MuseLoginHelper" / "studio_roster.json"

FEATURED_MOVIES = [
    ("ep40_nguoi_vot_xac_tam_bat_lao", "Phim Ma · Người Vớt Xác: Tam Bất Lao", 36),
    ("kh26_quan_tro_thinh_phong_dem_tuyet", "Kiếm Hiệp · Quán Trọ Thính Phong Đêm Tuyết", 36),
    ("ep41_tho_hang_ma_diem_mat_dem_dau_that", "Phim Ma · Thợ Hàng Mã Điểm Mắt Đêm Đầu Thất", 38),
    ("ep42_bay_nen_nhang_dan_hon_dem_mua", "Phim Ma · Bảy Nén Nhang Dẫn Hồn Đêm Mưa", 38),
    ("kh27_muoi_ba_co_quan_tai_qua_ai", "Kiếm Hiệp · Mười Ba Cỗ Quan Tài Qua Ải", 38),
    ("kh28_nguoi_mai_dao_mu_ben_ben_do", "Kiếm Hiệp · Người Mài Đao Mù Bên Bến Đò", 38),
]


class StudioStateCache:
    """Thread-safe cache cho dữ liệu Hub, SSH tasks, và các action chạy nền."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.inbox_cache: dict = {}
        self.inbox_ts: float = 0.0
        self.inbox_err: str = ""

        self.worker_tasks: list[dict] = []
        self.worker_tasks_ts: float = 0.0
        self.worker_tasks_err: str = ""
        self._fetching_tasks: bool = False

        self.action_state: dict = {
            "running": False,
            "name": "",
            "started_at": 0.0,
            "finished_at": 0.0,
            "exit_code": None,
            "log": "",
        }
        self._history_lock = threading.Lock()

    def get_inbox(self, force: bool = False) -> tuple[dict, str]:
        now = time.time()
        with self._lock:
            if not force and self.inbox_cache and (now - self.inbox_ts) < 3.0:
                return self.inbox_cache, self.inbox_err
        try:
            tok = clc.get_invite_token()
            data = clc.fetch_chief_inbox(tok)
            with self._lock:
                self.inbox_cache = data
                self.inbox_ts = time.time()
                self.inbox_err = ""
            return data, ""
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            with self._lock:
                self.inbox_err = err
                return self.inbox_cache, err

    def trigger_worker_tasks_refresh(self, force: bool = False) -> None:
        now = time.time()
        with self._lock:
            if self._fetching_tasks:
                return
            if not force and self.worker_tasks and (now - self.worker_tasks_ts) < 25.0:
                return
            self._fetching_tasks = True

        def _bg() -> None:
            try:
                import process_muse_pipeline as pmp  # noqa: E402
                rows = pmp.fetch_hub_tasks()
                slim = []
                for r in rows:
                    payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}
                    res = r.get("result") if isinstance(r.get("result"), dict) else {}
                    summary = res.get("summary") or r.get("result_summary") or ""
                    if isinstance(summary, (dict, list)):
                        summary = json.dumps(summary, ensure_ascii=False)
                    slim.append({
                        "id": r.get("id") or r.get("task_id") or "",
                        "kind": r.get("kind") or "",
                        "assigned_to": r.get("assigned_to") or "",
                        "status": r.get("status") or "",
                        "claimed_by": r.get("claimed_by") or r.get("worker_id") or "",
                        "dedup": r.get("dedup") or "",
                        "slug": payload.get("slug") or r.get("slug") or "",
                        "objective": str(payload.get("objective") or "")[:240],
                        "summary": str(summary)[:900],
                        "updated_at": r.get("updated_at") or r.get("created_at") or 0,
                        "created_at": r.get("created_at") or 0,
                    })
                slim.sort(key=lambda x: float(x.get("updated_at") or 0), reverse=True)
                with self._lock:
                    self.worker_tasks = slim[:120]
                    self.worker_tasks_ts = time.time()
                    self.worker_tasks_err = ""
            except Exception as e:
                with self._lock:
                    self.worker_tasks_err = f"{type(e).__name__}: {str(e)[:200]}"
            finally:
                with self._lock:
                    self._fetching_tasks = False

        threading.Thread(target=_bg, daemon=True).start()

    def append_history(self, entry: dict) -> dict:
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        entry.setdefault("ts", time.time())
        entry.setdefault("time_str", datetime.now().strftime("%H:%M:%S %d/%m"))
        line = json.dumps(entry, ensure_ascii=False)
        with self._history_lock:
            with HISTORY_PATH.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        return entry

    def read_history(self, limit: int = 80) -> list[dict]:
        if not HISTORY_PATH.is_file():
            return []
        with self._history_lock:
            lines = HISTORY_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
        items = []
        for ln in lines[-limit:]:
            ln = ln.strip()
            if not ln:
                continue
            try:
                items.append(json.loads(ln))
            except Exception:
                pass
        items.reverse()
        return items

    def run_bg_action(self, name: str, cmd: list[str]) -> tuple[bool, str]:
        with self._lock:
            if self.action_state["running"]:
                return False, f"Đang chạy tác vụ `{self.action_state['name']}`, vui lòng đợi hoàn tất."
            self.action_state = {
                "running": True,
                "name": name,
                "started_at": time.time(),
                "finished_at": 0.0,
                "exit_code": None,
                "log": f"[{datetime.now().strftime('%H:%M:%S')}] Bắt đầu {name}...\n",
            }

        def _worker() -> None:
            buf: list[str] = []
            rc = -1
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=str(PIPELINE_DIR),
                )
                assert proc.stdout is not None
                for line in proc.stdout:
                    buf.append(line)
                    if len(buf) > 120:
                        buf = buf[-120:]
                    with self._lock:
                        self.action_state["log"] = "".join(buf)[-8000:]
                rc = proc.wait()
            except Exception as e:
                buf.append(f"\nERROR: {type(e).__name__}: {e}\n")
            finally:
                with self._lock:
                    self.action_state["running"] = False
                    self.action_state["finished_at"] = time.time()
                    self.action_state["exit_code"] = rc
                    self.action_state["log"] = ("".join(buf) + f"\n[{datetime.now().strftime('%H:%M:%S')}] Hoàn tất (exit={rc}).")[-8000:]

        threading.Thread(target=_worker, daemon=True).start()
        return True, f"Đã khởi chạy `{name}`."


STATE = StudioStateCache()


def _tail_file(path: Path, max_lines: int = 30) -> list[str]:
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return lines[-max_lines:]
    except Exception:
        return []


def _scan_featured_movies() -> list[dict]:
    out = []
    channels = ("phim-ma-dan-gian", "kiem-hiep-co-trang", "tap-lam-content", "tien-va-doi-srt", "")
    for slug, title, target in FEATURED_MOVIES:
        imgs = set()
        clips = set()
        final_mp4 = False
        for ch in channels:
            sdir = (MEDIA_ROOT / ch / slug) if ch else (MEDIA_ROOT / slug)
            if not sdir.is_dir():
                continue
            for f in sdir.rglob("*"):
                if not f.is_file():
                    continue
                nm = f.name.lower()
                if nm.startswith("scene_") and nm.endswith((".jpg", ".jpeg", ".png")):
                    imgs.add(nm)
                elif nm.startswith("scene_") and nm.endswith(".mp4"):
                    clips.add(nm)
                elif nm.endswith("_final.mp4") or nm == f"{slug}.mp4":
                    final_mp4 = True
        out.append({
            "slug": slug,
            "title": title,
            "target_scenes": target,
            "images": len(imgs),
            "clips": len(clips),
            "final_ready": final_mp4,
        })
    return out


def _get_roster_snapshot() -> list[dict]:
    new_keys: set[str] = set()
    if NEW_ROSTER_PATH.is_file():
        try:
            new_keys = {str(k)[:8] for k in json.loads(NEW_ROSTER_PATH.read_text(encoding="utf-8")).keys()}
        except Exception:
            pass
    acc_root = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "MuseLoginHelper" / "Accounts"
    disk_profiles = {d.name[:8] for d in acc_root.iterdir() if d.is_dir()} if acc_root.is_dir() else set()
    role_order = {"chief": 0, "director": 1, "artist": 2, "animator": 3, "qa_critic": 4}
    items = []
    seen = set()
    for pref, (role, title) in amr.ROSTER.items():
        seen.add(pref)
        items.append({
            "profile": pref,
            "role": role,
            "title": title,
            "is_new_cookie": pref in new_keys,
            "has_chrome_profile": pref in disk_profiles,
        })
    for pref in sorted(disk_profiles - seen):
        items.append({
            "profile": pref,
            "role": "extra",
            "title": "Hồ sơ dự phòng",
            "is_new_cookie": pref in new_keys,
            "has_chrome_profile": True,
        })
    items.sort(key=lambda x: (role_order.get(x["role"], 9), x["is_new_cookie"], x["profile"]))
    return items


def _get_api_meta() -> dict:
    try:
        cfg = clc.load_api_cfg()
        return {
            "configured": True,
            "model": cfg.get("model") or "gpt-6.1-sol",
            "base_url": cfg.get("base_url") or "",
            "hub_url": clc.HUB_BASE,
        }
    except Exception as e:
        return {
            "configured": False,
            "model": "chưa cấu hình",
            "base_url": "",
            "hub_url": clc.HUB_BASE,
            "error": str(e),
        }


def _build_full_state(force_inbox: bool = False) -> dict:
    inbox, inbox_err = STATE.get_inbox(force=force_inbox)
    STATE.trigger_worker_tasks_refresh(force=False)

    hb = {}
    if HEARTBEAT_PATH.is_file():
        try:
            hb = json.loads(HEARTBEAT_PATH.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            hb = {}

    lock_info = {"locked": False, "pid": "", "age_s": 0}
    if NUDGE_LOCK_PATH.is_file():
        try:
            age_s = round(time.time() - NUDGE_LOCK_PATH.stat().st_mtime, 1)
            if age_s < 600:
                lock_info = {
                    "locked": True,
                    "pid": NUDGE_LOCK_PATH.read_text(encoding="utf-8", errors="replace").strip(),
                    "age_s": age_s,
                }
        except Exception:
            pass

    with STATE._lock:
        worker_tasks = list(STATE.worker_tasks)
        worker_tasks_ts = STATE.worker_tasks_ts
        worker_tasks_err = STATE.worker_tasks_err
        fetching_tasks = STATE._fetching_tasks
        action_state = dict(STATE.action_state)

    return {
        "ok": True,
        "server_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
        "server_ts": time.time(),
        "api_meta": _get_api_meta(),
        "inbox": inbox,
        "inbox_error": inbox_err,
        "history": STATE.read_history(limit=80),
        "worker_tasks": worker_tasks,
        "worker_tasks_ts": worker_tasks_ts,
        "worker_tasks_err": worker_tasks_err,
        "worker_tasks_loading": fetching_tasks,
        "featured_movies": _scan_featured_movies(),
        "roster": _get_roster_snapshot(),
        "heartbeat": hb,
        "nudge_lock": lock_info,
        "daemon_log": _tail_file(DAEMON_LOG_PATH, 28),
        "croc_log": _tail_file(CROC_LOG_PATH, 28),
        "action": action_state,
    }


def _maybe_wake_chief() -> tuple[bool, str]:
    if NUDGE_LOCK_PATH.is_file():
        age = time.time() - NUDGE_LOCK_PATH.stat().st_mtime
        if age < 600:
            return False, f"Daemon đang đánh thức dàn Muse (lock {int(age)}s), lệnh đã vào Hub và sẽ được Muse Tổng đọc ngay."
    return STATE.run_bg_action(
        "Đánh thức Muse Tổng (db93da63)",
        [sys.executable, str(PIPELINE_DIR / "nudge_muses.py"), "--only", "db93da63"],
    )


class ControlUIHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return  # giữ console gọn sạch

    def _send_json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_bytes(self, code: int, data: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict:
        ln = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(ln) if ln > 0 else b"{}"
        return json.loads(raw.decode("utf-8", errors="replace") or "{}")

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        route = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        if route == "/":
            idx = STATIC_DIR / "index.html"
            if not idx.is_file():
                return self._send_json(500, {"ok": False, "error": "Missing ui_static/index.html"})
            return self._send_bytes(200, idx.read_bytes(), "text/html; charset=utf-8")

        if route == "/api/state":
            force = qs.get("force", ["0"])[0] == "1"
            return self._send_json(200, _build_full_state(force_inbox=force))

        if route == "/api/health":
            return self._send_json(200, {"ok": True, "ts": time.time()})

        return self._send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        route = urlsplit(self.path).path.rstrip("/")
        try:
            body = self._read_json()
        except Exception as e:
            return self._send_json(400, {"ok": False, "error": f"Invalid JSON: {e}"})

        # 1) Gọi API gpt-6.1-sol (test hoặc tự soạn & đẩy lệnh cho Muse Tổng)
        if route == "/api/llm/ask":
            user_prompt = str(body.get("prompt") or "").strip()
            auto_dispatch = bool(body.get("auto_dispatch", False))
            wake_chief = bool(body.get("wake_chief", False))
            include_ctx = bool(body.get("include_studio_context", True))
            if not user_prompt:
                return self._send_json(400, {"ok": False, "error": "Vui lòng nhập nội dung yêu cầu cho API."})

            try:
                cfg = clc.load_api_cfg()
                inbox, _ = STATE.get_inbox(force=True)
                full_prompt = user_prompt
                if include_ctx:
                    fleet = inbox.get("fleet") or {}
                    snap = {
                        "active_workers_5m": fleet.get("active_workers_5m"),
                        "task_counts": fleet.get("task_counts"),
                        "pending_commands": len(inbox.get("pending_commands") or []),
                        "scores_summary": inbox.get("scores_summary"),
                        "featured_movies_on_E": _scan_featured_movies()[:4],
                    }
                    mode_hint = (
                        "Hãy viết ĐÚNG 1 đoạn chỉ thị súc tích, rõ ràng bằng tiếng Việt (tối đa 5 câu, không dùng markdown rườm rà) để gửi trực tiếp cho Muse Tổng Điều Phối (chief) thực thi ngay."
                        if auto_dispatch
                        else "Hãy trả lời trực tiếp bằng tiếng Việt, ngắn gọn, cụ thể, dựa trên số liệu thật của xưởng bên dưới."
                    )
                    full_prompt = (
                        f"Bối cảnh xưởng phim AI hiện tại (số liệu thật): {json.dumps(snap, ensure_ascii=False)}\n"
                        f"Yêu cầu từ Chủ dự án: {user_prompt}\n"
                        f"{mode_hint}"
                    )

                reply_text, via, elapsed = clc.call_llm_responses(cfg, full_prompt)
                hub_resp = None
                cmd_id = ""
                wake_msg = ""

                if auto_dispatch:
                    tok = clc.get_invite_token()
                    model_tag = cfg.get("model") or "gpt-6.1-sol"
                    hub_resp = clc.send_chief_command(tok, f"[API {model_tag}] {reply_text}", source=model_tag)
                    cmd_id = str(hub_resp.get("id") or hub_resp.get("command_id") or (hub_resp.get("command") or {}).get("id") or "")
                    STATE.get_inbox(force=True)
                    if wake_chief:
                        _, wake_msg = _maybe_wake_chief()

                entry = STATE.append_history({
                    "type": "llm_dispatch" if auto_dispatch else "llm_chat",
                    "user_prompt": user_prompt,
                    "api_model": cfg.get("model") or "gpt-6.1-sol",
                    "api_via": via,
                    "api_elapsed_s": elapsed,
                    "api_response": reply_text,
                    "dispatched_to_chief": auto_dispatch,
                    "hub_command_id": cmd_id,
                    "hub_response": hub_resp,
                    "wake_msg": wake_msg,
                })
                return self._send_json(200, {"ok": True, "entry": entry})
            except Exception as e:
                err_txt = f"{type(e).__name__}: {e}"
                STATE.append_history({
                    "type": "llm_error",
                    "user_prompt": user_prompt,
                    "api_model": _get_api_meta().get("model"),
                    "error": err_txt,
                })
                return self._send_json(502, {"ok": False, "error": err_txt})

        # 2) Gửi thẳng lệnh cho Muse Tổng (/api/chief/command)
        if route == "/api/chief/send":
            cmd_text = str(body.get("command_text") or "").strip()
            source = str(body.get("source") or "owner_ui").strip() or "owner_ui"
            wake_chief = bool(body.get("wake_chief", False))
            if not cmd_text:
                return self._send_json(400, {"ok": False, "error": "Nội dung lệnh trống."})
            try:
                tok = clc.get_invite_token()
                hub_resp = clc.send_chief_command(tok, cmd_text, source=source)
                cmd_id = str(hub_resp.get("id") or hub_resp.get("command_id") or (hub_resp.get("command") or {}).get("id") or "")
                STATE.get_inbox(force=True)
                wake_msg = ""
                if wake_chief:
                    _, wake_msg = _maybe_wake_chief()
                entry = STATE.append_history({
                    "type": "direct_chief",
                    "source": source,
                    "user_prompt": cmd_text,
                    "dispatched_to_chief": True,
                    "hub_command_id": cmd_id,
                    "hub_response": hub_resp,
                    "wake_msg": wake_msg,
                })
                return self._send_json(200, {"ok": True, "entry": entry})
            except Exception as e:
                return self._send_json(502, {"ok": False, "error": f"{type(e).__name__}: {e}"})

        # 3) Các nút hành động nhanh
        if route == "/api/action":
            act = str(body.get("action") or "").strip()
            if act == "wake_chief":
                ok, msg = _maybe_wake_chief()
                return self._send_json(200, {"ok": ok, "message": msg})
            if act == "wake_all":
                if NUDGE_LOCK_PATH.is_file() and (time.time() - NUDGE_LOCK_PATH.stat().st_mtime) < 600:
                    return self._send_json(200, {"ok": False, "message": "Đang có tiến trình đánh thức dàn Muse chạy sẵn (nudge_muses.lock)."})
                ok, msg = STATE.run_bg_action(
                    "Đánh thức toàn đội 25 Muse",
                    [sys.executable, str(PIPELINE_DIR / "nudge_muses.py")],
                )
                return self._send_json(200, {"ok": ok, "message": msg})
            if act == "harvest_now":
                ok, msg = STATE.run_bg_action(
                    "Thu hoạch & Đồng bộ Hub (process_muse_pipeline)",
                    [sys.executable, str(PIPELINE_DIR / "process_muse_pipeline.py")],
                )
                return self._send_json(200, {"ok": ok, "message": msg})
            if act == "refresh_tasks":
                STATE.trigger_worker_tasks_refresh(force=True)
                STATE.get_inbox(force=True)
                return self._send_json(200, {"ok": True, "message": "Đang tải lại danh sách task & báo cáo từ Hub..."})
            return self._send_json(400, {"ok": False, "error": f"Unknown action: {act}"})

        return self._send_json(404, {"ok": False, "error": "not_found"})


def main() -> int:
    ap = argparse.ArgumentParser(description="Muse Chief & API gpt-6.1-sol Control Center UI")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8788)
    args = ap.parse_args()

    STATE.trigger_worker_tasks_refresh(force=True)
    srv = ThreadingHTTPServer((args.host, args.port), ControlUIHandler)
    print(f"MUSE_CONTROL_UI_READY http://{args.host}:{args.port}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
