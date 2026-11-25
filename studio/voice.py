"""Giọng đọc dùng chung cho studio.

- `phonui`: giọng kênh Góc Nhỏ Phố Núi (VieNeu-TTS v3turbo clone từ giong_dalat_chua_lanh_ref.wav).
  Gọi môi trường + worker có sẵn ở Tầng 1 ở chế độ CHỈ ĐỌC; file ra ghi vào thư mục làm việc của studio.
- `edge`: edge-tts (vi-VN-NamMinhNeural / HoaiMyNeural) — nháp nhanh, cần mạng.
- ghost_fx(): biến một câu thành giọng ma (hạ cao độ + vang + lệch pan) bằng FFmpeg rubberband.
"""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

VIENEU_PY = Path(r"D:\0.1_FACE_BOOK\Lay video tiktok\MOI_TRUONG\tts_thu_nghiem\vieneu_env\Scripts\python.exe")
VIENEU_WORKER = Path(r"D:\0.1_FACE_BOOK\Lay video tiktok\backend\vieneu_worker.py")
PHONUI_REF = Path(r"D:\0.1_FACE_BOOK\Lay video tiktok\voice_samples\giong_dalat_chua_lanh_ref.wav")

VOICES = {
    "phonui": "VieNeu v3turbo · clone Góc Nhỏ Phố Núi (Đà Lạt chữa lành)",
    "edge_nam": "edge-tts vi-VN-NamMinhNeural",
    "edge_nu": "edge-tts vi-VN-HoaiMyNeural",
}


def synth_phonui(lines: list[str], out_dir: Path, ref: Path = PHONUI_REF) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    outs = [out_dir / f"vo_{i:02d}.wav" for i in range(len(lines))]
    todo = [(t, o) for t, o in zip(lines, outs) if not o.is_file()]
    if todo:
        if not VIENEU_PY.is_file() or not VIENEU_WORKER.is_file() or not ref.is_file():
            raise FileNotFoundError("Thiếu môi trường VieNeu hoặc file giọng mẫu Phố Núi")
        payload = [json.dumps({"text": t, "ref_audio": str(ref), "denoise": True, "out": str(o)}, ensure_ascii=False)
                   for t, o in todo]
        payload.append(json.dumps({"cmd": "quit"}))
        proc = subprocess.run([str(VIENEU_PY), str(VIENEU_WORKER), "v3turbo", "auto"],
                              input="\n".join(payload) + "\n", text=True, encoding="utf-8", capture_output=True)
        errs = [ln for ln in proc.stdout.splitlines() if ln.startswith("@@VN@@") and '"ok": false' in ln]
        if proc.returncode or errs:
            raise RuntimeError(f"VieNeu lỗi: {errs[:2] or proc.stderr[-400:]}")
    return outs


def synth_edge(lines: list[str], out_dir: Path, voice: str = "vi-VN-NamMinhNeural", rate: str = "-8%") -> list[Path]:
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


def synth(lines: list[str], out_dir: Path, voice: str = "phonui") -> list[Path]:
    if voice == "phonui":
        return synth_phonui(lines, out_dir)
    if voice == "edge_nu":
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
