import json,secrets,tempfile,unittest
from pathlib import Path
from corner import Registry,capacity,connect

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.reg=Registry(self.root,lambda ip:'device-'+ip)
        with connect(self.root) as db:db.execute('INSERT INTO config VALUES(?,?)',('controller',json.dumps({'url':'http://100.64.0.1:8110','generation':1,'mode':'research-only'})))
    def tearDown(self):self.tmp.cleanup()
    def test_pending_not_self_promoted(self):
        key=secrets.token_urlsafe(40)
        row=self.reg.enroll('100.64.0.2','controller',key)
        self.assertEqual(row['status'],'REPLACEMENT_PENDING')
        with self.assertRaises(PermissionError):self.reg.resolve('100.64.0.2',key)
        self.reg.approve(row['id'])
        self.assertEqual(self.reg.resolve('100.64.0.2',key)['role'],'controller')
        self.assertEqual(self.reg.resolve('100.64.0.2',key)['application_token'],key)
    def test_machine_identity_and_role_credentials(self):
        for index,role in enumerate(['research','verify','engineer']):
            ip='100.64.0.'+str(index+2);key=secrets.token_urlsafe(40)
            row=self.reg.enroll(ip,role,key);self.reg.approve(row['id'])
            result=self.reg.resolve(ip,key)
            self.assertEqual(result['role'],role)
            self.assertNotIn('credentials',result)
            with self.assertRaises(PermissionError):self.reg.resolve('100.64.0.99',key)
    def test_replacement_requires_explicit_revoke(self):
        a=self.reg.enroll('100.64.0.2','research',secrets.token_urlsafe(40));self.reg.approve(a['id'])
        b=self.reg.enroll('100.64.0.3','research',secrets.token_urlsafe(40))
        with self.assertRaises(ValueError):self.reg.approve(b['id'])
    def test_idempotency_and_route_refresh(self):
        key=secrets.token_urlsafe(40);a=self.reg.enroll('100.64.0.2','verify',key)
        self.assertEqual(a,self.reg.enroll('100.64.0.2','verify',key));self.reg.approve(a['id'])
        with connect(self.root) as db:db.execute('UPDATE config SET value=?',(json.dumps({'url':'http://100.64.0.9:8110','generation':2,'mode':'research-only'}),))
        self.assertEqual(self.reg.resolve('100.64.0.2',key)['controller_generation'],2)
    def test_storage_limit(self):
        self.assertLess(capacity(self.root),1000000)

    def test_stale_registry_is_not_network_offline(self):
        key=secrets.token_urlsafe(40)
        node=self.reg.enroll('100.64.0.2','research',key);self.reg.approve(node['id'])
        status=[n for n in self.reg.status() if n['id']==node['id']][0]
        self.assertEqual(status['availability'],'REGISTRY_STALE')
        self.assertIsNone(status['registry_heartbeat_age_seconds'])

    def test_temporary_engineering_only_for_chief(self):
        chief=secrets.token_urlsafe(40);worker=secrets.token_urlsafe(40)
        a=self.reg.enroll('100.64.0.2','controller',chief);self.reg.approve(a['id'])
        b=self.reg.enroll('100.64.0.3','research',worker);self.reg.approve(b['id'])
        self.reg.delegate_engineering(True)
        self.assertNotIn('additional_roles',self.reg.resolve('100.64.0.2',chief))
        extra=self.reg.resolve('100.64.0.2',chief,include_delegation=True)['additional_roles']['engineer']
        self.assertEqual(extra['application_token'],chief)
        self.assertNotIn('additional_roles',self.reg.resolve('100.64.0.3',worker,include_delegation=True))
        pending=self.reg.enroll('100.64.0.4','engineer',secrets.token_urlsafe(40))
        with self.assertRaises(ValueError):self.reg.approve(pending['id'])
        self.reg.delegate_engineering(False)
        self.assertNotIn('additional_roles',self.reg.resolve('100.64.0.2',chief,include_delegation=True))
        self.reg.approve(pending['id'])
        with self.assertRaises(ValueError):self.reg.delegate_engineering(True)

if __name__=='__main__':unittest.main(verbosity=2)
