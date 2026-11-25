"""Sinh bộ ảnh dọc 9:16 (768x1344) chuẩn điện ảnh trên GPU local (RTX 5060 Ti) bằng RealVisXL V5.0 Lightning.

- Lưu cache model vào D:\MEDIA_STUDIO\_hf_cache (không chiếm ổ C).
- Tự bỏ qua các cảnh đã có ảnh (trừ khi truyền --overwrite) nên ghép mượt với ảnh Muse nộp.
- Xuất kèm storyboard.png (lưới toàn bộ cảnh) để soi QC bằng mắt trước khi ghép video.

python studio/image_gen.py --spec channels/phim-ma-dan-gian/ep01_ma_da/episode.json \
       --out-dir D:/MEDIA_STUDIO/phim-ma-dan-gian/ep01_ma_da/01_images
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

os.environ.setdefault("HF_HOME", r"D:\MEDIA_STUDIO\_hf_cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from PIL import Image  # noqa: E402

MODEL_ID = "SG161222/RealVisXL_V5.0_Lightning"
DEFAULT_NEG = (
    "red Chinese lanterns, Chinese palace, curved pagoda roof, Hanfu, Chinese text, Japanese text, "
    "text, letters, subtitles, watermark, logo, modern clothing, cars, neon, electric streetlight, "
    "anime, cartoon, 3d render, plastic skin, gore, blood, visible scary ghost face, "
    "extra fingers, deformed hands, ugly, blurry, lowres"
)
STYLE_SUFFIX = ", 35mm documentary cinema still, moody natural lighting, subtle film grain, atmospheric, photorealistic"


def make_storyboard(images: list[Path], dst: Path, cols: int = 3) -> Path:
    if not images:
        return dst
    tw, th = 270, 480
    rows = math.ceil(len(images) / cols)
    pad = 8
    canvas = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * th + (rows + 1) * pad), (10, 12, 16))
    for i, p in enumerate(images):
        r, c = divmod(i, cols)
        with Image.open(p) as im:
            im = im.convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
            canvas.paste(im, (pad + c * (tw + pad), pad + r * (th + pad)))
    dst.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dst, "PNG")
    return dst


def build_prompt(scene: dict, spec: dict) -> tuple[str, str]:
    raw = str(scene.get("image_prompt") or scene.get("label") or "").strip()
    if "cinematic" not in raw.lower() and "documentary" not in raw.lower():
        raw = raw + STYLE_SUFFIX
    neg = str(spec.get("negative_prompt") or "").strip()
    if not neg or len(neg) < 30:
        neg = DEFAULT_NEG
    else:
        neg = neg + ", watermark, logo, text, deformed hands, extra fingers, blurry"
    return raw, neg


def generate_episode(
    spec_path: Path,
    out_dir: Path,
    overwrite: bool = False,
    steps: int = 6,
    guidance: float = 1.8,
    width: int = 768,
    height: int = 1344,
) -> list[Path]:
    import torch
    from diffusers import StableDiffusionXLPipeline

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    scenes = sorted(spec.get("scenes") or [], key=lambda s: int(s.get("id", 0)))
    out_dir.mkdir(parents=True, exist_ok=True)

    todo = []
    saved = []
    for sc in scenes:
        sid = int(sc["id"])
        dst = out_dir / f"scene_{sid:02d}.png"
        saved.append(dst)
        if overwrite or not dst.is_file():
            todo.append((sc, dst))

    if not todo:
        print(f"Đã đủ {len(saved)} ảnh trong {out_dir}")
        make_storyboard(saved, out_dir / "storyboard.png")
        return saved

    print(f"Đang nạp model {MODEL_ID} (cache: {os.environ['HF_HOME']})…", flush=True)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True,
    )
    pipe.to("cuda")
    pipe.vae.enable_slicing()

    ep_seed = int(spec.get("seed") or spec.get("episode") or 1) * 1000
    for sc, dst in todo:
        sid = int(sc["id"])
        prompt, neg = build_prompt(sc, spec)
        gen = torch.Generator(device="cuda").manual_seed(ep_seed + sid * 17)
        print(f"  [scene_{sid:02d}] {sc.get('label', '')[:45]}…", flush=True)
        img = pipe(
            prompt=prompt,
            negative_prompt=neg,
            num_inference_steps=steps,
            guidance_scale=guidance,
            width=width,
            height=height,
            generator=gen,
        ).images[0]
        img.save(dst, "PNG")

    board = make_storyboard(saved, out_dir / "storyboard.png")
    print(f"Xong {len(saved)} ảnh + storyboard: {board}", flush=True)
    return saved


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh bộ ảnh 9:16 điện ảnh cho tập phim bằng RTX 5060 Ti")
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--steps", type=int, default=6)
    ap.add_argument("--guidance", type=float, default=1.8)
    a = ap.parse_args()
    generate_episode(a.spec, a.out_dir, overwrite=a.overwrite, steps=a.steps, guidance=a.guidance)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
