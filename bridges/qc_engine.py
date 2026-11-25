"""Tier-1 Local Deterministic QC Engine (0-token · Python/FFmpeg/OpenCV/OCR) for 12 Facebook channels.

Strictly READ-ONLY toward all source video/image folders in D:/0.1_FACE_BOOK.
All JSON reports and lightweight contact sheets are written ONLY to RAG/data/qc_reports/.

Implements Codex 23:48 Section 2 & Muse Wave-1 specs:
- Container/Aspect-Ratio/Distortion & A/V sync drift (ffprobe) — catches K01 distortion
- Audio Loudness (ebur128), True Peak clipping, silence, & Voice-band (300-3400Hz) vs BGM ratio
  (supports both mixed clip check AND dual-stem voice/BGM check for K04 OmniVoice)
- Visual frames, black/frozen frame checks, 3x2 timestamped contact sheet (L006 + single-pass Muse review)
- Blur-box alignment & face/hair encroachment (OpenCV Laplacian + Haar face cascade) — catches K02/K05/K06
- Camera-compensated OCR stability & confidence (phaseCorrelate + scene-cut reset) — catches K07/K11
- SHA-256 + 64-bit visual dHash identity — catches renamed duplicates (K01/K10)
- K10 Morning Auto-Publish Hard-QC Relevance Gate (allowlist/blocklist + 0-100 rubric + 24h dedup)
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import unicodedata

import cv2
import numpy as np

RAG_ROOT = Path(__file__).resolve().parent
REPORTS_DIR = RAG_ROOT / 'data' / 'qc_reports'
SHEETS_DIR = REPORTS_DIR / 'sheets'
TZ = dt.timezone(dt.timedelta(hours=7))

POLICY_VERSION = 'qc-v1.0-20261122'

# K10 Hard-QC Relevance Rules (calibrated for Người Đưa Tin 24H morning auto-publish 06:00/07:00/09:00)
K10_DEFAULT_RULES = {
    'policy_version': 'k10-rel-v1.0',
    'pass_threshold': 80,
    'allow_topics': [
        'thoi su', 'kinh te', 'tai chinh', 'xa hoi', 'giao thong', 'chinh sach', 'phap luat',
        'cong nghe', 'ai', 'gia vang', 'xang dau', 'bat dong san', 'y te', 'giao duc', 'thoi tiet',
        'con bao', 'mua bao', 'lu lut', 'quoc te', 'chung khoan', 'ngan hang', 'lai suat', 'lao dong', 'viec lam',
        'an ninh', 'canh bao', 'lua dao', 'gia ca', 'thi truong', 'viet nam', 'ha noi', 'tp hcm',
    ],
    'hard_block_keywords': [
        'anh 7', 'anh bay', 'ronaldo', 'cr7', 'messi', 'mbappe', 'bong da', 'premier league',
        'ngoai hang anh', 'qua bong vang', 'world cup', 'champions league', 'phat den',
        'chelsea', 'arsenal', 'man united', 'quy do', 'phao thu', 'ga trong', 'spurs', 'al nassr', 'newcastle',
        'showbiz', 'scandal ca si', 'drama nguoi dep',
        'hoa hau', 'tinh ai', 'ban gai tin don', 'game thu', 'esport', 'lien quan mobile',
        'free fire', 'truyen tranh', 'anime', 'review phim', 'boi toan', 'tu vi 12 con giap',
        'xo so', 'lo de', 'ca cuoc',
    ],
    'soft_penalty_keywords': [
        'hai huoc', 'viral tiktok', 'netizen tranh cai', 'cu dan mang soc', 'bat ngo nhan sac',
        'thu hut trieu view', 'chuyen la',
    ],
}

_OCR_READER = None
_FACE_CASCADE = None


def _fold(text: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFKD', str(text).lower().replace('đ', 'd'))
        if not unicodedata.combining(c)
    )


def _run_cmd(cmd: list[str], timeout: int = 35) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
            stdin=subprocess.DEVNULL, timeout=timeout,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
        return r.returncode, r.stdout, r.stderr
    except (OSError, subprocess.SubprocessError) as exc:
        return -1, '', f'{type(exc).__name__}: {exc}'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def dhash_frame(frame_bgr: np.ndarray, hash_size: int = 8) -> str:
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
    diff = resized[:, 1:] > resized[:, :-1]
    bits = ''.join('1' if b else '0' for b in diff.flatten())
    return f'{int(bits, 2):0{hash_size * hash_size // 4}x}'


def _get_face_cascade():
    global _FACE_CASCADE
    if _FACE_CASCADE is None:
        xml = Path(cv2.data.haarcascades) / 'haarcascade_frontalface_default.xml'
        if xml.is_file():
            _FACE_CASCADE = cv2.CascadeClassifier(str(xml))
        else:
            _FACE_CASCADE = False
    return _FACE_CASCADE if _FACE_CASCADE is not False else None


def _get_ocr():
    global _OCR_READER
    if _OCR_READER is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _OCR_READER = RapidOCR()
        except Exception:
            _OCR_READER = False
    return _OCR_READER if _OCR_READER is not False else None


def probe_media(path: Path) -> dict:
    rc, out, err = _run_cmd([
        'ffprobe', '-v', 'error', '-print_format', 'json',
        '-show_format', '-show_streams', str(path),
    ], timeout=15)
    if rc != 0 or not out.strip():
        return {'ok': False, 'error': err[:200] or 'ffprobe_failed'}
    data = json.loads(out)
    v_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)
    a_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), None)
    fmt = data.get('format') or {}
    w = int(v_stream.get('width', 0)) if v_stream else 0
    h = int(v_stream.get('height', 0)) if v_stream else 0
    v_dur = float(v_stream.get('duration') or fmt.get('duration') or 0) if v_stream else 0.0
    a_dur = float(a_stream.get('duration') or fmt.get('duration') or 0) if a_stream else 0.0
    sar = (v_stream.get('sample_aspect_ratio') or '1:1') if v_stream else '1:1'
    dar = (v_stream.get('display_aspect_ratio') or '') if v_stream else ''
    fps = 0.0
    if v_stream and v_stream.get('avg_frame_rate') and '/' in str(v_stream['avg_frame_rate']):
        n, d = v_stream['avg_frame_rate'].split('/', 1)
        if float(d) > 0:
            fps = round(float(n) / float(d), 2)
    return {
        'ok': True,
        'width': w,
        'height': h,
        'sar': sar,
        'dar': dar,
        'aspect_ratio': round(w / h, 4) if h else 0.0,
        'fps': fps,
        'has_audio': a_stream is not None,
        'video_duration_s': round(v_dur, 2),
        'audio_duration_s': round(a_dur, 2),
        'av_sync_diff_s': round(abs(v_dur - a_dur), 2) if (v_stream and a_stream) else None,
        'size_bytes': int(fmt.get('size') or path.stat().st_size),
    }


def analyze_audio(path: Path, sample_seconds: int = 35, channel: str = '') -> dict:
    """Measure Integrated LUFS, True Peak, clipping, and voice-band (300-3400Hz) vs non-voice BGM energy."""
    # 1) Full-band ebur128 loudness & true peak
    rc, _, err = _run_cmd([
        'ffmpeg', '-hide_banner', '-nostats', '-t', str(sample_seconds),
        '-i', str(path), '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-',
    ], timeout=25)
    if rc != 0:
        return {'ok': False, 'error': 'ffmpeg_audio_failed'}

    m_i = re.findall(r'I:\s*(-?\d+(?:\.\d+)?)\s*LUFS', err)
    m_lra = re.findall(r'LRA:\s*(-?\d+(?:\.\d+)?)\s*LU', err)
    m_tp = re.findall(r'Peak:\s*(-?\d+(?:\.\d+)?)\s*dBFS', err)
    lufs = float(m_i[-1]) if m_i else None
    lra = float(m_lra[-1]) if m_lra else None
    true_peak = float(m_tp[-1]) if m_tp else None

    # 2) Band energy comparison: vocal band (300-3400Hz) vs bass/sub-bass BGM band (<250Hz)
    _, _, err_v = _run_cmd([
        'ffmpeg', '-hide_banner', '-nostats', '-t', str(sample_seconds),
        '-i', str(path), '-vn', '-af', 'highpass=f=300,lowpass=f=3400,volumedetect', '-f', 'null', '-',
    ], timeout=20)
    _, _, err_b = _run_cmd([
        'ffmpeg', '-hide_banner', '-nostats', '-t', str(sample_seconds),
        '-i', str(path), '-vn', '-af', 'lowpass=f=240,volumedetect', '-f', 'null', '-',
    ], timeout=20)
    mv = re.search(r'mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB', err_v)
    mb = re.search(r'mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB', err_b)
    voice_db = float(mv.group(1)) if mv else None
    low_bgm_db = float(mb.group(1)) if mb else None
    voice_minus_bgm = round(voice_db - low_bgm_db, 2) if (voice_db is not None and low_bgm_db is not None) else None

    issues = []
    if lufs is None or lufs < -40.0:
        issues.append('AUDIO_SILENT_OR_TOO_QUIET')
    elif lufs > -9.0:
        issues.append('AUDIO_TOO_LOUD')
    if true_peak is not None and true_peak > -0.3:
        issues.append('AUDIO_CLIPPING')
    narration_chs = {'KENH_001', 'KENH_003', 'KENH_004'}
    v_b_floor = 3.0 if str(channel or '').upper() in narration_chs else 0.5
    if voice_minus_bgm is not None and voice_minus_bgm < v_b_floor:
        issues.append(f'BGM_OVERPOWERING_VOICE(v-b={voice_minus_bgm}dB<{v_b_floor}dB)')

    return {
        'ok': True,
        'integrated_lufs': lufs,
        'lra_lu': lra,
        'true_peak_dbfs': true_peak,
        'voice_band_mean_db': voice_db,
        'low_bgm_mean_db': low_bgm_db,
        'voice_minus_low_bgm_db': voice_minus_bgm,
        'issues': issues,
    }


def analyze_dual_stems(voice_path: Path, bgm_path: Path) -> dict:
    """Direct 2-track loudness comparison for K04 (OmniVoice stem vs BGM stem before mix)."""
    v = analyze_audio(voice_path)
    b = analyze_audio(bgm_path)
    if not v.get('ok') or not b.get('ok'):
        return {'ok': False, 'voice': v, 'bgm': b}
    vl, bl = v.get('integrated_lufs'), b.get('integrated_lufs')
    delta = round(vl - bl, 2) if (vl is not None and bl is not None) else None
    issues = []
    if delta is not None and delta < 12.0:
        issues.append(f'STEM_BGM_TOO_LOUD (voice-bgm={delta} LU < 12 LU)')
    return {'ok': True, 'voice_lufs': vl, 'bgm_lufs': bl, 'delta_lu': delta, 'issues': issues}


def _build_contact_sheet(frames: list[tuple[float, np.ndarray]], out_path: Path) -> str:
    if not frames:
        return ''
    cols, rows = 3, 2
    cell_w, cell_h = 360, 640
    # Adapt cell orientation to source frames
    fh, fw = frames[0][1].shape[:2]
    if fw > fh:
        cell_w, cell_h = 480, 270
    canvas = np.zeros((rows * cell_h, cols * cell_w, 3), dtype=np.uint8)
    for idx, (ts, img) in enumerate(frames[:cols * rows]):
        r, c = divmod(idx, cols)
        thumb = cv2.resize(img, (cell_w, cell_h), interpolation=cv2.INTER_AREA)
        cv2.rectangle(thumb, (6, 6), (118, 36), (0, 0, 0), -1)
        cv2.putText(thumb, f'{ts:05.1f}s', (12, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
        canvas[r * cell_h:(r + 1) * cell_h, c * cell_w:(c + 1) * cell_w] = thumb
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
    return str(out_path)


def analyze_visual_and_ocr(path: Path, channel: str = '', *, run_ocr: bool = True,
                           make_sheet: bool = True, max_frames: int = 6) -> dict:
    """Inspect real video frames: black/freeze, blur/face encroachment, camera-compensated OCR jitter."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return {'ok': False, 'error': 'cv2_open_failed'}

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    dur = (total_frames / fps) if (total_frames > 0 and fps > 0) else 0.0
    if total_frames <= 0:
        cap.release()
        return {'ok': False, 'error': 'empty_video_stream'}

    # Always include a real 0-3s opening hook frame (1.5s or 4% of duration) as Frame #1
    # (learned from Muse W2-01 pilot & verify acdef78f!), followed by evenly spaced frames across timeline
    hook_f = min(total_frames - 1, max(0, int(min(1.5, dur * 0.04) * fps)))
    sample_indices = [hook_f] + [
        min(total_frames - 1, max(0, int(frac * total_frames)))
        for frac in np.linspace(0.18, 0.92, max(1, max_frames - 1))
    ]
    sampled: list[tuple[float, np.ndarray]] = []
    for fidx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fidx)
        ok, frame = cap.read()
        if ok and frame is not None:
            sampled.append((round(fidx / fps, 2), frame))

    # Also grab a tight 4-frame burst around 40% (step ~0.4s) for camera-compensated OCR jitter check (K07/K11)
    burst: list[tuple[float, np.ndarray]] = []
    if run_ocr and total_frames > int(fps * 2):
        base_f = int(total_frames * 0.40)
        step_f = max(2, int(fps * 0.4))
        for k in range(4):
            fidx = min(total_frames - 1, base_f + k * step_f)
            cap.set(cv2.CAP_PROP_POS_FRAMES, fidx)
            ok, frame = cap.read()
            if ok and frame is not None:
                burst.append((round(fidx / fps, 2), frame))
    cap.release()

    if not sampled:
        return {'ok': False, 'error': 'no_frames_decoded'}

    black_ts, blur_face_ts, sharp_vals = [], [], []
    frozen_pairs = 0
    face_cascade = _get_face_cascade()
    prev_gray = None
    mid_dhash = dhash_frame(sampled[len(sampled) // 2][1])

    for ts, frame in sampled:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_luma = float(gray.mean())
        if mean_luma < 12.0:
            black_ts.append(ts)
        if prev_gray is not None and prev_gray.shape == gray.shape:
            mad = float(np.abs(gray.astype(np.float32) - prev_gray.astype(np.float32)).mean())
            if mad < 0.8:
                frozen_pairs += 1
        prev_gray = gray

        h, w = gray.shape
        # Sharpness across bands
        lap_full = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        lap_sub = float(cv2.Laplacian(gray[int(h * 0.72):int(h * 0.96), :], cv2.CV_64F).var())
        sharp_vals.append({'t': ts, 'full_lap': round(lap_full, 1), 'sub_band_lap': round(lap_sub, 1)})

        # Face blur encroachment check (K02/K05/K06)
        if face_cascade is not None:
            small = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)
            faces = face_cascade.detectMultiScale(small, scaleFactor=1.15, minNeighbors=5, minSize=(30, 30))
            for (fx, fy, fw, fh) in faces[:2]:
                roi = small[fy:fy + fh, fx:fx + fw]
                face_lap = float(cv2.Laplacian(roi, cv2.CV_64F).var())
                # If a detected face is dramatically softer than the rest of the frame, blur may have hit the face
                if lap_full > 80.0 and face_lap < lap_full * 0.12 and face_lap < 18.0:
                    blur_face_ts.append({'t': ts, 'face_lap': round(face_lap, 1), 'frame_lap': round(lap_full, 1)})

    # Camera-compensated OCR stability, confidence & ZONE-AWARE CJK leak policy (Codex 01:31!)
    # Subtitle/caption erasure zones: top band [0.00..0.26] & bottom band [0.68..1.00].
    # Mid-frame CJK (0.26 < y_rel < 0.68, e.g. shop sign/prop) -> CAN_XEM review, NEVER blind FAIL!
    ocr_info = {
        'ran': False, 'boxes_total': 0, 'matched_pairs': 0, 'mean_conf': None,
        'max_jitter_px': None, 'scene_cuts': 0, 'low_conf_ts': [],
        'cjk_leak_ts': [], 'cjk_outside_zone_ts': [],
    }
    cjk_re = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
    ocr_engine = _get_ocr() if run_ocr else None
    if ocr_engine is not None and sampled:
        ocr_info['ran'] = True
        confs, jitters = [], []
        # 1) Check ALL 6 sampled timeline frames for CJK chars, classifying inside vs outside subtitle zone
        for ts, frame in sampled:
            h, w = frame.shape[:2]
            scale = min(1.0, 720.0 / max(w, 1))
            img_s = cv2.resize(frame, (int(w * scale), int(h * scale))) if scale < 1.0 else frame
            hs = max(img_s.shape[0], 1)
            res_s, _ = ocr_engine(img_s)
            saw_in, saw_out = False, False
            for b in (res_s or []):
                if len(b) < 3:
                    continue
                pts, txt_s, conf_s = b[0], str(b[1] or ''), float(b[2])
                if not cjk_re.search(txt_s) or conf_s < 0.55:
                    continue
                cy_rel = (sum(p[1] for p in pts) / 4.0) / hs
                in_sub_zone = (cy_rel <= 0.26) or (cy_rel >= 0.68)
                entry = {'t': ts, 'text': txt_s[:30], 'conf': round(conf_s, 3), 'y_rel': round(cy_rel, 3), 'in_zone': in_sub_zone}
                if in_sub_zone and not saw_in:
                    ocr_info['cjk_leak_ts'].append(entry)
                    saw_in = True
                elif not in_sub_zone and not saw_out:
                    ocr_info['cjk_outside_zone_ts'].append(entry)
                    saw_out = True
        # 2) Tight burst around 40% for camera-compensated bbox jitter
        prev_g, prev_hist, prev_items = None, None, []

        def _text_sim(a: str, b: str) -> float:
            ta, tb = set(_fold(a).split()), set(_fold(b).split())
            if not ta or not tb:
                return 0.0
            return len(ta & tb) / max(len(ta | tb), 1)

        for ts, frame in burst:
            h, w = frame.shape[:2]
            scale = min(1.0, 720.0 / max(w, 1))
            img_s = cv2.resize(frame, (int(w * scale), int(h * scale))) if scale < 1.0 else frame
            g = cv2.cvtColor(img_s, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([g], [0], None, [32], [0, 256])
            cv2.normalize(hist, hist)

            dx, dy = 0.0, 0.0
            scene_cut = False
            if prev_g is not None and prev_g.shape == g.shape:
                corr = float(cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL))
                if corr < 0.60:
                    scene_cut = True
                    ocr_info['scene_cuts'] += 1
                    prev_items = []
                else:
                    (dx, dy), _ = cv2.phaseCorrelate(np.float32(prev_g), np.float32(g))

            res, _ = ocr_engine(img_s)
            boxes = res or []
            ocr_info['boxes_total'] += len(boxes)
            cur_items = []
            f_confs = []
            for b in boxes:
                if len(b) < 3:
                    continue
                pts, txt, conf = b[0], str(b[1] or '').strip(), float(b[2])
                f_confs.append(conf)
                cx = sum(p[0] for p in pts) / 4.0
                cy = sum(p[1] for p in pts) / 4.0
                cur_items.append((txt, cx, cy))
            if f_confs:
                confs.extend(f_confs)
                if (sum(f_confs) / len(f_confs)) < 0.65:
                    ocr_info['low_conf_ts'].append({'t': ts, 'avg_conf': round(sum(f_confs) / len(f_confs), 3)})

            # Compare only boxes with matching text (>=0.55 similarity) to avoid false jumps on new subtitle lines
            if prev_items and cur_items and not scene_cut:
                for txt, cx, cy in cur_items:
                    best = None
                    best_sim = 0.55
                    for ptxt, pcx, pcy in prev_items:
                        sim = _text_sim(txt, ptxt)
                        if sim >= best_sim:
                            best_sim = sim
                            best = (pcx, pcy)
                    if best is not None:
                        ocr_info['matched_pairs'] += 1
                        res_shift = float(np.hypot((cx - best[0]) - dx, (cy - best[1]) - dy))
                        jitters.append(round(res_shift / max(scale, 0.1), 1))
            prev_items = cur_items
            prev_g, prev_hist = g, hist
        if confs:
            ocr_info['mean_conf'] = round(sum(confs) / len(confs), 3)
        if jitters:
            ocr_info['max_jitter_px'] = max(jitters)

    issues = []
    if len(black_ts) >= 2:
        issues.append(f'BLACK_FRAMES@{black_ts}')
    if frozen_pairs >= max(2, len(sampled) - 2):
        issues.append('FROZEN_VIDEO')
    if blur_face_ts:
        issues.append(f'BLUR_ON_FACE@{[x["t"] for x in blur_face_ts]}')
    if ocr_info['mean_conf'] is not None and ocr_info['mean_conf'] < 0.68:
        issues.append(f"OCR_LOW_CONF({ocr_info['mean_conf']})")
    if ocr_info['max_jitter_px'] is not None and ocr_info['max_jitter_px'] > 28.0:
        issues.append(f"OCR_JITTER_HIGH({ocr_info['max_jitter_px']}px)")
    if ocr_info.get('cjk_leak_ts'):
        ts_list = [x['t'] for x in ocr_info['cjk_leak_ts']]
        issues.append(f"CJK_CHINESE_LEAK@{ts_list}")
    if ocr_info.get('cjk_outside_zone_ts'):
        ts_out = [x['t'] for x in ocr_info['cjk_outside_zone_ts']]
        issues.append(f"CJK_OUTSIDE_ZONE_REVIEW@{ts_out}")

    sheet_path = ''
    if make_sheet:
        slug = re.sub(r'[^a-zA-Z0-9_-]+', '_', path.stem)[:40]
        sheet_path = _build_contact_sheet(sampled, SHEETS_DIR / f'{channel or "GEN"}_{slug}_sheet.jpg')

    return {
        'ok': True,
        'dhash': mid_dhash,
        'frames_sampled': len(sampled),
        'duration_est_s': round(dur, 2),
        'black_frame_ts': black_ts,
        'frozen_pairs': frozen_pairs,
        'sharpness_samples': sharp_vals,
        'blur_face_hits': blur_face_ts,
        'ocr': ocr_info,
        'contact_sheet': sheet_path,
        'issues': issues,
    }


def check_k10_relevance(
    title: str,
    caption: str = '',
    transcript: str = '',
    *,
    source_url: str = '',
    age_hours: float | None = None,
    recent_titles: list[str] | None = None,
    rules: dict | None = None,
) -> dict:
    """Hard-QC Relevance Gate for K10 (Người Đưa Tin 24H) morning auto-publish slots (06:00/07:00/09:00).

    Fail-closed: returns REJECT on hard blocklist, HOLD if score < 80 or missing freshness/dup, PASS only if >= 80.
    """
    cfg = rules or K10_DEFAULT_RULES
    combined = _fold(f'{title} {caption} {transcript}')
    reasons: list[str] = []

    # 1) Hard blocklist (off-topic sports / Ronaldo "Anh 7" / showbiz / horoscope)
    blocked = [kw for kw in cfg['hard_block_keywords'] if re.search(r'(?<!\w)' + re.escape(_fold(kw)) + r'(?!\w)', combined)]
    if blocked:
        return {
            'verdict': 'REJECT',
            'score': 0,
            'policy_version': cfg['policy_version'],
            'allow_auto_publish': False,
            'blocked_keywords': blocked,
            'reasons': [f'Chặn cứng chủ đề ngoài lề: {", ".join(blocked)}'],
        }

    # 2) Duplicate title check against 24h recent news
    norm_t = _fold(title).strip()
    for old in (recent_titles or []):
        old_n = _fold(old).strip()
        if not old_n:
            continue
        w1, w2 = set(norm_t.split()), set(old_n.split())
        if w1 and w2 and (len(w1 & w2) / max(len(w1 | w2), 1)) >= 0.72:
            return {
                'verdict': 'HOLD',
                'score': 25,
                'policy_version': cfg['policy_version'],
                'allow_auto_publish': False,
                'reasons': [f'Trùng tin 24h gần đây: "{old[:60]}"'],
            }

    score = 55
    allow_hits = [kw for kw in cfg['allow_topics'] if re.search(r'(?<!\w)' + re.escape(_fold(kw)) + r'(?!\w)', combined)]
    if allow_hits:
        score += min(35, 15 + 7 * (len(allow_hits) - 1))
    else:
        score -= 20
        reasons.append('Không khớp chủ đề thời sự/kinh tế/xã hội được phép')

    soft_hits = [kw for kw in cfg['soft_penalty_keywords'] if _fold(kw) in combined]
    if soft_hits:
        score -= min(30, 15 * len(soft_hits))
        reasons.append(f'Tín hiệu giật gân/giải trí: {", ".join(soft_hits)}')

    if source_url:
        score += 10
    else:
        score -= 5
        reasons.append('Thiếu URL nguồn kiểm chứng')

    if age_hours is not None:
        if age_hours > 24.0:
            score -= 30
            reasons.append(f'Tin cũ quá 24h ({age_hours:.1f}h)')
        elif age_hours <= 12.0:
            score += 5

    score = max(0, min(100, score))
    threshold = int(cfg.get('pass_threshold', 80))
    verdict = 'PASS' if score >= threshold else 'HOLD'
    return {
        'verdict': verdict,
        'score': score,
        'threshold': threshold,
        'policy_version': cfg['policy_version'],
        'allow_auto_publish': verdict == 'PASS',
        'allow_hits': allow_hits,
        'reasons': reasons,
    }


def qc_video(path: str | Path, channel: str = '', *, expected_ratio: float | None = None,
             run_ocr: bool = True, make_sheet: bool = True, known_shas: set[str] | None = None) -> dict:
    """Run complete Tier-1 deterministic QC on a single local video (strictly read-only)."""
    t0 = time.perf_counter()
    p = Path(path)
    if not p.is_file():
        return {'verdict': 'FAIL', 'error': f'FILE_NOT_FOUND: {p}', 'elapsed_ms': 0}

    sha = sha256_file(p)
    media = probe_media(p)
    audio = analyze_audio(p, channel=channel) if media.get('has_audio') else {'ok': False, 'issues': ['NO_AUDIO_STREAM']}
    visual = analyze_visual_and_ocr(p, channel=channel, run_ocr=run_ocr, make_sheet=make_sheet)

    fail_reasons, warn_reasons = [], []
    score = 55  # Tier-1 physical max = 55 pts (matches Wave-1 W1-06 rubric)

    if known_shas and sha in known_shas:
        fail_reasons.append(f'DUPLICATE_SHA256({sha[:12]})')
        score -= 30

    if not media.get('ok') or media.get('width', 0) <= 0:
        fail_reasons.append('CORRUPT_OR_UNREADABLE_VIDEO')
        score = 0
    else:
        ar = media['aspect_ratio']
        # Accept standard 9:16 (0.5625), 16:9 (1.7778), 4:5 (0.8), or 1:1 unless explicit expected_ratio is forced
        std_ratios = [expected_ratio] if expected_ratio else [9 / 16, 16 / 9, 4 / 5, 1.0]
        min_dev = min(abs(ar - r) / r for r in std_ratios if r)
        if min_dev > 0.08:
            fail_reasons.append(f'ASPECT_RATIO_DISTORTED({media["width"]}x{media["height"]}, sar={media["sar"]})')
            score -= 12
        if media.get('sar') not in ('1:1', '0:1', 'N/A', ''):
            fail_reasons.append(f"NON_SQUARE_PIXEL_SAR({media['sar']})")
            score -= 10
        if media.get('av_sync_diff_s') is not None and media['av_sync_diff_s'] > 0.8:
            warn_reasons.append(f"AV_DURATION_DRIFT({media['av_sync_diff_s']}s)")
            score -= 5
        if media.get('video_duration_s', 0) < 5.0:
            fail_reasons.append(f"TOO_SHORT({media['video_duration_s']}s)")
            score -= 15

    for iss in (audio.get('issues') or []):
        if iss in ('NO_AUDIO_STREAM', 'AUDIO_SILENT_OR_TOO_QUIET', 'AUDIO_CLIPPING'):
            fail_reasons.append(iss)
            score -= 15
        else:
            warn_reasons.append(iss)
            score -= 8

    for iss in (visual.get('issues') or []):
        if iss.startswith(('BLACK_FRAMES', 'FROZEN_VIDEO', 'BLUR_ON_FACE', 'CJK_CHINESE_LEAK')):
            fail_reasons.append(iss)
            score -= 15
        else:
            warn_reasons.append(iss)
            score -= 7

    score = max(0, score)
    if fail_reasons:
        verdict = 'FAIL'
    elif warn_reasons:
        verdict = 'CAN_XEM'
    else:
        verdict = 'PASS'

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    return {
        'checked_at': dt.datetime.now(TZ).isoformat(timespec='seconds'),
        'policy_version': POLICY_VERSION,
        'channel': channel,
        'file_name': p.name,
        'path': str(p),
        'sha256': sha,
        'dhash': visual.get('dhash', ''),
        'verdict': verdict,
        'score_tier1': score,
        'score_tier1_max': 55,
        'fail_reasons': fail_reasons,
        'warn_reasons': warn_reasons,
        'media': media,
        'audio': audio,
        'visual': visual,
        'contact_sheet': visual.get('contact_sheet', ''),
        'elapsed_ms': elapsed_ms,
    }


def run_benchmark(sample_specs: list[dict], *, save_name: str = 'benchmark_p1_latest.json',
                  run_ocr: bool = True) -> dict:
    """Run Tier-1 QC across a batch of real good/bad samples and compute p95 latency & detection rates."""
    items = []
    latencies = []
    for sp in sample_specs:
        rep = qc_video(
            sp['path'],
            channel=sp.get('channel', ''),
            expected_ratio=sp.get('expected_ratio'),
            run_ocr=run_ocr,
            make_sheet=sp.get('make_sheet', True),
            known_shas=sp.get('known_shas'),
        )
        rep['expected_bucket'] = sp.get('bucket', 'unknown')  # 'good' | 'bad'
        items.append(rep)
        latencies.append(rep['elapsed_ms'])

    latencies_sorted = sorted(latencies)
    p95 = latencies_sorted[min(len(latencies_sorted) - 1, int(len(latencies_sorted) * 0.95))] if latencies_sorted else 0.0
    goods = [x for x in items if x['expected_bucket'] == 'good']
    bads = [x for x in items if x['expected_bucket'] == 'bad']
    false_pos = sum(1 for x in goods if x['verdict'] == 'FAIL')
    false_neg = sum(1 for x in bads if x['verdict'] == 'PASS')

    out = {
        'generated_at': dt.datetime.now(TZ).isoformat(timespec='seconds'),
        'policy_version': POLICY_VERSION,
        'total_samples': len(items),
        'good_samples': len(goods),
        'bad_samples': len(bads),
        'false_positive_fail_on_good': false_pos,
        'false_negative_pass_on_bad': false_neg,
        'latency_p95_ms': p95,
        'latency_avg_ms': round(sum(latencies) / len(latencies), 1) if latencies else 0.0,
        'items': items,
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / save_name).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    return out


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print('Usage: python qc_engine.py <video_path> [channel]')
        sys.exit(1)
    ch = sys.argv[2] if len(sys.argv) > 2 else ''
    r = qc_video(sys.argv[1], channel=ch)
    print(json.dumps(r, ensure_ascii=False, indent=2))
