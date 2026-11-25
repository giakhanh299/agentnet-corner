# core/vps_live · Bản Hub đang chạy thật trên VPS

Chụp từ `/opt/agentnet-corner` ngày 25/11/2026 (service `agentnet-corner.service`, version `1.3-fleet`).

| File | SHA-256 (khớp VPS) |
| :--- | :--- |
| `corner.py` | `0b08adcbadce5b44fb717e81ed4cabe1c531684d9e1297e8fd7f88eef78232cc` |
| `research_queue.py` | `49f1415fa669dea9db0ed846b01ed9cd185a19ffa9ba7650e2de9437bb53d1a5` |
| `hub_portal.py` | `85ee92495cc6c95088e05a7a708c91778e8146a05d7b5c41c51989a1e36580d0` |
| `ggmap_scout.py` | `54baae6472a1bee3753840fb907a5a05d48573cb937c13dc8ef9994be4743f84` |
| `join.py` | `b7969218ed411b210ba645e3fe23ed787fa880f72c5ab3ddf121c788c2a73d58` |

- Đây là nguồn để **deploy lại** khi VPS hỏng. Bản V2.0 ở gốc repo chưa deploy.
- `state/` (SQLite registry/queue, ảnh ggmap) không nằm trong git.
- Test: `cd core/vps_live && python -m unittest discover -p "test_*.py" -v`
