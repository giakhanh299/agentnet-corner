"""Đồng bộ sổ tay vai trò (docs/roles/*.md) từ Git lên VPS Hub (/opt/agentnet-corner/roles)
để mọi AI (bất kể model hay phiên chat) đọc được qua https://muse.alltool.pro/roles/.

Cách dùng:
    python studio/pipeline/publish_role_docs.py                 # chỉ đồng bộ file .md trong docs/roles/
    python studio/pipeline/publish_role_docs.py --deploy-hub    # đồng bộ .md + cập nhật hub_portal.py & restart service
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
ROLES_LOCAL = REPO_ROOT / "docs" / "roles"
HUB_LOCAL = REPO_ROOT / "core" / "vps_live" / "hub_portal.py"
VPS_ROLES_DIR = "/opt/agentnet-corner/roles"
VPS_HUB_FILE = "/opt/agentnet-corner/hub_portal.py"
HUB_BASE = "https://muse.alltool.pro"

sys.path.insert(0, str(HERE))
import process_muse_pipeline as pm  # noqa: E402


def _run_remote(ssh, cmd: str) -> tuple[int, str, str]:
    _, out, err = ssh.exec_command(cmd)
    rc = out.channel.recv_exit_status()
    return rc, out.read().decode("utf-8", "replace").strip(), err.read().decode("utf-8", "replace").strip()


def publish(deploy_hub: bool = False, verify: bool = True) -> dict:
    if not ROLES_LOCAL.is_dir():
        raise FileNotFoundError(f"Không thấy thư mục sổ tay: {ROLES_LOCAL}")
    md_files = sorted(p for p in ROLES_LOCAL.glob("*.md") if p.is_file())
    if not md_files:
        raise RuntimeError(f"Không có file .md nào trong {ROLES_LOCAL}")

    local_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in md_files}
    ssh = pm.connect_vps_ssh(timeout=30)
    try:
        rc, _, err = _run_remote(ssh, f"mkdir -p {VPS_ROLES_DIR}")
        if rc != 0:
            raise RuntimeError(f"mkdir failed: {err}")

        sftp = ssh.open_sftp()
        try:
            # Xoá file .md thừa trên VPS nếu không còn trong Git
            remote_existing = {f for f in sftp.listdir(VPS_ROLES_DIR) if f.endswith(".md")}
            for stale in sorted(remote_existing - set(local_hashes)):
                sftp.remove(f"{VPS_ROLES_DIR}/{stale}")

            for p in md_files:
                sftp.put(str(p), f"{VPS_ROLES_DIR}/{p.name}")

            hub_restarted = False
            if deploy_hub:
                if not HUB_LOCAL.is_file():
                    raise FileNotFoundError(f"Không thấy {HUB_LOCAL}")
                _run_remote(ssh, f"cp -f {VPS_HUB_FILE} {VPS_HUB_FILE}.bak_roles")
                sftp.put(str(HUB_LOCAL), VPS_HUB_FILE)
        finally:
            sftp.close()

        _run_remote(ssh, f"chown -R agentnet-corner:agentnet-corner {VPS_ROLES_DIR} && chmod 644 {VPS_ROLES_DIR}/*.md")

        if deploy_hub:
            rc, out, err = _run_remote(
                ssh,
                f"chown agentnet-corner:agentnet-corner {VPS_HUB_FILE} && "
                f"python3 -m py_compile {VPS_HUB_FILE} && "
                f"systemctl restart agentnet-corner.service && "
                f"sleep 1 && systemctl is-active agentnet-corner.service",
            )
            if rc != 0 or "active" not in out:
                raise RuntimeError(f"Restart agentnet-corner.service thất bại: rc={rc} out={out} err={err}")
            hub_restarted = True
    finally:
        ssh.close()

    verified = None
    if verify:
        req = urllib.request.Request(f"{HUB_BASE}/roles", headers={"User-Agent": "AgentNetRolePublish/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            idx = json.loads(r.read().decode("utf-8"))
        remote_hashes = {d["file"]: d["sha256"] for d in (idx.get("docs") or [])}
        mismatches = [
            f for f, h in local_hashes.items()
            if remote_hashes.get(f) != h
        ]
        if mismatches:
            raise RuntimeError(f"Sai lệch sha256 sau khi đẩy lên Hub: {mismatches}")
        verified = {"count": len(remote_hashes), "matched_sha256": True, "url": f"{HUB_BASE}/roles"}

    return {
        "ok": True,
        "published": sorted(local_hashes.keys()),
        "hub_restarted": hub_restarted,
        "verified": verified,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--deploy-hub", action="store_true", help="Cập nhật thêm core/vps_live/hub_portal.py và khởi động lại service")
    ap.add_argument("--no-verify", action="store_true", help="Bỏ qua bước gọi HTTPS kiểm chứng /roles")
    args = ap.parse_args(argv)
    res = publish(deploy_hub=args.deploy_hub, verify=not args.no_verify)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
