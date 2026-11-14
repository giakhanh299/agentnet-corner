"""Download the 100 verified candidate videos for deep analysis.
Reads candidates_compact from verify_research_payload_20261114.txt.
Priority order: the 6 directly verified TikTok pages first, then Shorts
in humor/surprise/curiosity, then the rest.
- YouTube Shorts: yt-dlp with android player client (bypasses the
  'Sign in to confirm you're not a bot' block seen with the default client).
- TikTok: default yt-dlp (slow start with retries, completes).
Skips files already downloaded; appends one JSON line per video to
download_log.jsonl so the run can resume. Usage:
  ~/workspace/agentnet-corner/venv/bin/python3 download_candidates.py
"""
import json, subprocess, sys
from pathlib import Path

BASE = Path.home() / 'workspace' / 'agentnet-corner'
OUT = BASE / 'video_downloads' / 'candidates'
LOG = BASE / 'video_downloads' / 'download_log.jsonl'
YTDLP = str(BASE / 'venv' / 'bin' / 'yt-dlp')

VERIFIED_TIKTOK = [
    'https://www.tiktok.com/@avrecap/video/7159757121213582619',
    'https://www.tiktok.com/@mrbeast/video/7705603633437527327',
    'https://www.tiktok.com/@johnspinaa/video/7706616869750459679',
    'https://www.tiktok.com/@lateese.miller/video/7706316280051059998',
    'https://www.tiktok.com/@henry_sargent_/video/7706655355748551958',
    'https://www.tiktok.com/@grwmia.o/video/7707441427575278878',
]
NICHE_ORDER = {'humor': 0, 'surprise': 1, 'curiosity': 2, 'entertainment': 3,
               'emotional storytelling': 4, 'relatable everyday life stories': 5}


def load_candidates():
    text = (BASE / 'verify_research_payload_20261114.txt').read_text()
    marker = 'RESEARCH RESULT (task ac56d158, outcome completed):\n'
    result = json.loads(text.split(marker, 1)[1])
    return result['candidates_compact']  # [url, platform, niche, channel]


def priority_key(item):
    url, platform, niche, channel = item
    if url in VERIFIED_TIKTOK:
        return (0, VERIFIED_TIKTOK.index(url))
    return (1, NICHE_ORDER.get(niche, 9), url)


def safe_name(url):
    return url.rstrip('/').split('/')[-1].replace('?', '_').replace('=', '_')[:60]


def download(url, platform, out_path):
    cmd = [YTDLP, '--no-playlist', '--socket-timeout', '30', '--retries', '3',
           '-f', 'bv*[height<=720]+ba/b[height<=720]/b',
           '-o', str(out_path), url]
    if 'youtube.com' in url:
        cmd[1:1] = ['--extractor-args', 'youtube:player_client=android']
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return p.returncode, (p.stdout + p.stderr)[-800:]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cands = sorted(load_candidates(), key=priority_key)
    print(f'{len(cands)} candidates, priority order: 6 verified TikTok first', flush=True)
    done = failed = 0
    with LOG.open('a') as log:
        for i, (url, platform, niche, channel) in enumerate(cands, 1):
            tag = 'tiktok' if 'tiktok.com' in url else 'shorts'
            out_path = OUT / f'{i:03d}_{tag}_{safe_name(url)}.mp4'
            if out_path.exists() and out_path.stat().st_size > 100000:
                print(f'[{i}/{len(cands)}] skip (exists) {url}', flush=True)
                done += 1
                continue
            rc, tail = download(url, platform, out_path)
            ok = rc == 0 and out_path.exists() and out_path.stat().st_size > 100000
            rec = {'i': i, 'url': url, 'platform': platform, 'niche': niche,
                   'channel': channel, 'ok': ok,
                   'bytes': out_path.stat().st_size if out_path.exists() else 0}
            log.write(json.dumps(rec, ensure_ascii=False) + '\n')
            log.flush()
            print(f'[{i}/{len(cands)}] {"OK " if ok else "FAIL"} {rec["bytes"]}B {url}', flush=True)
            if ok:
                done += 1
            else:
                failed += 1
                print('  last output:', tail.replace('\n', ' | ')[-400:], flush=True)
    print(f'DONE ok={done} failed={failed}', flush=True)


if __name__ == '__main__':
    main()
