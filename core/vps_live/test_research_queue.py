import json, secrets, tempfile, unittest, sqlite3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from research_queue import ResearchQueue, QueueError
from corner import Registry, connect


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.q = ResearchQueue(self.root)
        self.chief = {'id': 'chief-node', 'role': 'controller'}
        self.research = {'id': 'research-node', 'role': 'research'}
        self.verify = {'id': 'verify-node', 'role': 'verify'}

    def tearDown(self):
        self.temp.cleanup()

    def make(self, role='research', dedup='one', payload=None, auto_verify=False):
        return self.q.post(
            self.chief,
            '/tasks',
            {
                'assigned_to': role,
                'kind': 'research',
                'dedup': dedup,
                'auto_verify': auto_verify,
                'payload': payload or {'objective': 'Independent research'},
            },
        )['id']

    def test_empty_queue_does_not_import_legacy(self):
        old = sqlite3.connect(self.root / 'legacy_tasks.sqlite3')
        old.execute('CREATE TABLE tasks(payload TEXT)')
        old.execute('INSERT INTO tasks VALUES(?)', ('Facebook audit',))
        old.commit()
        old.close()
        self.assertEqual(self.q.post(self.research, '/claim', {})['id'], None)
        self.assertEqual(self.q.get(self.chief, '/tasks'), [])

    def test_rejects_fb_routes_and_other_projects(self):
        for url in [
            'http://100.67.236.124:8000/video-audit',
            'http://100.67.236.124:8101/tasks',
            'https://example.org/monetization-advisor',
        ]:
            with self.assertRaises(QueueError):
                self.make(payload={'source_url': url})
        with self.assertRaises(QueueError):
            self.q.post(self.chief, '/tasks', {'project': 'fb'})
        self.make(payload={'source_url': 'https://www.facebook.com/allowed-public-research-video'})

    def test_privileges_result_and_receipt(self):
        tid = self.make()
        r = self.q.post(self.research, '/claim', {'capabilities': ['research']})
        with self.assertRaises(QueueError):
            self.q.get(self.research, '/tasks')
        with self.assertRaises(QueueError):
            self.q.post(self.verify, '/tasks/' + tid + '/result', {'lease': r['lease'], 'result': {'outcome': 'ok'}})
        body = {'lease': r['lease'], 'result': {'outcome': 'ok', 'summary': 'Observed result'}}
        for _ in range(2):
            self.assertTrue(self.q.post(self.research, '/tasks/' + tid + '/result', body)['received'])
        # Verify role can read individual task directly via GET /tasks/{id}
        fetched = self.q.get(self.verify, '/tasks/' + tid)
        self.assertEqual(fetched['result']['summary'], 'Observed result')
        # Unrelated research node cannot read another worker's task
        other_research = {'id': 'other-research-node', 'role': 'research'}
        with self.assertRaises(QueueError):
            self.q.get(other_research, '/tasks/' + tid)
        self.assertEqual(self.q.post(self.chief, '/tasks/' + tid + '/approve', {})['status'], 'APPROVED')

    def test_batch_capability_matching_and_auto_verify(self):
        batch = self.q.post(self.chief, '/tasks/batch', {
            'project': 'research',
            'tasks': [
                {
                    'assigned_to': 'research',
                    'kind': 'video_fetch',
                    'dedup': 'b-1',
                    'auto_verify': True,
                    'payload': {'objective': 'Download video', 'required_capabilities': ['yt-dlp']},
                },
                {
                    'assigned_to': 'research',
                    'kind': 'web_scan',
                    'dedup': 'b-2',
                    'auto_verify': True,
                    'payload': {'objective': 'Browser scan', 'required_capabilities': ['browser']},
                },
            ],
        })
        self.assertEqual(batch['count'], 2)
        browser_worker = {'id': 'w-browser', 'role': 'research'}
        ytdlp_worker = {'id': 'w-ytdlp', 'role': 'research'}
        # Browser worker skips b-1 (needs yt-dlp) and claims b-2!
        c_browser = self.q.post(browser_worker, '/claim', {'capabilities': ['browser']})
        self.assertEqual(c_browser['dedup'], 'b-2')
        # yt-dlp worker claims b-1!
        c_ytdlp = self.q.post(ytdlp_worker, '/claim', {'capabilities': ['yt-dlp', 'ffmpeg']})
        self.assertEqual(c_ytdlp['dedup'], 'b-1')
        # Submitting b-2 with auto_verify=True automatically enqueues a verify task
        sub = self.q.post(
            browser_worker,
            '/tasks/' + c_browser['id'] + '/result',
            {'lease': c_browser['lease'], 'result': {'outcome': 'ok', 'summary': 'Scanned'}},
        )
        self.assertIn('verify_task_id', sub)
        v_claim = self.q.post(self.verify, '/claim', {'capabilities': ['verify']})
        self.assertEqual(v_claim['id'], sub['verify_task_id'])
        self.assertEqual(v_claim['payload']['target_task_id'], c_browser['id'])

    def test_parallel_10_workers_claim_distinct_tasks(self):
        tasks = [
            {'assigned_to': 'research', 'kind': 'scan', 'dedup': f'p-{i}', 'payload': {'objective': f'Item {i}'}}
            for i in range(10)
        ]
        self.q.post(self.chief, '/tasks/batch', {'project': 'research', 'tasks': tasks})
        workers = [{'id': f'worker-{i}', 'role': 'research'} for i in range(10)]
        with ThreadPoolExecutor(max_workers=10) as pool:
            claimed = list(pool.map(lambda w: self.q.post(w, '/claim', {'capabilities': ['research']})['id'], workers))
        self.assertEqual(len(set(claimed)), 10)
        self.assertNotIn(None, claimed)

    def test_engineer_is_explicit_and_revocable(self):
        tid = self.make('engineer')
        with self.assertRaises(QueueError):
            self.q.post(self.chief, '/claim', {}, True)
        r = self.q.post(self.chief, '/claim', {'as_role': 'engineer'}, True)
        self.assertEqual(r['id'], tid)
        with self.assertRaises(QueueError):
            self.q.post(self.chief, '/tasks/' + tid + '/heartbeat', {'as_role': 'engineer', 'lease': r['lease']}, False)
        self.assertEqual(
            self.q.post(self.chief, '/tasks/' + tid + '/heartbeat', {'as_role': 'engineer', 'lease': r['lease']}, True)['status'],
            'ok',
        )

    def test_concurrency_lease_and_node_ownership(self):
        tid = self.make()
        with ThreadPoolExecutor() as pool:
            rs = list(pool.map(lambda _: self.q.post(self.research, '/claim', {}), range(5)))
        self.assertEqual(len({r['lease'] for r in rs}), 1)
        old = rs[0]['lease']
        with self.q.db() as c:
            c.execute('UPDATE tasks SET lease_until=0 WHERE id=?', (tid,))
        new = self.q.post(self.research, '/claim', {})
        self.assertNotEqual(old, new['lease'])
        with self.assertRaises(QueueError):
            self.q.post(self.research, '/tasks/' + tid + '/result', {'lease': old, 'result': {'outcome': 'ok'}})

    def test_dedup_conflict_and_blocked_approval(self):
        tid = self.make()
        self.assertEqual(tid, self.make())
        with self.assertRaises(QueueError):
            self.make(payload={'objective': 'Different'})
        r = self.q.post(self.research, '/claim', {})
        self.q.post(self.research, '/tasks/' + tid + '/result', {'lease': r['lease'], 'result': {'outcome': 'BLOCKED'}})
        with self.assertRaises(QueueError):
            self.q.post(self.chief, '/tasks/' + tid + '/approve', {})

    def test_registry_never_reads_fb_credentials(self):
        reg = Registry(self.root, lambda ip: 'test-node')
        key = secrets.token_urlsafe(40)
        n = reg.enroll('100.64.0.1', 'research', key)
        reg.approve(n['id'])
        with connect(self.root) as c:
            c.execute(
                'INSERT INTO config VALUES(?,?)',
                ('controller', json.dumps({'url': 'http://100.64.0.1:8110', 'generation': 2, 'mode': 'research-only'})),
            )
        (self.root / 'credentials.json').write_text('THIS MUST NEVER BE PARSED')
        result = reg.resolve('100.64.0.1', key)
        self.assertEqual(result['application_token'], key)
        self.assertEqual(result['project'], 'research')
        with connect(self.root) as c:
            c.execute(
                'UPDATE config SET value=? WHERE key=?',
                (json.dumps({'url': 'http://100.64.0.1:8101', 'generation': 1, 'mode': 'legacy-adapter'}), 'controller'),
            )
        with self.assertRaises(PermissionError):
            reg.resolve('100.64.0.1', key)


if __name__ == '__main__':
    unittest.main(verbosity=2)
