"""Giọng đọc dùng chung cho studio (hỗ trợ đa giọng Nam / Nữ / Châu Tinh Trì / Phim Ma trên từng câu thoại).

- `phonui`: giọng gốc Phim Ma ấm, ma mị (giong_dalat_chua_lanh_ref.wav, atempo=1.06) — đã cắt sạch khoảng lặng đầu/cuối.
- `chautinhtri`: giọng Châu Tinh Trì cho Kiếm Hiệp / Cổ Trang (chautinhtri_short.wav, atempo=1.14).
- `kiemhiep_nam` (alias `nam`, `tauthao`): giọng nam hiệp trầm hùng (giongtauthao_short.wav, atempo=1.15).
- `kiemhiep_nu` (alias `nu`, `nu_hiep`): giọng nữ hiệp / cô nương truyền cảm (vieneu_nu_ref.wav, atempo=1.14).
- `taplamcontent` (alias `maianh`): giọng nữ sáng rõ Tập Làm Content KENH_008 (giongnucute.wav, atempo=1.22).
- `tienvadoi`: giọng nam trầm 100Hz chuẩn Tiền Và Đời KENH_001 (giongcuakienthuctaichinh_short.wav, atempo=1.22).
- `phimma`: giọng nam review nhanh (vieneu_nam_ref.wav, atempo=1.24).
"""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

VIENEU_PY = Path(r"D:\0.1_FACE_BOOK\Lay video tiktok\MOI_TRUONG\tts_thu_nghiem\vieneu_env\Scripts\python.exe")
VIENEU_WORKER = Path(r"D:\0.1_FACE_BOOK\Lay video tiktok\backend\vieneu_worker.py")
VOICE_SAMPLES = Path(r"D:\0.1_FACE_BOOK\Lay video tiktok\voice_samples")

PHONUI_REF = VOICE_SAMPLES / "giong_dalat_chua_lanh_ref.wav"
CHAUTINHTRI_REF = VOICE_SAMPLES / "chautinhtri_short.wav"
TAUTHAO_REF = VOICE_SAMPLES / "giongtauthao_short.wav"
VIENEU_NU_REF = VOICE_SAMPLES / "vieneu_nu_ref.wav"
PHIMMA_REF = VOICE_SAMPLES / "vieneu_nam_ref.wav"
TAPLAMCONTENT_REF = VOICE_SAMPLES / "giongnucute.wav"
TIENVADOI_REF = VOICE_SAMPLES / "giongcuakienthuctaichinh_short.wav"

VOICE_PROFILES: dict[str, tuple[Path, float]] = {
    "phonui": (PHONUI_REF, 1.06),
    "chautinhtri": (CHAUTINHTRI_REF, 1.14),
    "kiemhiep_nam": (TAUTHAO_REF, 1.15),
    "nam": (TAUTHAO_REF, 1.15),
    "tauthao": (TAUTHAO_REF, 1.15),
    "kiemhiep_nu": (VIENEU_NU_REF, 1.14),
    "nu": (VIENEU_NU_REF, 1.14),
    "nu_hiep": (VIENEU_NU_REF, 1.14),
    "taplamcontent": (TAPLAMCONTENT_REF, 1.22),
    "maianh": (TAPLAMCONTENT_REF, 1.22),
    "tienvadoi": (TIENVADOI_REF, 1.22),
    "phimma": (PHIMMA_REF, 1.24),
}

VOICES = {
    "phonui": "VieNeu v3turbo · Giọng gốc Phim Ma ấm, ma mị (atempo=1.06, cắt khoảng lặng)",
    "chautinhtri": "VieNeu v3turbo · Châu Tinh Trì cho Kiếm Hiệp (atempo=1.14)",
    "kiemhiep_nam": "VieNeu v3turbo · Nam hiệp trầm hùng (atempo=1.15)",
    "kiemhiep_nu": "VieNeu v3turbo · Nữ hiệp / cô nương truyền cảm (atempo=1.14)",
    "taplamcontent": "VieNeu v3turbo · Nữ sáng rõ Tập Làm Content KENH_008 (atempo=1.22)",
    "maianh": "Alias -> taplamcontent",
    "tienvadoi": "VieNeu v3turbo · Nam trầm 100Hz chuẩn Tiền Và Đời KENH_001 (atempo=1.22)",
    "phimma": "VieNeu v3turbo · Nam review nhanh (atempo=1.24)",
    "edge_nam": "edge-tts vi-VN-NamMinhNeural",
    "edge_nu": "edge-tts vi-VN-HoaiMyNeural",
}


