"""Phase 4: Unified Declarative Episode Compiler (Visual Essay + Stickman).

Compiles a single declarative `episode.yaml` / `episode.json` manifest into a
broadcast-ready 1080x1920 30fps `final.mp4`:
1. Runs `TTSAutoHealer` (unless pre-built `timing.json` + `voice.wav` provided).
2. Compiles visuals synced to exact measured beat timestamps:
   - `template: visual_essay` -> FFmpeg Ken Burns zoompan + Be Vietnam Pro Bold
     cards + dark endcard + `captions.ass` (run with `cwd=build_dir` so Windows
     paths with `C:` never break `drawtext` or `libass`).
   - `template: stickman` -> Auto-generates `generated_scene.py` against the
     frozen `stickman-shorts` rig (`Stickman`, `TextCard`, `POSE_*`, gestures,
     props) and renders via Manim.
3. Normalizes audio via true 2-pass EBU R128 (`-16.0 LUFS`, `-1.5 dBTP`) +
   optional BGM ducking + `alimiter=limit=0.7:level=false`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from .tts_auto_heal import TTSAutoHealer, nfc

REPO_ROOT = Path(__file__).resolve().parent.parent
STICKMAN_ROOT = REPO_ROOT / "stickman-shorts"
DEFAULT_FONT_BOLD = STICKMAN_ROOT / "src" / "assets" / "fonts" / "BeVietnamPro-Bold.ttf"

TARGET_LUFS = -16.0
TRUE_PEAK = -1.5
LRA = 11


def load_episode_spec(path_or_dict: Path | str | dict) -> dict:
    """Load an episode manifest from dict, JSON, or YAML (with stdlib fallback)."""
    if isinstance(path_or_dict, dict):
        return path_or_dict
    p = Path(path_or_dict)
    raw = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json" or raw.lstrip().startswith("{"):
        return json.loads(raw)
    try:
        import yaml  # type: ignore
        return yaml.safe_load(raw)
    except ImportError:
        return _minimal_yaml_load(raw)


def _parse_scalar(val: str):
    v = val.strip()
    if not v:
        return ""
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(x) for x in inner.split(",")]
    if v.lower() in ("true", "yes"):
        return True
    if v.lower() in ("false", "no"):
        return False
    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        return v


def _minimal_yaml_load(text: str) -> dict:
    """Zero-dependency parser for flat/2-level episode YAML (`ep001/script.yaml` compatible)."""
    result: dict = {}
    cur_section: str | None = None
    cur_item: dict | None = None

    for raw_line in text.splitlines():
        # Strip full-line comments and unquoted trailing comments
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            cur_item = None
            if ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.strip()
                if not v:
                    cur_section = k
                    result[k] = []
                else:
                    cur_section = None
                    result[k] = _parse_scalar(v)
        elif cur_section is not None:
            sec = result.get(cur_section)
            if stripped.startswith("- "):
                rest = stripped[2:].strip()
                if ":" in rest and not (rest.startswith('"') or rest.startswith("'")):
                    k, v = rest.split(":", 1)
                    cur_item = {k.strip(): _parse_scalar(v)}
                    if isinstance(sec, list):
                        sec.append(cur_item)
                else:
                    cur_item = None
                    if isinstance(sec, list):
                        sec.append(_parse_scalar(rest))
            elif ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                if cur_item is not None:
                    cur_item[k] = _parse_scalar(v)
                else:
                    if isinstance(sec, list) and not sec:
                        sec = {}
                        result[cur_section] = sec
                    if isinstance(sec, dict):
                        sec[k] = _parse_scalar(v)
    return result


def measure_loudnorm_stats(audio_path: Path | str) -> dict | None:
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(audio_path),
        "-af", f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA={LRA}:print_format=json",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", proc.stderr or "")
    if not m:
        return None
    try:
        stats = json.loads(m.group(0))
        if stats.get("input_i") in (None, "-inf", "inf"):
            return None
        return stats
    except Exception:
        return None


def build_two_pass_audio_m4a(
    voice_wav: Path,
    out_m4a: Path,
    bgm_path: Path | None = None,
    bgm_volume: float = 0.12,
) -> Path:
    """Normalize voice + optional BGM to exact -16.0 LUFS / <= -1.5 dBTP via 2-pass loudnorm."""
    work_mix = out_m4a.parent / "_mix_pre_norm.wav"
    if bgm_path and bgm_path.exists():
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(voice_wav),
                "-stream_loop", "-1", "-i", str(bgm_path),
                "-filter_complex",
                f"[1:a]volume={bgm_volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "[aout]", "-ar", "48000", "-ac", "2", str(work_mix),
            ],
            check=True,
        )
    else:
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(voice_wav), "-ar", "48000", "-ac", "2", str(work_mix),
            ],
            check=True,
        )

    stats = measure_loudnorm_stats(work_mix)
    if stats:
        af = (
            f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA={LRA}"
            f":measured_I={stats['input_i']}"
            f":measured_TP={stats['input_tp']}"
            f":measured_LRA={stats['input_lra']}"
            f":measured_thresh={stats['input_thresh']}"
            f":offset={stats['target_offset']}:linear=true,"
            f"alimiter=limit=0.7:level=false"
        )
    else:
        af = f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA={LRA},alimiter=limit=0.7:level=false"

    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(work_mix), "-af", af,
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out_m4a),
        ],
        check=True,
    )
    try:
        work_mix.unlink()
    except OSError:
        pass
    return out_m4a


def _ensure_placeholder_image(out_jpg: Path, index: int) -> Path:
    """Create a clean 1080x1920 gradient/slate background frame when beat image is omitted."""
    palette = ["#14213d", "#1b263b", "#0f3460", "#22223b", "#1d3557"]
    color = palette[index % len(palette)]
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-i", f"color=c={color}:s=1080x1920:d=1",
            "-frames:v", "1", "-q:v", "2", str(out_jpg),
        ],
        check=True,
    )
    return out_jpg


def compile_visual_essay_video(
    spec: dict,
    timing: dict,
    build_dir: Path,
    font_path: Path = DEFAULT_FONT_BOLD,
) -> Path:
    """Render 1080x1920 30fps Visual Essay video (`v011_render` architecture, Windows-safe)."""
    build_dir.mkdir(parents=True, exist_ok=True)
    local_font = build_dir / "BeVietnamPro-Bold.ttf"
    if font_path.exists() and not local_font.exists():
        shutil.copy2(font_path, local_font)

    beats_spec = spec.get("beats", [])
    beats_timed = timing["beats"]
    total_dur = float(timing["duration_s"])
    fps = 30

    img_inputs: list[str] = []
    filter_lines: list[str] = []
    concat_refs: list[str] = []

    for idx, bt in enumerate(beats_timed):
        b_spec = beats_spec[idx] if idx < len(beats_spec) else {}
        src_img = b_spec.get("image")
        local_img = build_dir / f"slide_{idx:02d}.jpg"
        if src_img and Path(src_img).exists():
            shutil.copy2(src_img, local_img)
        elif not local_img.exists():
            _ensure_placeholder_image(local_img, idx)

        b_dur = max(0.5, float(bt["end_s"]) - float(bt["start_s"]))
        if idx == len(beats_timed) - 1:
            b_dur = max(b_dur, total_dur - float(bt["start_s"]) + 0.15)
        frames = max(15, int(round(b_dur * fps)))
        zoom_expr = f"1+0.08*on/{frames}" if idx % 2 == 0 else f"1.08-0.08*on/{frames}"
        img_inputs += ["-i", local_img.name]
        filter_lines.append(
            f"[{idx}:v]scale=2160:3840:force_original_aspect_ratio=increase,"
            f"crop=2160:3840:(iw-2160)/2:0,"
            f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s=1080x1920:fps={fps},format=yuv420p,setsar=1[v{idx}]"
        )
        concat_refs.append(f"[v{idx}]")

    filter_lines.append(f"{''.join(concat_refs)}concat=n={len(beats_timed)}:v=1:a=0,format=yuv420p,setsar=1[vc]")
    cur_label = "vc"
    step_i = 0

    has_font = local_font.exists()
    font_arg = "fontfile=BeVietnamPro-Bold.ttf:" if has_font else ""

    for idx, bt in enumerate(beats_timed):
        b_spec = beats_spec[idx] if idx < len(beats_spec) else {}
        st = float(bt["start_s"])
        en = float(bt["end_s"]) if idx < len(beats_timed) - 1 else total_dur
        title = nfc(b_spec.get("card_title") or bt.get("card_title") or "").strip()
        sub = nfc(b_spec.get("card_subtitle") or bt.get("card_subtitle") or "").strip()
        is_endcard = idx == len(beats_timed) - 1

        if is_endcard:
            step_i += 1
            nxt = f"h{step_i}"
            filter_lines.append(
                f"[{cur_label}]drawbox=x=0:y=0:w=1080:h=1920:color=black@0.45:t=fill:"
                f"enable='between(t,{st:.2f},{en:.2f})'[{nxt}]"
            )
            cur_label = nxt

        if title:
            txt_file = build_dir / f"card_title_{idx:02d}.txt"
            txt_file.write_text(title, encoding="utf-8")
            fsize = 72 if idx == 0 else (64 if is_endcard else 56)
            step_i += 1
            nxt = f"h{step_i}"
            filter_lines.append(
                f"[{cur_label}]drawtext={font_arg}textfile={txt_file.name}:fontsize={fsize}:"
                f"fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=22:"
                f"x=(w-text_w)/2:y=h*0.26:expansion=none:enable='between(t,{st:.2f},{en:.2f})'[{nxt}]"
            )
            cur_label = nxt

        if sub:
            sub_file = build_dir / f"card_sub_{idx:02d}.txt"
            sub_file.write_text(sub, encoding="utf-8")
            y_expr = "h*0.58" if is_endcard else "h*0.35"
            step_i += 1
            nxt = f"h{step_i}"
            filter_lines.append(
                f"[{cur_label}]drawtext={font_arg}textfile={sub_file.name}:fontsize=44:"
                f"fontcolor=white:box=1:boxcolor=black@0.50:boxborderw=16:"
                f"x=(w-text_w)/2:y={y_expr}:expansion=none:enable='between(t,{st:.2f},{en:.2f})'[{nxt}]"
            )
            cur_label = nxt

    local_ass = build_dir / "captions.ass"
    src_ass = Path(timing["captions_ass"])
    if src_ass.resolve() != local_ass.resolve():
        shutil.copy2(src_ass, local_ass)
    filter_lines.append(f"[{cur_label}]ass=captions.ass,scale=out_range=tv,format=yuv420p[vout]")

    filter_script = build_dir / "assemble_filter.txt"
    filter_script.write_text(";\n".join(filter_lines) + "\n", encoding="utf-8")

    video_only = build_dir / "raw_video.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            *img_inputs,
            "-filter_complex_script", filter_script.name,
            "-map", "[vout]",
            "-t", f"{total_dur:.3f}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-color_range", "tv", "-r", str(fps),
            video_only.name,
        ],
        cwd=str(build_dir),
        check=True,
    )
    return video_only


def generate_stickman_scene_code(spec: dict, timing: dict) -> str:
    """Compile declarative Stickman beats into a valid Manim `StickmanScene` script."""
    beats_spec = spec.get("beats", [])
    beats_timed = timing["beats"]
    total_dur = round(float(timing["duration_s"]) + 0.6, 2)

    compiled_beats = []
    for idx, bt in enumerate(beats_timed):
        bs = beats_spec[idx] if idx < len(beats_spec) else {}
        action = bs.get("action")
        if not action:
            vis = str(bs.get("visual", "")).lower()
            if idx == 0 or "surprised" in vis:
                action = "surprised_center"
            elif "di bo vao" in vis or "walk" in vis:
                action = "walk_in_sad"
            elif "think" in vis or "point" in vis:
                action = "think_to_point"
            elif "canh nhau" in vis or "side" in vis:
                action = "side_by_side"
            else:
                action = "wave_payoff"
        props = bs.get("props")
        if props is None:
            vis = str(bs.get("visual", "")).lower()
            props = [p for p in ("clock_wall", "money_bag", "coin_stack", "laptop") if p in vis]
        compiled_beats.append({
            "id": bt["id"],
            "start_s": round(float(bt["start_s"]), 3),
            "end_s": round(float(bt["end_s"]), 3),
            "card_title": nfc(bs.get("card_title") or bt.get("card_title") or ""),
            "card_subtitle": nfc(bs.get("card_subtitle") or bt.get("card_subtitle") or ""),
            "action": action,
            "props": props,
        })

    beats_json = json.dumps(compiled_beats, ensure_ascii=False, indent=2)
    stickman_root_str = repr(str(STICKMAN_ROOT))

    return f'''"""Auto-generated Stickman episode scene compiled by AgentNet V2.0 Auto-99%."""
import json
import math
import sys

sys.path.insert(0, {stickman_root_str})

from manim import UP, FadeIn, FadeOut, ValueTracker, always_redraw, config, linear
from config import GROUND_Y, SPEC
from src.rig.character import Stickman
from src.rig.gestures import point_pose, think_pose, wave_pose
from src.rig.poses import POSE_HAPPY, POSE_NEUTRAL, POSE_SAD, POSE_SURPRISED, lerp_pose
from src.rig.props import clock_wall, coin_stack, ground_line, laptop, money_bag
from src.rig.walk import walk_bob, walk_pose
from src.scenes.base_scene import StickmanScene as BaseStickmanScene
from src.scenes.text_card import TextCard
from src.utils.export import apply_video_config

apply_video_config()
config.background_color = SPEC["BG"]

BEATS = json.loads({repr(beats_json)})
TOTAL_DUR = {total_dur}
CARD_Y = 4.6
HIP_Y = GROUND_Y + SPEC["UPPER_LEG"] + SPEC["LOWER_LEG"]

PROP_BUILDERS = {{
    "clock_wall": (clock_wall, [2.9, 1.2, 0]),
    "money_bag": (money_bag, [-2.4, -3.0, 0]),
    "coin_stack": (coin_stack, [2.6, -3.25, 0]),
    "laptop": (laptop, [2.2, -3.1, 0]),
}}


class StickmanScene(BaseStickmanScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.t_now = 0.0

    def wait_until(self, t_target: float):
        rem = t_target - self.t_now
        if rem > 0.01:
            self.wait(rem)
            self.t_now += rem

    def construct(self):
        self.add(ground_line(GROUND_Y))
        prev_fades = []
        prev_updaters = []

        for idx, b in enumerate(BEATS):
            end_t = TOTAL_DUR if idx == len(BEATS) - 1 else float(b["end_s"])
            dur = max(0.8, end_t - self.t_now)

            for u in prev_updaters:
                self.remove(u)
            prev_updaters = []

            card = TextCard(b["card_title"] or "...", subtitle=b["card_subtitle"] or None)
            card.move_to([0, CARD_Y, 0])

            prop_mobs = []
            for pname in b.get("props", []):
                if pname in PROP_BUILDERS:
                    fn, pos = PROP_BUILDERS[pname]
                    m = fn(1.0)
                    m.move_to(pos)
                    prop_mobs.append(m)

            anims = [FadeOut(m) for m in prev_fades] + [FadeIn(card, shift=UP * 0.3)] + [FadeIn(p) for p in prop_mobs]
            prev_fades = [card, *prop_mobs]

            act = b["action"]
            if act == "surprised_center":
                man = Stickman(pose=POSE_SURPRISED).place(0, HIP_Y)
                self.add(man)
                prev_fades.append(man)
                self.play(*anims, run_time=0.45)
                self.t_now += 0.45
                self.wait_until(end_t)
            elif act == "walk_in_sad":
                phase_t = ValueTracker(0.0)
                sad_t = ValueTracker(0.0)
                actor = always_redraw(lambda: Stickman(
                    pose=lerp_pose(walk_pose(phase_t.get_value()), POSE_SAD, sad_t.get_value())
                ).place(-5.2 + 2.4 * min(1.0, phase_t.get_value() / (2 * math.pi)), HIP_Y + walk_bob(phase_t.get_value()) * (1.0 - sad_t.get_value())))
                self.add(actor)
                prev_updaters.append(actor)
                self.play(*anims, run_time=0.45)
                self.t_now += 0.45
                walk_rt = max(0.5, min(dur - 1.2, 4.5))
                self.play(phase_t.animate.set_value(4 * math.pi), run_time=walk_rt, rate_func=linear)
                self.t_now += walk_rt
                self.play(sad_t.animate.set_value(1.0), run_time=0.5)
                self.t_now += 0.5
                self.wait_until(end_t)
            elif act == "think_to_point":
                blend = ValueTracker(0.0)
                actor = always_redraw(lambda: Stickman(
                    pose=lerp_pose(think_pose(), point_pose(), blend.get_value())
                ).place(0.6, HIP_Y))
                self.add(actor)
                prev_updaters.append(actor)
                self.play(*anims, run_time=0.45)
                self.t_now += 0.45
                hold = max(0.3, min(1.8, (end_t - self.t_now) * 0.4))
                self.wait(hold)
                self.t_now += hold
                self.play(blend.animate.set_value(1.0), run_time=0.5)
                self.t_now += 0.5
                self.wait_until(end_t)
            elif act == "side_by_side":
                left_man = Stickman(pose=POSE_SAD).place(-2.1, HIP_Y)
                right_man = Stickman(pose=POSE_HAPPY).place(2.1, HIP_Y)
                self.add(left_man, right_man)
                prev_fades.extend([left_man, right_man])
                self.play(*anims, run_time=0.45)
                self.t_now += 0.45
                self.wait_until(end_t)
            else:
                w_phase = ValueTracker(0.0)
                actor = always_redraw(lambda: Stickman(
                    pose=wave_pose(w_phase.get_value())
                ).place(0.0, HIP_Y))
                self.add(actor)
                prev_updaters.append(actor)
                self.play(*anims, run_time=0.45)
                self.t_now += 0.45
                rem = max(0.4, end_t - self.t_now)
                self.play(w_phase.animate.set_value(4 * math.pi), run_time=rem, rate_func=linear)
                self.t_now += rem
'''


def _find_manim_python() -> str:
    candidates = [
        STICKMAN_ROOT / ".venv-win" / "Scripts" / "python.exe",
        STICKMAN_ROOT / ".venv" / "bin" / "python",
        Path(sys.executable),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return sys.executable


class EpisodeCompiler:
    """End-to-end declarative compiler: `episode.yaml` -> `final.mp4` + metadata."""

    def __init__(self, healer: TTSAutoHealer | None = None):
        self.healer = healer or TTSAutoHealer()

    def compile(
        self,
        spec_or_path: Path | str | dict,
        out_dir: Path | str,
        quality: str = "high",
    ) -> dict:
        spec = load_episode_spec(spec_or_path)
        out_path = Path(out_dir).resolve()
        build_dir = out_path / "build"
        build_dir.mkdir(parents=True, exist_ok=True)

        slug = spec.get("slug") or "auto-episode"
        title = nfc(spec.get("title") or slug)
        inferred_tpl = "stickman" if (spec.get("poses_used") or spec.get("props_used")) else "visual_essay"
        template = (spec.get("template") or inferred_tpl).lower()
        beats = spec.get("beats") or []
        if not beats:
            raise ValueError("Episode spec must define at least 1 beat")

        # Step 1: Self-Healing TTS + Whisper timing alignment (auto-selects VieNeu vs MMS)
        voice_cfg = str(spec.get("voice") or "mms").lower()
        healer = self.healer
        if ("vieneu" in voice_cfg or "mai anh" in voice_cfg) and self.healer.synth_fn is not None:
            from .tts_auto_heal import HardwareModels
            # Only swap when using default hardware synthesizer (preserve custom test mocks)
            if getattr(self.healer, "_uses_default_synth", False):
                healer = TTSAutoHealer(
                    lexicon=self.healer.lexicon,
                    synth_fn=lambda txt, rate: HardwareModels.synth_vieneu(txt, atempo=rate * 0.73),
                    base_rate=0.92,
                )
        timing = healer.synthesize_episode(
            beats=beats,
            out_dir=out_path,
            extra_fallbacks=spec.get("phrase_fallbacks"),
        )

        # Step 2: Visual compilation (Visual Essay OR Stickman Manim)
        bgm = Path(spec["bgm"]) if spec.get("bgm") else None
        final_mp4 = out_path / "final.mp4"

        if template == "stickman":
            scene_py = out_path / "generated_scene.py"
            scene_py.write_text(generate_stickman_scene_code(spec, timing), encoding="utf-8")
            manim_py = _find_manim_python()
            q_flag = "-ql" if quality == "low" else "-qh"
            media_dir = build_dir / "manim_media"
            subprocess.run(
                [
                    manim_py, "-m", "manim", "render", q_flag,
                    "--media_dir", str(media_dir),
                    str(scene_py), "StickmanScene",
                ],
                cwd=str(STICKMAN_ROOT),
                check=True,
            )
            rendered = list(media_dir.rglob("StickmanScene.mp4"))
            if not rendered:
                raise RuntimeError("Manim did not produce StickmanScene.mp4")
            raw_video = rendered[0]
            # Burn captions + 2-pass normalized audio
            audio_m4a = build_two_pass_audio_m4a(Path(timing["voice_wav"]), build_dir / "audio_final.m4a", bgm_path=bgm)
            local_ass = build_dir / "captions.ass"
            shutil.copy2(timing["captions_ass"], local_ass)
            subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", str(raw_video), "-i", str(audio_m4a),
                    "-vf", "ass=captions.ass",
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "copy",
                    "-shortest", str(final_mp4),
                ],
                cwd=str(build_dir),
                check=True,
            )
        else:
            raw_video = compile_visual_essay_video(spec, timing, build_dir=build_dir)
            audio_m4a = build_two_pass_audio_m4a(Path(timing["voice_wav"]), build_dir / "audio_final.m4a", bgm_path=bgm)
            subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", str(raw_video), "-i", str(audio_m4a),
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "copy",
                    "-shortest", str(final_mp4),
                ],
                check=True,
            )

        manifest_out = {
            "outcome": "ok",
            "slug": slug,
            "title": title,
            "template": template,
            "video_path": str(final_mp4),
            "voice_wav": timing["voice_wav"],
            "captions_ass": timing["captions_ass"],
            "timing_json": str(out_path / "timing.json"),
            "duration_s": timing["duration_s"],
            "speech_wpm": timing["speech_wpm"],
            "asr_match": timing["asr_match"],
        }
        (out_path / "episode_output.json").write_text(
            json.dumps(manifest_out, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return manifest_out
