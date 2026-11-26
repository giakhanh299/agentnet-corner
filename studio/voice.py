"""Giọng đọc dùng chung cho studio (gọi chỉ đọc môi trường VieNeu ở Tầng 1).

- `phimma`: giọng nam kể chuyện/review phim nhanh, cuốn hút (clone vieneu_nam_ref.wav, atempo=1.26).
- `taplamcontent` (alias `maianh`): giọng nữ trong trẻo, lanh lợi cho Tập Làm Content KENH_008 (clone giongnucute.wav, atempo=1.22).
- `tienvadoi`: giọng nam trầm chắc 100Hz chuẩn kênh Tiền Và Đời KENH_001 (clone giongcuakienthuctaichinh_short.wav, atempo=1.22).
- `phonui`: giọng kể chuyện ấm (mặc định nâng nhịp atempo=1.24 khi dùng cho phim ma/kiếm hiệp để không bị chậm).
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
PHIMMA_REF = VOICE_SAMPLES / "vieneu_nam_ref.wav"
TAPLAMCONTENT_REF = VOICE_SAMPLES / "giongnucute.wav"
TIENVADOI_REF = VOICE_SAMPLES / "giongcuakienthuctaichinh_short.wav"

VOICES = {
    "phimma": "VieNeu v3turbo · Nam kể phim nhanh cuốn hút (atempo=1.26)",
    "taplamcontent": "VieNeu v3turbo · Nữ sáng rõ Tập Làm Content KENH_008 (atempo=1.22)",
    "maianh": "Alias -> taplamcontent (đã bỏ atempo=0.78 gây méo chậm)",
    "tienvadoi": "VieNeu v3turbo · Nam trầm 100Hz chuẩn Tiền Và Đời KENH_001 (atempo=1.22)",
    "phonui": "VieNeu v3turbo · Giọng kể ấm nâng nhịp (atempo=1.24)",
    "edge_nam": "edge-tts vi-VN-NamMinhNeural",
    "edge_nu": "edge-tts vi-VN-HoaiMyNeural",
}


def synth_vieneu_clone(lines: list[str], out_dir: Path, ref: Path, atempo: float = 1.24) -> list[Path]:
    """Clone từ mẫu giọng chuẩn bằng vieneu_worker (chỉ đọc) + chỉnh nhịp atempo tự nhiên."""
    out_dir.mkdir(parents=True, exist_ok=True)
    outs = [out_dir / f"vo_{i:02d}.wav" for i in range(len(lines))]
    todo = [(i, t, o) for i, (t, o) in enumerate(zip(lines, outs)) if not o.is_file()]
    if todo:
        use_ref = ref if ref.is_file() else PHONUI_REF
        if not VIENEU_PY.is_file() or not VIENEU_WORKER.is_file() or not use_ref.is_file():
            raise FileNotFoundError(f"Thiếu môi trường VieNeu hoặc mẫu giọng: {use_ref}")
        payload = [
            json.dumps({"text": t, "ref_audio": str(use_ref), "denoise": True, "out": str(out_dir / f"raw_{i:02d}.wav")}, ensure_ascii=False)
            for i, t, _ in todo
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
        af = "silenceremove=start_periods=1:start_threshold=-45dB"
        if abs(atempo - 1.0) > 0.01:
            af += f",atempo={atempo:.2f}"
        for i, _, o in todo:
            raw = out_dir / f"raw_{i:02d}.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ar", "48000", "-ac", "1", str(o)],
                check=True,
            )
            raw.unlink(missing_ok=True)
    return outs


def synth_edge(lines: list[str], out_dir: Path, voice: str = "vi-VN-NamMinhNeural", rate: str = "+12%") -> list[Path]:
    import edge_tts

    out_dir.mkdir(parents=True, exist_ok=True)
    outs = []

    async def _run():
        for i, t in enumerate(lines):
            mp3 = out_dir / f"vo_{i:02d}.mp3"
            wav = out_dir / f"vo_{i:02d}.wav"
            if not wav.is_file():
                await edge_tts.Communicate(t, voice, rate=rate).save(str(mp3))
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(wav)],
                               check=True)
            outs.append(wav)

    asyncio.run(_run())
    return outs


def synth(lines: list[str], out_dir: Path, voice: str = "phimma") -> list[Path]:
    v = (voice or "phimma").lower().strip()
    if v == "phimma":
        return synth_vieneu_clone(lines, out_dir, PHIMMA_REF, atempo=1.26)
    if v in ("taplamcontent", "maianh"):
        return synth_vieneu_clone(lines, out_dir, TAPLAMCONTENT_REF, atempo=1.22)
    if v == "tienvadoi":
        return synth_vieneu_clone(lines, out_dir, TIENVADOI_REF, atempo=1.22)
    if v == "phonui":
        return synth_vieneu_clone(lines, out_dir, PHIMMA_REF, atempo=1.25)
    if v == "edge_nu":
        return synth_edge(lines, out_dir, "vi-VN-HoaiMyNeural")
    return synth_edge(lines, out_dir, "vi-VN-NamMinhNeural")


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