def synth_multi(items: list[tuple[str, str]], out_dir: Path) -> list[Path]:
    """Nhận danh sách [(text, voice_key), ...] và tổng hợp đa giọng Nam/Nữ chỉ trong 1 lần nạp model VieNeu.
    Tự động cắt sạch khoảng lặng thừa ở CẢ ĐẦU VÀ CUỐI câu để triệt tiêu khoảng nghỉ chết.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    outs = [out_dir / f"vo_{i:02d}.wav" for i in range(len(items))]
    todo_vieneu: list[tuple[int, str, Path, float, Path]] = []
    todo_edge: list[tuple[int, str, str, Path]] = []

    for i, ((text, vkey), out_wav) in enumerate(zip(items, outs)):
        if out_wav.is_file() and out_wav.stat().st_size > 1024:
            continue
        vk = (vkey or "phonui").lower().strip()
        if vk in ("edge_nam", "edge_nu"):
            ev = "vi-VN-HoaiMyNeural" if vk == "edge_nu" else "vi-VN-NamMinhNeural"
            todo_edge.append((i, text, ev, out_wav))
        else:
            ref, atempo = VOICE_PROFILES.get(vk, VOICE_PROFILES["phonui"])
            use_ref = ref if ref.is_file() else PHONUI_REF
            todo_vieneu.append((i, text, use_ref, atempo, out_wav))

    if todo_vieneu:
        if not VIENEU_PY.is_file() or not VIENEU_WORKER.is_file():
            raise FileNotFoundError("Thiếu môi trường VieNeu")
        payload = [
            json.dumps(
                {"text": t, "ref_audio": str(ref), "denoise": True, "out": str(out_dir / f"raw_{i:02d}.wav")},
                ensure_ascii=False,
            )
            for i, t, ref, _, _ in todo_vieneu
        ]
        payload.append(json.dumps({"cmd": "quit"}))
        proc = subprocess.run(
            [str(VIENEU_PY), str(VIENEU_WORKER), "v3turbo", "auto"],
            input="\n".join(payload) + "\n",
            text=True, encoding="utf-8", capture_output=True,
        )
        errs = [ln for ln in proc.stdout.splitlines() if ln.startswith("@@VN@@") and '"ok": false' in ln]
        if proc.returncode or errs:
            raise RuntimeError(f"VieNeu lỗi: {errs[:2] or proc.stderr[-400:]}")
        for i, _, _, atempo, out_wav in todo_vieneu:
            raw = out_dir / f"raw_{i:02d}.wav"
            # Trim BOTH leading AND trailing dead silence so shots lock back-to-back with zero dead air
            af = (
                "silenceremove=start_periods=1:start_threshold=-44dB,"
                "areverse,silenceremove=start_periods=1:start_threshold=-44dB,areverse"
            )
            if abs(atempo - 1.0) > 0.01:
                af += f",atempo={atempo:.2f}"
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ar", "48000", "-ac", "1", str(out_wav)],
                check=True,
            )
            raw.unlink(missing_ok=True)

    if todo_edge:
        import edge_tts

        async def _run_edge():
            for i, t, ev, out_wav in todo_edge:
                mp3 = out_dir / f"vo_{i:02d}.mp3"
                await edge_tts.Communicate(t, ev, rate="+12%").save(str(mp3))
                subprocess.run(
                    ["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(out_wav)],
                    check=True,
                )
                mp3.unlink(missing_ok=True)

        asyncio.run(_run_edge())

    return outs


def synth(lines: list[str], out_dir: Path, voice: str = "phonui") -> list[Path]:
    return synth_multi([(t, voice) for t in lines], out_dir)


def ghost_fx(src: Path, dst: Path, semitones: float = -3.0) -> Path:
    """Giọng ma: hạ cao độ, vang lạnh, lệch pan chậm."""
    ratio = 2 ** (semitones / 12)
    af = (f"rubberband=pitch={ratio:.4f},aecho=0.8:0.7:90|180:0.35|0.25,"
          "apulsator=hz=0.12:amount=0.6,volume=-2dB")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "2", "-af", af, "-ar", "48000", str(dst)],
                   check=True)
    return dst


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True)
    return float(out.stdout.strip() or 0)
