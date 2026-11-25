import json, secrets, tempfile, unittest
from pathlib import Path
from corner import Registry, capacity, connect


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.reg = Registry(self.root, lambda ip: 'device-' + ip)
        with connect(self.root) as db:
            db.execute(
                'INSERT INTO config VALUES(?,?)',
                ('controller', json.dumps({'url': 'http://100.64.0.1:8110', 'generation': 1, 'mode': 'research-only'})),
            )

    def tearDown(self):
        self.tmp.cleanup()

    def test_pending_not_self_promoted(self):
        key = secrets.token_urlsafe(40)
        row = self.reg.enroll('100.64.0.2', 'controller', key)
        self.assertEqual(row['status'], 'REPLACEMENT_PENDING')
        with self.assertRaises(PermissionError):
            self.reg.resolve('100.64.0.2', key)
        self.reg.approve(row['id'])
        self.assertEqual(self.reg.resolve('100.64.0.2', key)['role'], 'controller')
        self.assertEqual(self.reg.resolve('100.64.0.2', key)['application_token'], key)

    def test_machine_identity_and_role_credentials(self):
        for index, role in enumerate(['research', 'verify', 'engineer']):
            ip = '100.64.0.' + str(index + 2)
            key = secrets.token_urlsafe(40)
            row = self.reg.enroll(ip, role, key)
            self.reg.approve(row['id'])
            result = self.reg.resolve(ip, key)
            self.assertEqual(result['role'], role)
            self.assertNotIn('credentials', result)
            with self.assertRaises(PermissionError):
                self.reg.resolve('100.64.0.99', key)

    def test_controller_singleton_requires_explicit_revoke(self):
        a = self.reg.enroll('100.64.0.2', 'controller', secrets.token_urlsafe(40))
        self.reg.approve(a['id'])
        b = self.reg.enroll('100.64.0.3', 'controller', secrets.token_urlsafe(40))
        with self.assertRaises(ValueError):
            self.reg.approve(b['id'])

    def test_multi_worker_pool_and_fleet_key_auto_enroll(self):
        fleet_secret = 'fleet_' + secrets.token_urlsafe(24)
        self.reg.set_fleet_key(fleet_secret, max_nodes=12, enabled=True)
        # Controller NEVER self-promotes even with a valid fleet_key
        c_row = self.reg.enroll('100.64.0.2', 'controller', secrets.token_urlsafe(40), fleet_key=fleet_secret)
        self.assertEqual(c_row['status'], 'REPLACEMENT_PENDING')
        self.reg.approve(c_row['id'])
        # Plug in 10 workers across research/verify/engineer seamlessly
        roles = ['research'] * 6 + ['verify'] * 2 + ['engineer'] * 2
        for idx, role in enumerate(roles, start=10):
            ip = f'100.64.0.{idx}'
            tok = secrets.token_urlsafe(40)
            r = self.reg.enroll(ip, role, tok, fleet_key=fleet_secret)
            self.assertEqual(r['status'], 'APPROVED')
            resolved = self.reg.resolve(ip, tok)
            self.assertEqual(resolved['role'], role)
        # Wrong fleet key falls back to REPLACEMENT_PENDING
        bad = self.reg.enroll('100.64.0.99', 'research', secrets.token_urlsafe(40), fleet_key='wrong_key_1234567890')
        self.assertEqual(bad['status'], 'REPLACEMENT_PENDING')

    def test_idempotency_and_route_refresh(self):
        key = secrets.token_urlsafe(40)
        a = self.reg.enroll('100.64.0.2', 'verify', key)
        self.assertEqual(a, self.reg.enroll('100.64.0.2', 'verify', key))
        self.reg.approve(a['id'])
        with connect(self.root) as db:
            db.execute(
                "UPDATE config SET value=? WHERE key='controller'",
                (json.dumps({'url': 'http://100.64.0.9:8110', 'generation': 2, 'mode': 'research-only'}),),
            )
        self.assertEqual(self.reg.resolve('100.64.0.2', key)['controller_generation'], 2)

    def test_storage_limit(self):
        self.assertLess(capacity(self.root), 1000000)

    def test_stale_registry_is_not_network_offline(self):
        key = secrets.token_urlsafe(40)
        node = self.reg.enroll('100.64.0.2', 'research', key)
        self.reg.approve(node['id'])
        status = [n for n in self.reg.status() if n['id'] == node['id']][0]
        self.assertEqual(status['availability'], 'REGISTRY_STALE')
        self.assertIsNone(status['registry_heartbeat_age_seconds'])

    def test_chief_delegation_coexists_with_engineer_pool(self):
        chief = secrets.token_urlsafe(40)
        worker = secrets.token_urlsafe(40)
        eng = secrets.token_urlsafe(40)
        a = self.reg.enroll('100.64.0.2', 'controller', chief)
        self.reg.approve(a['id'])
        b = self.reg.enroll('100.64.0.3', 'research', worker)
        self.reg.approve(b['id'])
        self.reg.delegate_engineering(True)
        self.assertNotIn('additional_roles', self.reg.resolve('100.64.0.2', chief))
        extra = self.reg.resolve('100.64.0.2', chief, include_delegation=True)['additional_roles']['engineer']
        self.assertEqual(extra['application_token'], chief)
        self.assertNotIn('additional_roles', self.reg.resolve('100.64.0.3', worker, include_delegation=True))
        # Dedicated engineer pool worker can ALSO be approved alongside Chief delegation
        e_node = self.reg.enroll('100.64.0.4', 'engineer', eng)
        self.reg.approve(e_node['id'])
        self.assertEqual(self.reg.resolve('100.64.0.4', eng)['role'], 'engineer')
        self.reg.delegate_engineering(False)
        self.assertNotIn('additional_roles', self.reg.resolve('100.64.0.2', chief, include_delegation=True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
