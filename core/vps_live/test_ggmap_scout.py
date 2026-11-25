import base64
import http.cookiejar
import json
import secrets
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener

from corner import LOCK, Registry, capacity, connect
from ggmap_scout import classify_maps_match, parse_multipart
from hub_portal import HubManager, _csrf_for, make_hub_handler
from research_queue import ResearchQueue

# Valid 1x1 PNG containing CR/LF/NUL bytes in IDAT/IHDR header checks
SAMPLE_PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
)


def _encode_multipart(fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]) -> tuple[str, bytes]:
    boundary = '----TestBoundary' + secrets.token_hex(8)
    parts: list[bytes] = []
    for k, v in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode('utf-8')
        )
    for k, (fname, data, ctype) in files.items():
        header = (
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{fname}"\r\n'
            f'Content-Type: {ctype}\r\n\r\n'
        ).encode('utf-8')
        parts.append(header + data + b'\r\n')
    parts.append(f'--{boundary}--\r\n'.encode('utf-8'))
    return f'multipart/form-data; boundary={boundary}', b''.join(parts)


class GgmapScoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.reg = Registry(self.root, lambda ip: 'ts-' + ip)
        self.queue = ResearchQueue(self.root)
        self.hub = HubManager(self.reg, self.queue, connect, capacity, LOCK)
        self.admin_key = 'adm_' + secrets.token_urlsafe(24)
        self.hub.set_admin_key(self.admin_key)
        self.srv = ThreadingHTTPServer(('127.0.0.1', 0), make_hub_handler(self.hub))
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.srv.server_port}'

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.thread.join(timeout=5)
        self.tmp.cleanup()

    def _api(self, method: str, path: str, body: bytes | None = None, headers: dict | None = None):
        hdrs = dict(headers or {})
        req = Request(self.base + path, data=body, headers=hdrs, method=method)
        try:
            with build_opener().open(req) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except HTTPError as e:
            return e.code, dict(e.headers), e.read()

    def test_classify_maps_match_variants(self):
        self.assertEqual(
            classify_maps_match('ĐƯỜNG NGUYỄN VĂN CỪ', 'ĐƯỜNG', 'Đường Nguyễn Văn Cừ', 'ĐƯỜNG'),
            'KHỚP',
        )
        self.assertEqual(
            classify_maps_match('ĐƯỜNG NGUYỄN VĂN CỪ', 'ĐƯỜNG', 'Phố Nguyễn Văn Cừ', 'PHỐ'),
            'KHÁC TIỀN TỐ (ĐƯỜNG/PHỐ)',
        )
        self.assertEqual(
            classify_maps_match('PHỐ BỒ ĐỀ', 'PHỐ', 'Phố Bồ Đề, Bồ Đề, Long Biên, Hà Nội', 'PHỐ'),
            'KHỚP',
        )
        self.assertEqual(
            classify_maps_match('ĐƯỜNG NGUYỄN VĂN CỪ', 'ĐƯỜNG', 'Nguyen Van Cu St', 'ĐƯỜNG'),
            'KHỚP',
        )
        self.assertEqual(
            classify_maps_match('ĐÊ LONG BIÊN-XUÂN QUAN', 'ĐÊ', 'Đê Long Biên - Xuân Quan', 'ĐÊ'),
            'KHỚP',
        )
        self.assertEqual(
            classify_maps_match('PHỐ BỒ ĐỀ', 'PHỐ', 'Phố Lâm Du', 'PHỐ'),
            'KHÁC TÊN',
        )
        self.assertEqual(
            classify_maps_match('PHỐ BỒ ĐỀ', 'PHỐ', '', 'KHÔNG TÌM THẤY'),
            'KHÔNG TÌM THẤY',
        )

    def test_parse_multipart_utf8_and_binary_png(self):
        binary_with_crlf = SAMPLE_PNG + b'\r\n\x00\xffPNG_END'
        ctype, payload = _encode_multipart(
            {'maps_found_name': 'Đường Nguyễn Văn Cừ', 'maps_prefix': 'ĐƯỜNG'},
            {'screenshot': ('shot.png', binary_with_crlf, 'image/png')},
        )
        fields, files = parse_multipart(ctype, payload)
        self.assertEqual(fields['maps_found_name'], 'Đường Nguyễn Văn Cừ')
        self.assertEqual(files['screenshot'][1], binary_with_crlf)

    def test_seed_104_priority_concurrency_isolation_and_export(self):
        canonical_path = Path(r'd:\AI_AGENT\longbien_pdf_104_canonical.json')
        if not canonical_path.is_file():
            self.skipTest('Thiếu dữ liệu mẫu longbien_pdf_104_canonical.json trên máy này')
        canonical = json.loads(canonical_path.read_text(encoding='utf-8'))
        items = canonical['items']
        self.assertEqual(len(items), 104)

        status, _, raw = self._api(
            'POST',
            '/api/ggmap/seed',
            json.dumps({'items': items, 'reset': True}).encode(),
            {'Authorization': f'Bearer {self.admin_key}', 'Content-Type': 'application/json'},
        )
        self.assertEqual(status, 200)
        seeded = json.loads(raw)
        self.assertEqual(seeded['total'], 104)

        # Video Studio queue stays untouched
        self.assertEqual(self.queue.get({'id': 'hub-owner', 'role': 'controller'}, '/tasks?limit=10'), [])

        inv = self.hub.create_invite(ttl_minutes=60, max_uses=10, targets={'research': 10, 'verify': 0, 'engineer': 0})
        workers = [self.hub.join_with_invite(inv['code'], f'203.0.113.{i + 1}') for i in range(7)]

        claimed_codes: list[str] = []
        claim_lock = threading.Lock()

        def grab(w):
            st, _, b = self._api(
                'POST',
                '/api/ggmap/claim',
                b'{}',
                {'Authorization': f"Bearer {w['token']}", 'Content-Type': 'application/json'},
            )
            self.assertEqual(st, 200)
            it = json.loads(b)['item']
            with claim_lock:
                claimed_codes.append(it['code'])

        threads = [threading.Thread(target=grab, args=(w,)) for w in workers]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 7 Muses claimed 7 distinct streets, prioritizing highest dot1_count (LB_001 has 16)
        self.assertEqual(len(set(claimed_codes)), 7)
        self.assertIn('LB_001', claimed_codes)

        # Idempotent re-claim by worker[0] returns same active street
        st, _, b1 = self._api(
            'POST',
            '/api/ggmap/claim',
            b'{}',
            {'Authorization': f"Bearer {workers[0]['token']}", 'Content-Type': 'application/json'},
        )
        self.assertEqual(st, 200)
        w0_item = json.loads(b1)['item']

        st, _, b2 = self._api(
            'POST',
            '/api/ggmap/claim',
            b'{}',
            {'Authorization': f"Bearer {workers[0]['token']}", 'Content-Type': 'application/json'},
        )
        self.assertEqual(st, 200)
        self.assertEqual(json.loads(b2)['item']['code'], w0_item['code'])

        # Submit mismatch prefix with base64 PNG via JSON API
        b64_data = 'data:image/png;base64,' + base64.b64encode(SAMPLE_PNG).decode()
        st, _, sub_raw = self._api(
            'POST',
            '/api/ggmap/submit',
            json.dumps(
                {
                    'code': w0_item['code'],
                    'lease': w0_item['lease'],
                    'maps_found_name': 'Phố ' + w0_item['pdf_name'].split(' ', 1)[1].title(),
                    'maps_prefix': 'PHỐ' if w0_item['pdf_prefix'] == 'ĐƯỜNG' else 'ĐƯỜNG',
                    'maps_url': 'https://www.google.com/maps/place/Test',
                    'screenshot_base64': b64_data,
                }
            ).encode(),
            {'Authorization': f"Bearer {workers[0]['token']}", 'Content-Type': 'application/json'},
        )
        self.assertEqual(st, 200)
        done_item = json.loads(sub_raw)['item']
        self.assertEqual(done_item['status'], 'DONE')
        self.assertEqual(done_item['screenshot_file'], f"{w0_item['code']}.png")

        # Unauthenticated shot access blocked
        st, _, _ = self._api('GET', f"/ggmap/shots/{done_item['screenshot_file']}")
        self.assertEqual(st, 403)

        # Path traversal blocked at both HTTP & storage layers
        self.assertIsNone(self.hub.ggmap.get_shot_path('../corner.py'))
        st, _, _ = self._api(
            'GET',
            '/ggmap/shots/..%2f..%2fcorner.py',
            headers={'Authorization': f"Bearer {self.admin_key}"},
        )
        self.assertIn(st, (403, 404))

        # Authenticated shot returns exact PNG bytes
        st, hdrs, png_out = self._api(
            'GET',
            f"/ggmap/shots/{done_item['screenshot_file']}",
            headers={'Authorization': f"Bearer {self.admin_key}"},
        )
        self.assertEqual(st, 200)
        self.assertEqual(hdrs.get('Content-Type'), 'image/png')
        self.assertEqual(hdrs.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(png_out, SAMPLE_PNG)

        # CSV export succeeds for admin
        st, hdrs, csv_bytes = self._api(
            'GET',
            '/ggmap/export.csv',
            headers={'Authorization': f"Bearer {self.admin_key}"},
        )
        self.assertEqual(st, 200)
        csv_text = csv_bytes.decode('utf-8-sig')
        self.assertIn(w0_item['code'], csv_text)
        self.assertIn(f"/ggmap/shots/{done_item['screenshot_file']}", csv_text)

    def test_browser_flow_multipart_security_and_reclaim(self):
        self.hub.ggmap.seed_items(
            [
                {
                    'code': 'LB_TEST1',
                    'pdf_name': 'ĐƯỜNG NGUYỄN VĂN CỪ',
                    'pdf_prefix': 'ĐƯỜNG',
                    'dot1_count': 10,
                    'total_count': 12,
                    'ggmap_search_url': 'https://www.google.com/maps/search/?api=1&query=Nguyen+Van+Cu',
                }
            ]
        )
        inv = self.hub.create_invite(ttl_minutes=30, max_uses=3, targets={'research': 3, 'verify': 0, 'engineer': 0})

        jar = http.cookiejar.CookieJar()
        op = build_opener(HTTPCookieProcessor(jar))

        # 1. Join directly via /ggmap/j/<code>
        html_worker = op.open(self.base + f"/ggmap/j/{inv['code']}").read().decode('utf-8')
        self.assertIn('Nhận 1 Tuyến Đường Tiếp Theo', html_worker)
        worker_tok = next(c.value for c in jar if c.name == 'agentnet_worker')
        csrf = _csrf_for(worker_tok)

        # 2. Claim via browser POST
        claimed_html = op.open(
            Request(self.base + '/ggmap/claim', data=urlencode({'csrf': csrf}).encode())
        ).read().decode('utf-8')
        self.assertIn('LB_TEST1', claimed_html)
        self.assertIn('ĐƯỜNG NGUYỄN VĂN CỪ', claimed_html)

        active = self.hub.ggmap.claim(
            self.hub.ggmap.list_items()[0]['owner_node'],
            lease_seconds=900,
        )

        # 3. Reject invalid fake image magic bytes via API
        st, _, err_body = self._api(
            'POST',
            '/api/ggmap/submit',
            json.dumps(
                {
                    'code': 'LB_TEST1',
                    'lease': active['lease'],
                    'maps_found_name': 'Đường Nguyễn Văn Cừ',
                    'maps_prefix': 'ĐƯỜNG',
                    'screenshot_base64': base64.b64encode(b'MZNOTAPNGFILE').decode(),
                }
            ).encode(),
            {'Authorization': f'Bearer {worker_tok}', 'Content-Type': 'application/json'},
        )
        self.assertEqual(st, 400)
        self.assertIn('Định dạng ảnh', err_body.decode('utf-8'))

        # 4. Reject oversized (>2MB) PNG upload
        huge = SAMPLE_PNG + (b'\x00' * (2 * 1024 * 1024 + 100))
        ctype_big, body_big = _encode_multipart(
            {
                'csrf': csrf,
                'code': 'LB_TEST1',
                'lease': active['lease'],
                'maps_found_name': 'Đường Nguyễn Văn Cừ',
                'maps_prefix': 'ĐƯỜNG',
            },
            {'screenshot': ('huge.png', huge, 'image/png')},
        )
        st, _, err_big = self._api(
            'POST',
            '/api/ggmap/submit',
            body_big,
            {'Authorization': f'Bearer {worker_tok}', 'Content-Type': ctype_big},
        )
        self.assertEqual(st, 400)

        # 5. Valid browser multipart submit succeeds
        ctype_ok, body_ok = _encode_multipart(
            {
                'csrf': csrf,
                'code': 'LB_TEST1',
                'lease': active['lease'],
                'maps_found_name': 'Đường Nguyễn Văn Cừ',
                'maps_prefix': 'ĐƯỜNG',
                'maps_url': 'https://www.google.com/maps/place/Nguyen+Van+Cu',
            },
            {'screenshot': ('map.png', SAMPLE_PNG, 'image/png')},
        )
        after_sub = op.open(
            Request(self.base + '/ggmap/submit', data=body_ok, headers={'Content-Type': ctype_ok})
        ).read().decode('utf-8')
        self.assertIn('KHỚP', after_sub)

        # 6. Admin requeue resets item cleanly and lease expiry works
        st, _, _ = self._api(
            'POST',
            '/api/ggmap/requeue',
            json.dumps({'code': 'LB_TEST1'}).encode(),
            {'Authorization': f'Bearer {self.admin_key}', 'Content-Type': 'application/json'},
        )
        self.assertEqual(st, 200)
        reclaimed = self.hub.ggmap.claim('other-node', lease_seconds=60)
        self.assertEqual(reclaimed['code'], 'LB_TEST1')

        # Backdate lease_until to simulate worker disappearing
        with self.hub.ggmap._db() as conn:
            conn.execute('UPDATE ggmap_items SET lease_until = 1.0 WHERE code = ?', ('LB_TEST1',))
        taken_over = self.hub.ggmap.claim('rescue-node', lease_seconds=60)
        self.assertEqual(taken_over['code'], 'LB_TEST1')
        self.assertEqual(taken_over['owner_node'], 'rescue-node')


if __name__ == '__main__':
    unittest.main()
