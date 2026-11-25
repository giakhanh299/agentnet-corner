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
from hub_portal import HubManager, _csrf_for, make_hub_handler
from research_queue import ResearchQueue


class HubPortalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.reg = Registry(self.root, lambda ip: 'ts-' + ip)
        self.queue = ResearchQueue(self.root)
        self.hub = HubManager(self.reg, self.queue, connect, capacity, LOCK)
        self.admin_key = 'adm_' + secrets.token_urlsafe(28)
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

    def test_auto_role_balance_and_quota(self):
        inv = self.hub.create_invite(
            ttl_minutes=30,
            max_uses=9,
            targets={'research': 5, 'verify': 2, 'engineer': 2},
        )
        roles = []
        for i in range(9):
            joined = self.hub.join_with_invite(inv['code'], f'203.0.113.{i+1}')
            roles.append(joined['role'])
        self.assertEqual(roles.count('research'), 5)
        self.assertEqual(roles.count('verify'), 2)
        self.assertEqual(roles.count('engineer'), 2)
        # 10th join exceeds max_uses=9
        with self.assertRaises(PermissionError):
            self.hub.join_with_invite(inv['code'], '203.0.113.99')

    def test_browser_worker_and_admin_full_flow(self):
        # 1. Admin logs in, creates batch tasks
        adm_jar = http.cookiejar.CookieJar()
        adm_op = build_opener(HTTPCookieProcessor(adm_jar))
        adm_csrf = _csrf_for(self.admin_key)

        r = adm_op.open(
            Request(
                self.base + '/admin/login',
                data=urlencode({'admin_key': self.admin_key}).encode(),
            )
        )
        html_dash = r.read().decode()
        self.assertIn('Bảng Chỉ Huy Đội Quân Muse', html_dash)

        # Admin dispatches 2 research tasks with auto_verify=1
        adm_op.open(
            Request(
                self.base + '/admin/task/batch',
                data=urlencode({
                    'csrf': adm_csrf,
                    'assigned_to': 'research',
                    'kind': 'hook_study',
                    'objectives': 'Analyze Hook A\nAnalyze Hook B',
                    'auto_verify': '1',
                }).encode(),
            )
        )

        # 2. Browser Muse joins via 1-click link /j/<CODE>
        inv = self.hub.create_invite(ttl_minutes=15, max_uses=5, targets={'research': 2, 'verify': 1, 'engineer': 0})
        w_jar = http.cookiejar.CookieJar()
        w_op = build_opener(HTTPCookieProcessor(w_jar))
        portal_html = w_op.open(self.base + '/j/' + inv['code']).read().decode()
        self.assertIn('Sẵn sàng nhận nhiệm vụ', portal_html)

        w_tok = [c.value for c in w_jar if c.name == 'agentnet_worker'][0]
        w_csrf = _csrf_for(w_tok)

        # Worker clicks Claim Task
        claimed_page = w_op.open(
            Request(
                self.base + '/portal/claim',
                data=urlencode({'csrf': w_csrf, 'capabilities': 'research,browser'}).encode(),
            )
        ).read().decode()
        self.assertIn('Nhiệm vụ đang nhận', claimed_page)
        self.assertIn('Analyze Hook A', claimed_page)

        # Extract task_id and lease from DB to submit via HTML form
        tasks = self.queue.get({'id': 'chief', 'role': 'controller'}, '/tasks')
        running = [t for t in tasks if t['status'] == 'RUNNING'][0]

        # Submitting with wrong CSRF is rejected (403)
        with self.assertRaises(HTTPError) as ctx:
            w_op.open(
                Request(
                    self.base + '/portal/submit',
                    data=urlencode({'csrf': 'bad', 'task_id': running['id'], 'lease': running['lease'], 'summary': 'x'}).encode(),
                )
            )
        self.assertEqual(ctx.exception.code, 403)

        # Valid submit completes Hook A, spawns auto-verify, and auto-claims Hook B!
        next_page = w_op.open(
            Request(
                self.base + '/portal/submit',
                data=urlencode({
                    'csrf': w_csrf,
                    'task_id': running['id'],
                    'lease': running['lease'],
                    'outcome': 'ok',
                    'summary': 'Hook A uses visual contrast at 0.4s',
                    'sources': 'https://example.com/v1',
                    'lessons': 'Strong contrast in frame 1',
                    'limitations': 'No audio stem split',
                    'next': '1',
                }).encode(),
            )
        ).read().decode()
        self.assertIn('Analyze Hook B', next_page)

        # Admin approves completed Hook A from dashboard
        adm_op.open(
            Request(
                self.base + '/admin/task/approve',
                data=urlencode({'csrf': adm_csrf, 'task_id': running['id']}).encode(),
            )
        )
        updated = self.queue.get({'id': 'chief', 'role': 'controller'}, '/tasks/' + running['id'])
        self.assertEqual(updated['status'], 'APPROVED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
