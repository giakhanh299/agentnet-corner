"""Analyse one short video file: probe, scene keyframes, audio, timeline report.
Tested on Big Buck Bunny (archive.org) and on downloaded TikTok/YouTube Shorts.
Requires system ffmpeg/ffprobe. Usage:
  python3 analyze_video.py <video.mp4> <out_dir>
Writes <out_dir>/timeline.md and <out_dir>/summary.json, plus scene and hook
images and audio.wav (if the input has audio). The transcript needs an ASR tool
(faster-whisper CPU tiny model is the lightest option).
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


FRAME_NAME = re.compile(r'(?:frame|hook)_\d{2,}_\d+\.\d{2}s\.jpg')


def run(cmd, timeout=300):
    result = subprocess.run(cmd, capture_output=True, encoding='utf-8',
                            errors='replace', timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'{cmd[0]} failed: {result.stderr.strip()}')
    return result


def probe(path):
    p = run(['ffprobe', '-v', 'error', '-show_entries',
             'format=duration,size', '-show_entries',
             'stream=codec_type,codec_name,width,height,r_frame_rate',
             '-of', 'json', str(path)])
    return json.loads(p.stdout)


def scene_keyframes(path, threshold=0.4):
    """Return scene-change timestamps from FFmpeg's scene filter."""
    filt = (f"select=gt(scene\\,{threshold}),"
            "metadata=mode=print:key=lavfi.scene_score:file=-")
    result = run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
                  '-vf', filt, '-f', 'null', '-'])
    return [round(float(t), 3) for t in re.findall(r'\bpts_time:(\S+)', result.stdout)]


def extract_frames(path, times, out_dir, prefix='frame'):
    frames = []
    for i, t in enumerate(times):
        fp = out_dir / f'{prefix}_{i:02d}_{t:.2f}s.jpg'
        run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', str(path),
             '-map', '0:v:0', '-frames:v', '1', '-q:v', '3', str(fp)])
        if fp.exists() and fp.stat().st_size:
            frames.append(fp.name)
    return frames


def extract_audio(path, out_path, duration=30):
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(path),
         '-map', '0:a:0', '-t', str(duration), '-ac', '1', '-ar', '16000', str(out_path)])
    return out_path.exists() and out_path.stat().st_size > 0


def analyze(video, out):
    info = probe(video)
    fmt = info.get('format', {})
    streams = info.get('streams', [])
    vstream = next((s for s in streams if s.get('codec_type') == 'video'), None)
    if vstream is None:
        raise RuntimeError('Input has no video stream')
    duration = float(fmt.get('duration', 0) or 0)
    times = scene_keyframes(video)
    frames = extract_frames(video, times, out)
    hook_times = [t for t in (0, 1, 2) if not duration or t < duration]
    hook_frames = extract_frames(video, hook_times, out, prefix='hook')
    audio = out / 'audio.wav'
    audio_ok = any(s.get('codec_type') == 'audio' for s in streams) and extract_audio(video, audio)
    summary = {
        'file': video.name,
        'size_bytes': int(fmt.get('size', 0) or 0),
        'duration_s': round(duration, 2),
        'width': vstream.get('width'),
        'height': vstream.get('height'),
        'video_codec': vstream.get('codec_name'),
        'scene_keyframes_s': times,
        'frames': frames,
        'hook_frames': hook_frames,
        'audio_wav_30s_mono_16k': audio_ok,
        'transcript': None,
        'note': 'No ASR/OCR/OpenCV in this pipeline; first-3s hook must be judged from frames at 0/1/2s.',
    }
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    lines = [f"# {video.name}", '',
             f"- Duration: {duration:.2f}s, {vstream.get('width')}x{vstream.get('height')} {vstream.get('codec_name')}",
             f"- Size: {summary['size_bytes']} bytes",
             f"- Scene keyframes ({len(times)}): {', '.join(str(t) for t in times)}s",
             f"- Audio: 30s mono 16kHz wav extracted: {audio_ok}",
             '- Transcript: run ASR separately.',
             '', '## Hook frames', '']
    lines.extend(f'- {name}' for name in hook_frames)
    lines.extend(['', '## Scene-change frames', ''])
    lines.extend(f'- {name}' for name in frames)
    (out / 'timeline.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return summary


def main():
    video, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='.analysis-', dir=out) as temp:
        staging = Path(temp)
        summary = analyze(video, staging)
        for old in out.iterdir():
            generated_media = old.name == 'audio.wav' or FRAME_NAME.fullmatch(old.name)
            if generated_media and old.is_file() and not (staging / old.name).exists():
                old.unlink()
        for artifact in staging.iterdir():
            if artifact.name != 'summary.json':
                artifact.replace(out / artifact.name)
        (staging / 'summary.json').replace(out / 'summary.json')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: python3 analyze_video.py <video.mp4> <out_dir>', file=sys.stderr)
        sys.exit(2)
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
        sys.exit(str(exc))
