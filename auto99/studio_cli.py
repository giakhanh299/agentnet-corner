"""CLI entrypoint for AgentNet V2.0 Auto-99% Studio."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .episode_compiler import EpisodeCompiler, load_episode_spec
from .qc_verify import inspect_episode
from .tts_auto_heal import ensure_windows_cuda_dlls_and_utf8


def cmd_run_local(args) -> int:
    spec = load_episode_spec(args.spec)
    out_dir = Path(args.out).resolve()
    compiler = EpisodeCompiler()
    print(f"[Auto-99%] Compiling episode '{spec.get('slug', 'episode')}' -> {out_dir} ...")
    compiled = compiler.compile(spec, out_dir=out_dir, quality=args.quality)
    qc = inspect_episode(
        video_path=compiled["video_path"],
        timing_json_path=compiled["timing_json"],
        ass_path=compiled["captions_ass"],
        duration_bounds=(args.min_duration, args.max_duration),
        min_score=args.min_score,
    )
    (out_dir / "qc_report.json").write_text(
        json.dumps(qc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"compiled": compiled, "qc": qc}, ensure_ascii=False, indent=2))
    return 0 if qc["outcome"] == "PASS" else 2


def main() -> int:
    ensure_windows_cuda_dlls_and_utf8()
    p = argparse.ArgumentParser(description="AgentNet V2.0 Auto-99% Studio CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    loc = sub.add_parser("run-local", help="Compile + Self-Heal TTS + 2-Pass Loudnorm + Auto-QC in 1 command")
    loc.add_argument("--spec", required=True, help="Path to episode.yaml or episode.json")
    loc.add_argument("--out", required=True, help="Output directory")
    loc.add_argument("--quality", choices=["low", "high"], default="high")
    loc.add_argument("--min-duration", type=float, default=35.0)
    loc.add_argument("--max-duration", type=float, default=65.0)
    loc.add_argument("--min-score", type=float, default=85.0)

    args = p.parse_args()
    if args.cmd == "run-local":
        return cmd_run_local(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
