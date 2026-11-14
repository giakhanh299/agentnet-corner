"""Analyse one short video file: probe, scene keyframes, audio, timeline report.
Tested on Big Buck Bunny (archive.org) and on downloaded TikTok/YouTube Shorts.
Requires system ffmpeg/ffprobe. Usage:
  python3 analyze_video.py <video.mp4> <out_dir>
Writes <out_dir>/timeline.md and <out_dir>/summary.json, plus
keyframes/ and audio.wav. No ASR/OCR/OpenCV: transcript needs an ASR tool
(faster-whisper CPU tiny model is the lightest option).
"""
import json, subprocess, sys
from pathlib import Path


def run(cmd, timeout=300):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def probe(path):
    p = run(['ffprobe', '-v', 'error', '-show_entries',
             'format=duration,size', '-show_entries',
             'stream=codec_name,width,height,r_frame_rate',
             '-of', 'json', str(path)])
    return json.loads(p.stdout)


def scene_keyframes(path, threshold=0.4):
    """Return scene-change timestamps via ffprobe lavfi select."""
    filt = f"movie={path},select=gt(scene\\,{threshold})"
    p = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'frame=pts_time', '-of', 'csv=p=0',
             '-f', 'lavfi', filt])
    times = []
    for line in p.stdout.splitlines():
        line = line.strip()
        if line:
            try:
                times.append(round(float(line), 3))
            except ValueError:
                pass
    return times


def extract_frames(path, times, out_dir):
    frames = []
    for i, t in enumerate(times):
        fp = out_dir / f'frame_{i:02d}_{t:.2f}s.jpg'
        run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', str(path),
             '-frames:v', '1', '-q:v', '3', str(fp)])
        if fp.exists():
            frames.append(str(fp.name))
    return frames


def extract_audio(path, out_path, duration=30):
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(path),
         '-t', str(duration), '-ac', '1', '-ar', '16000', str(out_path)])
    return out_path.exists()


def main():
    video, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    info = probe(video)
    fmt = info.get('format', {})
    streams = info.get('streams', [])
    vstream = next((s for s in streams if s.get('codec_name') and 'width' in s), {})
    duration = float(fmt.get('duration', 0) or 0)
    times = scene_keyframes(video)
    frames = extract_frames(video, times, out)
    audio_ok = extract_audio(video, out / 'audio.wav')
    summary = {
        'file': video.name,
        'size_bytes': int(fmt.get('size', 0) or 0),
        'duration_s': round(duration, 2),
        'width': vstream.get('width'),
        'height': vstream.get('height'),
        'video_codec': vstream.get('codec_name'),
        'scene_keyframes_s': times,
        'frames': frames,
        'audio_wav_30s_mono_16k': audio_ok,
        'transcript': None,
        'note': 'No ASR/OCR/OpenCV in this pipeline; first-3s hook must be judged from frames at 0/1/2s.',
    }
    (out / 'summary.json').write_text(json.dumps(summary, indent=2))
    lines = [f"# {video.name}", '',
             f"- Duration: {duration:.2f}s, {vstream.get('width')}x{vstream.get('height')} {vstream.get('codec_name')}",
             f"- Size: {summary['size_bytes']} bytes",
             f"- Scene keyframes ({len(times)}): {', '.join(str(t) for t in times)}s",
             f"- Audio: 30s mono 16kHz wav extracted: {audio_ok}",
             '- Transcript: not available (no ASR tool installed)',
             '', '## Frames', '']
    for f in frames:
        lines.append(f'- {f}')
    (out / 'timeline.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: python3 analyze_video.py <video.mp4> <out_dir>', file=sys.stderr)
        sys.exit(2)
    main()
