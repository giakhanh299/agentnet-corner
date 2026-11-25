"""
Muse AI OS – Video Studio  (localhost:3456)
Backend FastAPI – quản lý hàng đợi tạo video hàng loạt
"""
import uuid, json, time, asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

app = FastAPI(title="Muse AI OS Video Studio", version="1.0.0")

# ── In-memory state ──────────────────────────────────────────
TASKS: dict[str, dict] = {}           # task_id -> task obj
PROJECTS: dict[str, dict] = {}        # project_id -> project
CONFIG = {
    "muse_accounts": ["Nam Em (1 ảnh)", "Muse Pro #1", "Muse Pro #2"],
    "active_account": "Nam Em (1 ảnh)",
    "luong_active": 0,
    "luong_max": 9,
    "muse_free": 9,
    "drive_synced": True,
    "bot_tg": 1,
}
QUEUE_STATUS = "idle"   # idle | running | paused

# ── Pydantic models ──────────────────────────────────────────
class TaskCreate(BaseModel):
    prompt: str
    account: str = "Nam Em (1 ảnh)"
    ratio: str = "9:16"
    model_ver: str = "v1"
    project_id: Optional[str] = None

class BulkCreate(BaseModel):
    prompts: List[str]
    account: str = "Nam Em (1 ảnh)"
    ratio: str = "9:16"
    model_ver: str = "v1"
    project_id: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str

# ── Helper ───────────────────────────────────────────────────
def _make_task(prompt: str, account: str, ratio: str, model_ver: str, project_id=None) -> dict:
    tid = str(uuid.uuid4())[:8]
    return {
        "id": tid,
        "prompt": prompt[:120],
        "prompt_full": prompt,
        "account": account,
        "ratio": ratio,
        "model": model_ver,
        "status": "pending",   # pending | running | done | error | stopped
        "progress": 0,
        "created_at": datetime.now().strftime("%H:%M %d-%m"),
        "thumb": None,
        "output_url": None,
        "project_id": project_id,
        "error_msg": None,
    }

async def _simulate_run(task_id: str):
    """Simulate video generation (replace with real Muse API call later)."""
    global CONFIG
    t = TASKS.get(task_id)
    if not t or t["status"] not in ("pending", "queued"):
        return
    t["status"] = "running"
    CONFIG["luong_active"] = sum(1 for x in TASKS.values() if x["status"] == "running")
    CONFIG["muse_free"] = max(0, CONFIG["muse_max"] if hasattr(CONFIG, "muse_max") else 9 - CONFIG["luong_active"])
    # Simulate progress
    for p in range(0, 101, 10):
        await asyncio.sleep(1.5)
        if TASKS.get(task_id, {}).get("status") == "stopped":
            return
        t["progress"] = p
    t["status"] = "done"
    t["progress"] = 100
    CONFIG["luong_active"] = sum(1 for x in TASKS.values() if x["status"] == "running")

# ── API Routes ───────────────────────────────────────────────
@app.get("/api/status")
def get_status():
    return {
        **CONFIG,
        "queue_status": QUEUE_STATUS,
        "task_counts": {
            s: sum(1 for t in TASKS.values() if t["status"] == s)
            for s in ["pending", "queued", "running", "done", "error", "stopped"]
        }
    }

@app.get("/api/tasks")
def list_tasks(project_id: Optional[str] = None):
    tasks = list(TASKS.values())
    if project_id:
        tasks = [t for t in tasks if t.get("project_id") == project_id]
    return sorted(tasks, key=lambda x: x["created_at"], reverse=True)

@app.post("/api/tasks")
def create_task(body: TaskCreate, bg: BackgroundTasks):
    t = _make_task(body.prompt, body.account, body.ratio, body.model_ver, body.project_id)
    t["status"] = "queued"
    TASKS[t["id"]] = t
    bg.add_task(_simulate_run, t["id"])
    return t

@app.post("/api/tasks/bulk")
def bulk_create(body: BulkCreate, bg: BackgroundTasks):
    created = []
    for p in body.prompts:
        p = p.strip()
        if not p:
            continue
        t = _make_task(p, body.account, body.ratio, body.model_ver, body.project_id)
        t["status"] = "queued"
        TASKS[t["id"]] = t
        bg.add_task(_simulate_run, t["id"])
        created.append(t)
    return {"created": len(created), "tasks": created}

@app.post("/api/tasks/{task_id}/stop")
def stop_task(task_id: str):
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(404, "task not found")
    t["status"] = "stopped"
    return t

@app.post("/api/tasks/{task_id}/retry")
def retry_task(task_id: str, bg: BackgroundTasks):
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(404)
    t["status"] = "queued"
    t["progress"] = 0
    t["error_msg"] = None
    bg.add_task(_simulate_run, task_id)
    return t

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    t = TASKS.pop(task_id, None)
    if not t:
        raise HTTPException(404)
    return {"deleted": task_id}

@app.delete("/api/tasks")
def clear_done():
    ids = [tid for tid, t in TASKS.items() if t["status"] in ("done", "error")]
    for tid in ids:
        TASKS.pop(tid)
    return {"cleared": len(ids)}

@app.post("/api/queue/run")
def run_queue(bg: BackgroundTasks):
    global QUEUE_STATUS
    QUEUE_STATUS = "running"
    pending = [t for t in TASKS.values() if t["status"] == "pending"]
    for t in pending:
        t["status"] = "queued"
        bg.add_task(_simulate_run, t["id"])
    return {"started": len(pending)}

@app.post("/api/queue/stop")
def stop_queue():
    global QUEUE_STATUS
    QUEUE_STATUS = "paused"
    for t in TASKS.values():
        if t["status"] in ("running", "queued"):
            t["status"] = "stopped"
    return {"ok": True}

@app.get("/api/projects")
def list_projects():
    return list(PROJECTS.values())

@app.post("/api/projects")
def create_project(body: ProjectCreate):
    pid = str(uuid.uuid4())[:8]
    p = {"id": pid, "name": body.name, "created_at": datetime.now().isoformat()}
    PROJECTS[pid] = p
    return p

@app.get("/api/config")
def get_config():
    return CONFIG

@app.patch("/api/config")
def patch_config(data: dict):
    CONFIG.update(data)
    return CONFIG

# ── Seed demo tasks (phim ma pilot) ─────────────────────────
def _seed():
    scenes_path = Path(__file__).parent.parent / "pilot01_ma_da" / "scenes.json"
    if scenes_path.exists():
        data = json.loads(scenes_path.read_text(encoding="utf-8"))
        for s in data.get("scenes", []):
            t = _make_task(
                prompt=f"**Bối cảnh:** {s['label']} | " + s.get("prompt_en", s.get("prompt_vi","")),
                account=s.get("muse_account","Nam Em (1 ảnh)"),
                ratio=s.get("ratio","9:16"),
                model_ver="v1",
                project_id="pilot01"
            )
            t["status"] = "pending"
            TASKS[t["id"]] = t
        PROJECTS["pilot01"] = {
            "id": "pilot01",
            "name": "Ma Da Kéo Giò – Pilot #1",
            "created_at": datetime.now().isoformat()
        }

_seed()

# ── Serve static UI ──────────────────────────────────────────
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    return FileResponse(str(static_dir / "index.html"))
