"""Cấu hình tách nhánh sản xuất âm thanh / dựng phim cho xưởng Muse Studio.

Hai nhánh chính thức:
- Cấu hình 1 (`ke_chuyen` — MẶC ĐỊNH HIỆN TẠI):
    Nhánh Kể Chuyện (Storytelling). Dùng DUY NHẤT 1 giọng `phonui` (Góc Nhỏ Phố Núi)
    xuyên suốt toàn bộ tập truyện (Phim Ma Dân Gian & Kiếm Hiệp Cổ Trang),
    không nhảy sang đa giọng nhân vật, không biến dạng giọng kể.

- Cấu hình 2 (`phim_da_vai` — DÀNH CHO NHÁNH LÀM PHIM THẬT SỰ):
    Pipeline chuẩn làm phim:
      1) Đọc kịch bản & phân tích cảnh (narrator vs dialogue trực diện).
      2) Tách cảnh đối thoại để chạy khẩu hình miệng (lip-sync) khớp nhân vật.
      3) Phân vai nhân vật theo giới tính / tuyến vai (character_id, gender).
      4) Tổng hợp đa giọng (multi-voice: phonui / chautinhtri / kiemhiep_nam / kiemhiep_nu + ghost_fx).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_PROFILE = "ke_chuyen"
PROFILE_STATE_FILE = Path(r"E:\MUSE_MEDIA_STUDIO\production_profile.json")

PRODUCTION_PROFILES: dict[str, dict[str, Any]] = {
    "ke_chuyen": {
        "id": "ke_chuyen",
        "config_slot": 1,
        "label": "Cấu hình 1 · Nhánh Kể Chuyện (1 giọng Góc Nhỏ Phố Núi)",
        "voice_mode": "single_narrator",
        "story_narrator_voice": "phonui",
        "allow_scene_voice_override": False,
        "allow_gender_casting": False,
        "allow_ghost_fx": False,
        "lip_sync_required": False,
        "stages": ["story_narration_single_voice", "ai_motion_clips", "bgm_sfx_subtitles"],
    },
    "phim_da_vai": {
        "id": "phim_da_vai",
        "config_slot": 2,
        "label": "Cấu hình 2 · Nhánh Làm Phim Đa Vai (Phân tích kịch bản + Khẩu hình miệng + Multi-voice)",
        "voice_mode": "multi_character_film",
        "story_narrator_voice": "phonui",
        "allow_scene_voice_override": True,
        "allow_gender_casting": True,
        "allow_ghost_fx": True,
        "lip_sync_required": True,
        "voice_cast": {
            "narrator": "phonui",
            "male_wuxia": "chautinhtri",
            "male_folk": "kiemhiep_nam",
            "female": "kiemhiep_nu",
        },
        "stages": [
            "script_scene_analysis",
            "dialogue_lipsync_split",
            "character_role_casting",
            "multi_voice_tts",
        ],
    },
}


def resolve_profile_name(explicit: str | None = None, spec: dict | None = None) -> str:
    """Thứ tự ưu tiên: tham số truyền trực tiếp -> spec['production_profile'] -> file state -> env -> mặc định `ke_chuyen`."""
    candidates = [
        explicit,
        (spec or {}).get("production_profile"),
    ]
    if PROFILE_STATE_FILE.is_file():
        try:
            data = json.loads(PROFILE_STATE_FILE.read_text(encoding="utf-8"))
            candidates.append(data.get("active_profile"))
        except Exception:
            pass
    candidates.append(os.environ.get("MUSE_PRODUCTION_PROFILE"))
    candidates.append(DEFAULT_PROFILE)

    for cand in candidates:
        key = str(cand or "").strip().lower()
        if key in PRODUCTION_PROFILES:
            return key
    return DEFAULT_PROFILE


def get_profile(explicit: str | None = None, spec: dict | None = None) -> dict[str, Any]:
    return PRODUCTION_PROFILES[resolve_profile_name(explicit=explicit, spec=spec)]
