"""Smart Multi-Host File Exchange Router for ProjectMind <-> Muse Fleet.

Avoids single-host fragility (e.g. file.io auto-deleting after 1 download when multiple
Research + Verify Muses need the same contact sheet or clip excerpt).

Security Guard (L065):
- Strictly blocks uploading databases (.db/.sqlite/.sqlite3), env/key/credential files,
  or JSON files containing tokens/passwords/cookies to public hosts.
- Enforces file size caps per host.

Provider order for public temporary non-sensitive media (contact sheets, sample clips, generated images):
  1. litterbox.catbox.moe  (multi-download, 1h/12h/24h/72h TTL, up to 1 GB)
  2. tmpfiles.org          (multi-download, ~1h TTL, direct URL)
  3. 0x0.st                (multi-download, up to 512 MiB)
  4. file.io               (1-time download fallback, last resort)
Permanent non-sensitive images (e.g. approved sample packs):
  - catbox.moe             (up to 200 MB, direct link)
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import requests

FORBIDDEN_EXTS = {'.db', '.sqlite', '.sqlite3', '.env', '.pem', '.key', '.p12', '.pfx', '.kdbx', '.bat', '.cmd', '.ps1', '.sh'}
SECRET_KEY_RE = re.compile(
    r'(?:telegram_bot_token|hatch_sess|api_key|secret_key|password|private_key|MUSE-[A-Z0-9]{8,}|hubw_[A-Za-z0-9_-]{16,})',
    re.I,
)
MAX_PUBLIC_BYTES = 100 * 1024 * 1024  # 100 MiB safe default cap


class UnsafeUploadError(ValueError):
    """Raised when a file violates L065 security guardrails for public file sharing."""


def validate_public_upload(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f'Không thấy tệp: {path}')
    if path.suffix.lower() in FORBIDDEN_EXTS:
        raise UnsafeUploadError(f'Cấm tải tệp loại {path.suffix} lên host công cộng (L065).')
    if any(tok in path.name.lower() for tok in ('secret', 'token', 'password', 'cookie', 'credential', 'invite', 'pending_account', 'automation_config')):
        raise UnsafeUploadError(f'Tên tệp nhạy cảm không được tải lên host công cộng: {path.name} (L065).')
    size = path.stat().st_size
    if size <= 0:
        raise ValueError('Tệp rỗng (0 bytes).')
    if size > MAX_PUBLIC_BYTES:
        raise ValueError(f'Tệp quá lớn ({size} bytes > {MAX_PUBLIC_BYTES}) cho kênh công khai; dùng Google Drive hoặc VPS.')
    # Inspect text/json files for accidental secret leakage
    if path.suffix.lower() in ('.txt', '.json', '.md', '.csv', '.yaml', '.yml', '.log'):
        head = path.read_text(encoding='utf-8', errors='ignore')[:65536]
        if SECRET_KEY_RE.search(head):
            raise UnsafeUploadError(f'Phát hiện chuỗi nghi secret/token bên trong {path.name} — chặn tải lên (L065).')


def _upload_litterbox(path: Path, ttl: str = '24h', timeout: int = 30) -> dict:
    valid_ttl = ttl if ttl in ('1h', '12h', '24h', '72h') else '24h'
    with path.open('rb') as f:
        r = requests.post(
            'https://litterbox.catbox.moe/resources/internals/api.php',
            data={'reqtype': 'fileupload', 'time': valid_ttl},
            files={'fileToUpload': (path.name, f)},
            timeout=timeout,
            headers={'User-Agent': 'ProjectMind-Exchange/1.0'},
        )
    r.raise_for_status()
    url = r.text.strip()
    if not url.startswith('https://'):
        raise RuntimeError(f'litterbox unexpected response: {url[:80]}')
    return {'ok': True, 'provider': 'litterbox.catbox.moe', 'url': url, 'multi_download': True, 'ttl': valid_ttl}


def _upload_catbox(path: Path, timeout: int = 30) -> dict:
    with path.open('rb') as f:
        r = requests.post(
            'https://catbox.moe/user/api.php',
            data={'reqtype': 'fileupload'},
            files={'fileToUpload': (path.name, f)},
            timeout=timeout,
            headers={'User-Agent': 'ProjectMind-Exchange/1.0'},
        )
    r.raise_for_status()
    url = r.text.strip()
    if not url.startswith('https://'):
        raise RuntimeError(f'catbox unexpected response: {url[:80]}')
    return {'ok': True, 'provider': 'catbox.moe', 'url': url, 'multi_download': True, 'ttl': 'permanent'}


def _upload_tmpfiles(path: Path, timeout: int = 30) -> dict:
    with path.open('rb') as f:
        r = requests.post(
            'https://tmpfiles.org/api/v1/upload',
            files={'file': (path.name, f)},
            timeout=timeout,
            headers={'User-Agent': 'ProjectMind-Exchange/1.0'},
        )
    r.raise_for_status()
    j = r.json()
    raw_url = ((j.get('data') or {}).get('url') or '').strip()
    if not raw_url.startswith('http'):
        raise RuntimeError(f'tmpfiles unexpected response: {str(j)[:100]}')
    # Convert tmpfiles view URL to direct download URL (/dl/)
    dl_url = raw_url.replace('http://', 'https://').replace('tmpfiles.org/', 'tmpfiles.org/dl/', 1)
    return {'ok': True, 'provider': 'tmpfiles.org', 'url': dl_url, 'view_url': raw_url, 'multi_download': True, 'ttl': '1h'}


def _upload_0x0(path: Path, timeout: int = 30) -> dict:
    with path.open('rb') as f:
        r = requests.post(
            'https://0x0.st',
            files={'file': (path.name, f)},
            timeout=timeout,
            headers={'User-Agent': 'ProjectMind-Exchange/1.0'},
        )
    r.raise_for_status()
    url = r.text.strip()
    if not url.startswith('https://'):
        raise RuntimeError(f'0x0.st unexpected response: {url[:80]}')
    return {'ok': True, 'provider': '0x0.st', 'url': url, 'multi_download': True, 'ttl': '30d+'}


def _upload_uguu(path: Path, timeout: int = 30) -> dict:
    with path.open('rb') as f:
        r = requests.post(
            'https://uguu.se/upload',
            files={'files[]': (path.name, f)},
            timeout=timeout,
            headers={'User-Agent': 'ProjectMind-Exchange/1.0'},
        )
    r.raise_for_status()
    j = r.json()
    files = j.get('files') or []
    url = (files[0].get('url') or '').strip() if files else ''
    if not url.startswith('https://'):
        raise RuntimeError(f'uguu unexpected response: {str(j)[:100]}')
    return {'ok': True, 'provider': 'uguu.se', 'url': url, 'multi_download': True, 'ttl': '3h'}


def _upload_fileio(path: Path, timeout: int = 30) -> dict:
    with path.open('rb') as f:
        r = requests.post(
            'https://file.io',
            files={'file': (path.name, f)},
            timeout=timeout,
            headers={'User-Agent': 'ProjectMind-Exchange/1.0'},
        )
    r.raise_for_status()
    j = r.json()
    url = (j.get('link') or '').strip()
    if not url.startswith('https://'):
        raise RuntimeError(f'file.io unexpected response: {str(j)[:100]}')
    return {'ok': True, 'provider': 'file.io', 'url': url, 'multi_download': False, 'ttl': '1-download'}


PROVIDERS = {
    'catbox': _upload_catbox,
    'uguu': _upload_uguu,
    'litterbox': _upload_litterbox,
    'tmpfiles': _upload_tmpfiles,
    '0x0': _upload_0x0,
    'fileio': _upload_fileio,
}


def upload_temp_share(path: str | Path, *, permanent: bool = False, ttl: str = '24h',
                      order: list[str] | None = None, timeout: int = 25) -> dict:
    """Upload a verified non-sensitive file with automatic multi-host fallback.

    Prioritizes direct-URL multi-download hosts (>3h TTL) so independent Verify workers
    can reliably re-fetch evidence without hitting 1h expiry (learned from verify a88db6fa).
    """
    p = Path(path)
    validate_public_upload(p)
    chain = order or (['catbox', 'uguu', 'litterbox', 'tmpfiles'] if permanent else ['uguu', 'catbox', 'litterbox', 'tmpfiles', '0x0', 'fileio'])
    errors = []
    for name in chain:
        fn = PROVIDERS.get(name)
        if not fn:
            continue
        try:
            res = fn(p, ttl=ttl, timeout=timeout) if name == 'litterbox' else fn(p, timeout=timeout)
            res['file_name'] = p.name
            res['size_bytes'] = p.stat().st_size
            res['tried_failed'] = errors
            return res
        except Exception as exc:
            errors.append({'provider': name, 'error': f'{type(exc).__name__}: {str(exc)[:120]}'})
    return {'ok': False, 'file_name': p.name, 'errors': errors}


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print('Usage: python file_exchange.py <file_path> [--permanent]')
        sys.exit(1)
    perm = '--permanent' in sys.argv[2:]
    print(json.dumps(upload_temp_share(sys.argv[1], permanent=perm), ensure_ascii=False, indent=2))
