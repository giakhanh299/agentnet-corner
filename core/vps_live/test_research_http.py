import json, secrets, tempfile, threading, unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from corner import Registry, Handler, connect
from research_queue import ResearchQueue


class HttpTests(unittest.TestCase):
    def test_research_only_transport_fleet_and_revocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'join.py').write_text('# join bootstrap\n')
            reg = Registry(root, lambda ip: 'mock-device-' + ip)
            fleet_secret = 'fleet_' + secrets.token_urlsafe(24)
            reg.set_fleet_key(fleet_secret, max_nodes=50, enabled=True)
            tokens = {r: secrets.token_urlsafe(40) for r in ['controller', 'research', 'verify']}
            ids = {}
            for role, token in tokens.items():
                n = reg.enroll('127.0.0.1', role, token)
                reg.approve(n['id'])
                ids[role] = n['id']
            with connect(root) as c:
                c.execute(
                    'INSERT INTO config VALUES(?,?)',
                    ('controller', json.dumps({'url': 'http://100.64.0.1:8110', 'generation': 2, 'mode': 'research-only'})),
                )
            h = type('TestHandler', (Handler,), {'registry': reg, 'queue': ResearchQueue(root)})
            server = ThreadingHTTPServer(('127.0.0.1', 0), h)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()

            def call(path, role=None, body=None, token=None):
                headers = {'Content-Type': 'application/json'}
                if role or token:
                    headers['Authorization'] = 'Bearer ' + (token or tokens[role])
                req = Request(
                    f'http://127.0.0.1:{server.server_port}' + path,
                    headers=headers,
                    data=json.dumps(body).encode() if body is not None else None,
                )
                try:
                    with urlopen(req, timeout=5) as r:
                        raw = r.read()
                        ctype = r.headers.get('Content-Type', '')
                        return r.status, (json.loads(raw) if 'json' in ctype else raw.decode())
                except HTTPError as e:
                    return e.code, json.load(e)

            try:
                self.assertEqual(call('/health')[1]['project'], 'research')
                self.assertTrue(call('/health')[1]['fleet_auto_enroll'])
                self.assertIn('join bootstrap', call('/join.py')[1])
                # Auto-enroll a 2nd research worker over HTTP using fleet_key
                extra_tok = secrets.token_urlsafe(40)
                st, enr = call('/enroll', body={'role': 'research', 'token': extra_tok, 'fleet_key': fleet_secret})
                self.assertEqual(st, 200)
                self.assertEqual(enr['status'], 'APPROVED')

                self.assertEqual(call('/tasks', 'controller')[1], [])
                self.assertEqual(call('/tasks', token='old-facebook-credential')[0], 403)
                self.assertEqual(call('/tasks', 'research')[0], 403)
                body = {
                    'project': 'research',
                    'assigned_to': 'research',
                    'kind': 'test',
                    'dedup': 'http-test',
                    'auto_verify': True,
                    'payload': {'objective': 'Transport smoke'},
                }
                status, task = call('/tasks', 'controller', body)
                self.assertEqual(status, 200)
                status, claim = call('/claim', token=extra_tok, body={'capabilities': ['test']})
                self.assertEqual(status, 200)
                self.assertEqual(claim['id'], task['id'])
                result = {'lease': claim['lease'], 'result': {'outcome': 'ok', 'summary': 'Transport test'}}
                st_res, sub_res = call('/tasks/' + task['id'] + '/result', token=extra_tok, body=result)
                self.assertEqual(st_res, 200)
                self.assertIn('verify_task_id', sub_res)
                # Verify worker reads GET /tasks/{id} directly
                st_get, fetched = call('/tasks/' + task['id'], 'verify')
                self.assertEqual(st_get, 200)
                self.assertEqual(fetched['result']['summary'], 'Transport test')
                self.assertEqual(call('/tasks/' + task['id'] + '/approve', 'controller', {})[0], 200)
                self.assertEqual(call('/fleet', 'controller')[0], 200)
                body['dedup'] = 'fb-rejected'
                body['payload'] = {'source_url': 'http://100.67.236.124:8000/video-audit'}
                self.assertEqual(call('/tasks', 'controller', body)[0], 400)
                with connect(root) as c:
                    c.execute("UPDATE nodes SET status='REVOKED' WHERE id=?", (ids['controller'],))
                self.assertEqual(call('/tasks', 'controller')[0], 403)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
