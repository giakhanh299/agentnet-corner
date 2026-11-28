"""Kiểm tra tự động chuẩn Kịch bản & Chỉ đạo Diễn xuất v2 cho episode.json (Phim Ma / Kiếm Hiệp).

Chuẩn gốc: docs/roles/TIEU_CHUAN_KICH_BAN_VA_DIEN_XUAT.md
Công cụ chỉ bắt lỗi hình thức có thể đo được; chất lượng diễn vẫn do QA đọc và chấm.

Dùng:
    python studio/script_direction_lint.py path/to/episode.json [--json]
Mã thoát: 0 = đạt (điểm >= 80 và không lỗi nghiêm trọng), 1 = chưa đạt, 2 = lỗi đọc file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STANDARD_VERSION = "v2.0"
PASS_SCORE = 80

ACTED_TYPES = {"doi_thoai", "hanh_dong"}
ALL_TYPES = ACTED_TYPES | {"dan_truyen"}
MIN_ACTED_RATIO = 0.60
MAX_NARRATION_RATIO = 0.30
MAX_LINE_WORDS = 20
SHOT_KEYS = ("size", "angle", "subject", "purpose", "move")

# Lời gián tiếp: "cậu nói cậu nghe…", "ông nói canh linh cữu…", "bà kể rằng…", "hắn bảo là…"
_PRONOUNS = r"(?:cậu|ông|bà|cô|anh|chị|em|hắn|nàng|chàng|lão|y|gã|thầy|người đó|họ|nó)"
REPORTED_SPEECH_RE = re.compile(
    rf"\b{_PRONOUNS}\s+(?:nói|bảo|kể|hỏi|đáp|dặn|kêu)\b(?![^\".“,;]{{0,24}}[:\"“])|\b(?:nói|bảo|kể|hỏi|đáp|dặn)\s+(?:rằng|là)\b",
    re.IGNORECASE,
)
# Đọc lại hồ sơ nhân vật: tuổi
AGE_DUMP_RE = re.compile(
    r"\b\d{1,3}\s*tuổi\b|\b(?:mười|hai mươi|ba mươi|bốn mươi|năm mươi|sáu mươi|bảy mươi|tám mươi|chín mươi)(?:\s+\w+)?\s+tuổi\b",
    re.IGNORECASE,
)
# Thoại thuyết minh / gọi tên cảm xúc
EXPOSITION_RE = re.compile(r"\bnhư\s+(?:cậu|anh|em|ông|bà|cô|ngươi|các hạ|huynh|muội)\s+(?:đã\s+)?biết\b|\bđể\s+(?:tôi|ta|con)\s+kể\b", re.IGNORECASE)
NAMED_EMOTION_RE = re.compile(r"\b(?:tôi|ta|con|em|tại hạ)\s+(?:đang\s+)?(?:rất\s+|thật\s+)?(?:sợ|buồn|giận|tức giận|đau khổ|vui)\s*(?:lắm|quá)?\s*[.!…]?$", re.IGNORECASE)
# Máy quay chung chung (chỉ lỗi khi đứng một mình, không có chủ thể/hành động)
GENERIC_CAMERA_RE = re.compile(
    r"\b(?:slow\s+(?:zoom(?:\s+in|\s+out)?|push[- ]in|pan|crane(?:\s+shot)?|tracking(?:\s+shot)?|dolly(?:\s+in)?)|camera\s+moves?\s+forward|cinematic\s+shot|zoom\s+chậm|máy\s+quay\s+tiến\s+vào)\b",
    re.IGNORECASE,
)
ACTION_HINT_RE = re.compile(
    r"\b(?:turns?|looks?|stares?|glances?|grips?|raises?|lowers?|steps?|walks?|runs?|reaches?|grabs?|pulls?|pushes?|taps?|knocks?|leans?|kneels?|swallows?|whispers?|shouts?|speaks?|says?|nods?|shakes?|trembles?|draws?|points?|opens?|closes?|lifts?|drops?|holds?|blinks?|flinches?|freezes?|backs?\s+away|steps?\s+back|recoils?|smiles?|frowns?|cries?|bows?)\b",
    re.IGNORECASE,
)

SEVERE = "severe"
MAJOR = "major"
MINOR = "minor"
PENALTY = {SEVERE: 10, MAJOR: 3, MINOR: 1}


def _words(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def _is_generic_motion(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if not GENERIC_CAMERA_RE.search(t):
        return False
    rest = GENERIC_CAMERA_RE.sub(" ", t)
    return not ACTION_HINT_RE.search(rest)


def lint_episode(spec: dict) -> dict:
    issues: list[dict] = []

    def add(level: str, code: str, msg: str, scene: int | None = None) -> None:
        issues.append({"level": level, "code": code, "scene": scene, "msg": msg})

    scenes = spec.get("scenes") or []
    chars = ((spec.get("character_bible") or {}).get("characters") or [])
    char_ids = {str(c.get("id")) for c in chars if c.get("id")}

    for c in chars:
        missing = [k for k in ("speech_style", "want", "secret") if not str(c.get(k) or "").strip()]
        if missing:
            add(MINOR, "BIBLE_V2_MISSING", f"Nhân vật '{c.get('id')}' thiếu {', '.join(missing)}")

    n = len(scenes)
    if n == 0:
        add(SEVERE, "NO_SCENES", "episode.json không có cảnh nào")

    type_counts = {t: 0 for t in ALL_TYPES}
    untyped = 0
    reported_scenes: list[int] = []
    age_dump_scenes: list[int] = []
    confront_by_act: dict[int, int] = {}
    acts_seen: set[int] = set()

    for idx, sc in enumerate(scenes, 1):
        sid = int(sc.get("id") or idx)
        act = int(sc.get("act") or 0)
        acts_seen.add(act)
        stype = str(sc.get("scene_type") or "").strip()
        vo = str(sc.get("voiceover") or "")

        if stype not in ALL_TYPES:
            untyped += 1
            add(MAJOR, "SCENE_TYPE_MISSING", "Thiếu/không hợp lệ scene_type (doi_thoai|hanh_dong|dan_truyen)", sid)
        else:
            type_counts[stype] += 1

        if not str(sc.get("beat") or "").strip():
            add(MAJOR, "BEAT_MISSING", "Thiếu beat (trước → chuyện xảy ra → sau)", sid)

        if REPORTED_SPEECH_RE.search(vo):
            reported_scenes.append(sid)
            add(MAJOR, "REPORTED_SPEECH", "voiceover dùng lời gián tiếp — chuyển thành thoại trực tiếp", sid)
        if AGE_DUMP_RE.search(vo):
            age_dump_scenes.append(sid)
            add(MAJOR, "PROFILE_DUMP", "voiceover đọc lại tuổi/hồ sơ nhân vật — đã có trong character_bible và ảnh", sid)

        shot = sc.get("shot")
        if not isinstance(shot, dict):
            add(MAJOR, "SHOT_MISSING", "Thiếu shot {size, angle, subject, purpose, move}", sid)
        else:
            miss = [k for k in SHOT_KEYS if not str(shot.get(k) or "").strip()]
            if miss:
                add(MINOR, "SHOT_INCOMPLETE", f"shot thiếu {', '.join(miss)}", sid)
            mv = str(shot.get("move") or "")
            if mv and mv.strip().lower() != "static" and _is_generic_motion(mv) and not str(shot.get("purpose") or "").strip():
                add(MAJOR, "GENERIC_CAMERA", f"shot.move chung chung, không động cơ: '{mv[:60]}'", sid)

        motion = str(sc.get("motion") or "")
        if _is_generic_motion(motion):
            add(MAJOR, "GENERIC_MOTION", f"motion chỉ mô tả máy quay, thiếu diễn xuất nhân vật: '{motion[:70]}'", sid)

        if idx > 1:
            cont = sc.get("continuity")
            if not isinstance(cont, dict) or not str(cont.get("from_prev") or "").strip():
                add(MINOR, "CONTINUITY_MISSING", "Thiếu continuity.from_prev", sid)

        if stype in ACTED_TYPES:
            for key in ("blocking", "action"):
                if not str(sc.get(key) or "").strip():
                    add(MAJOR, f"{key.upper()}_MISSING", f"Cảnh {stype} thiếu {key}", sid)

        if stype == "doi_thoai":
            dlg = sc.get("dialogue")
            if not isinstance(dlg, list) or not dlg:
                add(SEVERE, "DIALOGUE_MISSING", "Cảnh doi_thoai không có dialogue", sid)
                dlg = []
            speakers = set()
            for li, d in enumerate(dlg, 1):
                if not isinstance(d, dict):
                    add(MAJOR, "DIALOGUE_FORMAT", f"Lượt thoại {li} sai định dạng", sid)
                    continue
                sp, to, line = str(d.get("speaker") or ""), str(d.get("to") or ""), str(d.get("line") or "")
                speakers.add(sp)
                if char_ids and sp not in char_ids:
                    add(MAJOR, "UNKNOWN_SPEAKER", f"Lượt {li}: speaker '{sp}' không có trong character_bible", sid)
                if not to:
                    add(MINOR, "NO_LISTENER", f"Lượt {li}: thiếu 'to' (nói với ai)", sid)
                if not str(d.get("intent") or "").strip():
                    add(MINOR, "NO_INTENT", f"Lượt {li}: thiếu intent (ý đồ câu thoại)", sid)
                wc = _words(line)
                if wc > MAX_LINE_WORDS:
                    add(MAJOR, "LINE_TOO_LONG", f"Lượt {li} dài {wc} chữ (> {MAX_LINE_WORDS}) — dễ thành thuyết minh", sid)
                if EXPOSITION_RE.search(line):
                    add(MAJOR, "EXPOSITION_LINE", f"Lượt {li} là thoại thuyết minh: '{line[:50]}'", sid)
                if NAMED_EMOTION_RE.search(line.strip()):
                    add(MINOR, "NAMED_EMOTION", f"Lượt {li} gọi tên cảm xúc thay vì thể hiện: '{line[:50]}'", sid)
                if AGE_DUMP_RE.search(line):
                    add(MAJOR, "PROFILE_DUMP_LINE", f"Lượt {li}: nhân vật tự đọc tuổi/hồ sơ", sid)
            rx = sc.get("reaction")
            if not (isinstance(rx, dict) and str(rx.get("what") or "").strip()) and not (isinstance(rx, str) and rx.strip()):
                add(MAJOR, "REACTION_MISSING", "Cảnh thoại thiếu reaction của người nghe", sid)
            if len({s for s in speakers if s}) >= 2:
                confront_by_act[act] = confront_by_act.get(act, 0) + 1

    if n:
        acted_ratio = (type_counts["doi_thoai"] + type_counts["hanh_dong"]) / n
        narration_ratio = type_counts["dan_truyen"] / n
        if acted_ratio < MIN_ACTED_RATIO:
            add(SEVERE, "ACTED_RATIO_LOW", f"Chỉ {acted_ratio:.0%} cảnh có diễn (cần ≥ {MIN_ACTED_RATIO:.0%})")
        if narration_ratio > MAX_NARRATION_RATIO:
            add(SEVERE, "NARRATION_RATIO_HIGH", f"{narration_ratio:.0%} cảnh chỉ lời dẫn (tối đa {MAX_NARRATION_RATIO:.0%})")
        for act in sorted(a for a in acts_seen if a > 0):
            if confront_by_act.get(act, 0) == 0:
                add(SEVERE, "NO_CONFRONTATION", f"Hồi {act} không có cảnh đối đầu ≥ 2 nhân vật thoại qua lại")
        if len(reported_scenes) >= 5:
            add(SEVERE, "REPORTED_SPEECH_WIDESPREAD", f"{len(reported_scenes)} cảnh dùng lời gián tiếp: {reported_scenes[:12]}")
        if len(age_dump_scenes) >= 5:
            add(SEVERE, "PROFILE_DUMP_WIDESPREAD", f"{len(age_dump_scenes)} cảnh đọc lại hồ sơ nhân vật: {age_dump_scenes[:12]}")
    else:
        acted_ratio = narration_ratio = 0.0

    penalty = sum(PENALTY[i["level"]] for i in issues)
    score = max(0, 100 - min(penalty, 100))
    severe = [i for i in issues if i["level"] == SEVERE]
    by_code: dict[str, int] = {}
    for i in issues:
        by_code[i["code"]] = by_code.get(i["code"], 0) + 1
    return {
        "standard": STANDARD_VERSION,
        "slug": spec.get("slug"),
        "scenes": n,
        "scene_types": type_counts,
        "acted_ratio": round(acted_ratio, 3),
        "narration_ratio": round(narration_ratio, 3),
        "score": score,
        "passed": score >= PASS_SCORE and not severe,
        "severe_count": len(severe),
        "issue_counts": dict(sorted(by_code.items(), key=lambda kv: -kv[1])),
        "issues": issues,
    }


def _print_human(rep: dict) -> None:
    status = "ĐẠT" if rep["passed"] else "CHƯA ĐẠT"
    print(f"[{status}] {rep.get('slug')} — chuẩn {rep['standard']} — điểm {rep['score']}/100 — {rep['severe_count']} lỗi nghiêm trọng")
    print(f"  Cảnh: {rep['scenes']} | loại: {rep['scene_types']} | có diễn {rep['acted_ratio']:.0%} | lời dẫn {rep['narration_ratio']:.0%}")
    print(f"  Thống kê lỗi: {rep['issue_counts']}")
    for i in [x for x in rep["issues"] if x["level"] == SEVERE] + [x for x in rep["issues"] if x["level"] != SEVERE][:25]:
        where = f"cảnh {i['scene']}" if i["scene"] else "toàn tập"
        print(f"  - [{i['level']}] {i['code']} ({where}): {i['msg']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("episode_json", type=Path)
    ap.add_argument("--json", action="store_true", help="In báo cáo JSON")
    args = ap.parse_args(argv)
    try:
        spec = json.loads(args.episode_json.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"Không đọc được {args.episode_json}: {e}", file=sys.stderr)
        return 2
    rep = lint_episode(spec)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        _print_human(rep)
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
