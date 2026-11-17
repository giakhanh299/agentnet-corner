"""Phase 2: Cross-Platform Persistent Worker Daemon (GPU-First -> CPU-Fallback).

Solves the 3 runtime reliability gaps in AgentNet V1.2:
1. Auto-detects hardware capabilities (`gpu_cuda` on RTX 5060 Ti, `tts_mms`,
   `whisper_large_v3`, `ffmpeg`, `manim`, `cpu_fallback`) so `ResearchQueue`
   automatically routes heavy jobs to PC GPU when online and falls back to VPS1
   CPU when PC is powered off.
2. Spawns a background Heartbeat thread every 45s while a task runs so 15-minute
   leases never expire during batch Whisper/Manim/FFmpeg jobs.
3. Maintains an atomic disk Outbox (`~/.agentnet-corner/outbox/`) so results are
   never lost on transient Tailscale/network drops.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import threading
import time
from typing import Callable, Protocol
from urllib.request import ProxyHandler, Request, build_opener

from .episode_compiler import EpisodeCompiler
from .qc_verify import inspect_episode
from .tts_auto_heal import ensure_windows_cuda_dlls_and_utf8


def detect_worker_capabilities() -> list[str]:
    ensure_windows_cuda_dlls_and_utf8()
    caps = ["python3", "cpu_fallback"]
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        caps.extend(["ffmpeg", "ffprobe", "visual_essay"])
    try:
        import torch  # type: ignore
        if torch.cuda.is_available():
            caps.append("gpu_cuda")
    except Exception:
        pass
    try:
        import transformers  # noqa: F401
        caps.append("tts_mms")
    except Exception:
        pass
    try:
        import faster_whisper  # noqa: F401
        caps.append("whisper_large_v3" if "gpu_cuda" in caps else "whisper_cpu")
    except Exception:
        pass
    stickman_root = Path(__file__).resolve().parent.parent / "stickman-shorts"
    if (stickman_root / "src" / "rig" / "character.py").exists():
        caps.append("manim_stickman")
    vieneu_py = Path(__file__).resolve().parent.parent / "ai-stack" / ".venv-vieneu" / "Scripts" / "python.exe"
    if vieneu_py.exists():
        caps.append("tts_vieneu")
    return sorted(set(caps))


class QueueTransport(Protocol):
    def claim(self, role: str, capabilities: list[str], as_role: str | None = None) -> dict: ...
    def heartbeat(self, task_id: str, lease: str, as_role: str | None = None) -> dict: ...
    def submit_result(self, task_id: str, lease: str, result: dict, as_role: str | None = None) -> dict: ...
    def get_task(self, task_id: str) -> dict: ...


class LocalQueueTransport:
    """In-process transport for unit/integration tests and single-machine runs."""
    def __init__(self, queue, node_id: str, role: str, delegated: bool = False):
        self.queue = queue
        self.node = {"id": node_id, "role": role}
        self.delegated = delegated

    def claim(self, role: str, capabilities: list[str], as_role: str | None = None) -> dict:
        body: dict = {"capabilities": capabilities}
        if as_role:
            body["as_role"] = as_role
        return self.queue.post(self.node, "/claim", body, self.delegated)

    def heartbeat(self, task_id: str, lease: str, as_role: str | None = None) -> dict:
        body: dict = {"lease": lease}
        if as_role:
            body["as_role"] = as_role
        return self.queue.post(self.node, f"/tasks/{task_id}/heartbeat", body, self.delegated)

    def submit_result(self, task_id: str, lease: str, result: dict, as_role: str | None = None) -> dict:
        body: dict = {"lease": lease, "result": result}
        if as_role:
            body["as_role"] = as_role
        return self.queue.post(self.node, f"/tasks/{task_id}/result", body, self.delegated)

    def get_task(self, task_id: str) -> dict:
        return self.queue.get(self.node, f"/tasks/{task_id}")


class HttpQueueTransport:
    """Tailscale HTTP transport refreshing `/controller` route as mandated by V1.2."""
    def __init__(self, master_url: str, state_dir: Path, proxy_url: str | None = None):
        self.master_url = master_url.rstrip("/")
        self.state_dir = state_dir
        self.opener = build_opener(ProxyHandler({"http": proxy_url, "https": proxy_url})) if proxy_url else build_opener()
        self._controller_url: str | None = None
        self._token: str | None = None

    def refresh_route(self) -> dict:
        ident = json.loads((self.state_dir / "identity.json").read_text(encoding="utf-8"))
        req = Request(
            f"{self.master_url}/controller",
            headers={"Authorization": f"Bearer {ident['token']}", "X-AgentNet-Client": "join/2"},
        )
        with self.opener.open(req, timeout=15) as r:
            conn = json.load(r)
        if conn.get("project") not in ("research", "studio") or conn.get("mode") not in ("research-only", "studio-auto99"):
            raise RuntimeError("Invalid project/mode on controller route")
        self._controller_url = conn["controller_url"].rstrip("/")
        self._token = conn["application_token"]
        return conn

    def _call(self, path: str, body: dict | None = None) -> dict:
        if not self._controller_url or not self._token:
            self.refresh_route()
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = Request(f"{self._controller_url}{path}", data=data, headers=headers)
        with self.opener.open(req, timeout=20) as r:
            return json.load(r)

    def claim(self, role: str, capabilities: list[str], as_role: str | None = None) -> dict:
        self.refresh_route()
        body: dict = {"capabilities": capabilities}
        if as_role:
            body["as_role"] = as_role
        return self._call("/claim", body)

    def heartbeat(self, task_id: str, lease: str, as_role: str | None = None) -> dict:
        body: dict = {"lease": lease}
        if as_role:
            body["as_role"] = as_role
        return self._call(f"/tasks/{task_id}/heartbeat", body)

    def submit_result(self, task_id: str, lease: str, result: dict, as_role: str | None = None) -> dict:
        body: dict = {"lease": lease, "result": result}
        if as_role:
            body["as_role"] = as_role
        return self._call(f"/tasks/{task_id}/result", body)

    def get_task(self, task_id: str) -> dict:
        return self._call(f"/tasks/{task_id}")


class WorkerDaemon:
    """Autonomous background runner with lease heartbeats and persistent outbox."""

    def __init__(
        self,
        transport: QueueTransport,
        role: str,
        outbox_dir: Path,
        workspace_dir: Path,
        capabilities: list[str] | None = None,
        as_role: str | None = None,
        heartbeat_interval_s: float = 45.0,
        compiler: EpisodeCompiler | None = None,
    ):
        self.transport = transport
        self.role = role
        self.as_role = as_role
        self.outbox_dir = Path(outbox_dir)
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.capabilities = capabilities if capabilities is not None else detect_worker_capabilities()
        self.heartbeat_interval_s = heartbeat_interval_s
        self.compiler = compiler
        self.handlers: dict[str, Callable[[dict], dict]] = {
            "episode_produce": self._handle_episode_produce,
            "episode_compile": self._handle_episode_produce,
            "verify_episode_produce": self._handle_verify_episode,
            "verify_episode_compile": self._handle_verify_episode,
        }

    def register_handler(self, kind: str, fn: Callable[[dict], dict]) -> None:
        self.handlers[kind] = fn

    def flush_outbox(self) -> int:
        flushed = 0
        for item_file in sorted(self.outbox_dir.glob("*.json")):
            saved = json.loads(item_file.read_text(encoding="utf-8"))
            try:
                res = self.transport.submit_result(
                    saved["task_id"], saved["lease"], saved["result"], as_role=saved.get("as_role")
                )
                if res.get("received"):
                    item_file.unlink()
                    flushed += 1
            except Exception:
                # Keep in outbox if transient network failure; discard only if permanent 403/409
                pass
        return flushed

    def _save_to_outbox(self, task_id: str, lease: str, result: dict) -> Path:
        path = self.outbox_dir / f"{task_id}.json"
        path.write_text(
            json.dumps(
                {"task_id": task_id, "lease": lease, "result": result, "as_role": self.as_role},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return path

    def _handle_episode_produce(self, task: dict) -> dict:
        payload = task.get("payload") or {}
        spec = payload.get("episode_spec") or payload.get("spec_path")
        if not spec:
            return {"outcome": "BLOCKED", "summary": "Missing episode_spec or spec_path in payload"}
        slug = (spec.get("slug") if isinstance(spec, dict) else None) or payload.get("slug") or task["id"][:8]
        attempt = int(task.get("attempt") or 1)
        out_dir = self.workspace_dir / f"{slug}_attempt{attempt}"
        comp = self.compiler or EpisodeCompiler()
        quality = payload.get("quality", "high")
        out = comp.compile(spec, out_dir=out_dir, quality=quality)
        return {
            "outcome": "ok",
            "slug": out["slug"],
            "title": out["title"],
            "video_path": out["video_path"],
            "timing_json": out["timing_json"],
            "captions_ass": out["captions_ass"],
            "duration_s": out["duration_s"],
            "speech_wpm": out["speech_wpm"],
            "asr_match": out["asr_match"],
            "summary": f"Compiled {out['slug']} ({out['duration_s']}s, {out['speech_wpm']} wpm, ASR {out['asr_match']:.1%})",
            "evidence_links": [out["video_path"]],
            "limitations": [],
        }

    def _handle_verify_episode(self, task: dict) -> dict:
        payload = task.get("payload") or {}
        target_id = payload.get("target_task_id") or task.get("target_task_id")
        if not target_id:
            return {"outcome": "FAIL", "hard_gate_passed": False, "score": 0, "reasons": ["Missing target_task_id"]}
        target_task = self.transport.get_task(target_id)
        t_res = target_task.get("result") or {}
        criteria = payload.get("acceptance_criteria") or {}
        min_score = float(criteria.get("min_score", 85.0))
        dur_bounds = tuple(criteria.get("duration_bounds", [35.0, 65.0]))  # type: ignore
        return inspect_episode(
            video_path=t_res.get("video_path", ""),
            timing_json_path=t_res.get("timing_json"),
            ass_path=t_res.get("captions_ass"),
            duration_bounds=(float(dur_bounds[0]), float(dur_bounds[1])),
            min_score=min_score,
        )

    def run_once(self) -> dict | None:
        self.flush_outbox()
        claimed = self.transport.claim(self.role, self.capabilities, as_role=self.as_role)
        if not claimed or not claimed.get("id"):
            return None

        tid = claimed["id"]
        lease = claimed["lease"]
        kind = claimed["kind"]
        stop_evt = threading.Event()

        def _hb_loop():
            while not stop_evt.wait(self.heartbeat_interval_s):
                try:
                    self.transport.heartbeat(tid, lease, as_role=self.as_role)
                except Exception:
                    pass

        hb_thread = threading.Thread(target=_hb_loop, daemon=True)
        hb_thread.start()
        try:
            handler = self.handlers.get(kind)
            if not handler:
                result = {"outcome": "UNSUPPORTED_CAPABILITY", "summary": f"No handler registered for kind={kind}"}
            else:
                result = handler(claimed)
        except Exception as exc:
            result = {"outcome": "RETRYABLE_FAIL", "summary": f"Worker execution error: {exc}", "reasons": [str(exc)]}
        finally:
            stop_evt.set()
            hb_thread.join(timeout=2.0)

        outbox_file = self._save_to_outbox(tid, lease, result)
        resp = self.transport.submit_result(tid, lease, result, as_role=self.as_role)
        if resp.get("received") and outbox_file.exists():
            outbox_file.unlink()
        return {"task_id": tid, "kind": kind, "result": result, "submit_response": resp}

    def serve_forever(self, poll_seconds: float = 10.0) -> None:
        print(f"[worker-daemon] role={self.role} as_role={self.as_role} capabilities={self.capabilities}")
        while True:
            try:
                worked = self.run_once()
                if not worked:
                    time.sleep(poll_seconds)
            except KeyboardInterrupt:
                break
            except Exception as exc:
                print(f"[worker-daemon] transient poll error: {exc}")
                time.sleep(poll_seconds)


def main() -> int:
    ensure_windows_cuda_dlls_and_utf8()
    p = argparse.ArgumentParser(description="AgentNet V2.0 Persistent Worker Daemon")
    p.add_argument("role", choices=["engineer", "verify", "research", "controller"])
    p.add_argument("--master", default="http://100.67.236.124:8110")
    p.add_argument("--state", default=str(Path.home() / ".agentnet-corner"))
    p.add_argument("--workspace", default=str(Path(__file__).resolve().parent.parent / "studio_runs"))
    p.add_argument("--as-role", default=None, help="Set to 'engineer' when controller runs delegated jobs")
    p.add_argument("--proxy", default=None, help="Optional tunnel proxy URL (e.g. http://host:3130)")
    p.add_argument("--poll-seconds", type=float, default=10.0)
    args = p.parse_args()

    state = Path(args.state)
    transport = HttpQueueTransport(args.master, state_dir=state, proxy_url=args.proxy)
    daemon = WorkerDaemon(
        transport=transport,
        role=args.role,
        outbox_dir=state / "outbox",
        workspace_dir=Path(args.workspace),
        as_role=args.as_role,
    )
    daemon.serve_forever(poll_seconds=args.poll_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
