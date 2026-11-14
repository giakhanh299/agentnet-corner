import json,secrets,tempfile,threading,unittest
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from corner import Registry,Handler,connect
from research_queue import ResearchQueue

class HttpTests(unittest.TestCase):
    def test_research_only_transport_and_revocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            reg=Registry(root,lambda _: 'mock-transport-test-device')
            tokens={r:secrets.token_urlsafe(40) for r in ['controller','research','verify']}
            ids={}
            for role,token in tokens.items():
                n=reg.enroll('127.0.0.1',role,token);reg.approve(n['id']);ids[role]=n['id']
            with connect(root) as c:c.execute('INSERT INTO config VALUES(?,?)',('controller',json.dumps({'url':'http://100.64.0.1:8110','generation':2,'mode':'research-only'})))
            h=type('TestHandler',(Handler,),{'registry':reg,'queue':ResearchQueue(root)})
            server=ThreadingHTTPServer(('127.0.0.1',0),h)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            def call(path,role=None,body=None,token=None):
                headers={'Content-Type':'application/json'}
                if role or token:headers['Authorization']='Bearer '+(token or tokens[role])
                req=Request(f'http://127.0.0.1:{server.server_port}'+path,headers=headers,data=json.dumps(body).encode() if body is not None else None)
                try:
                    with urlopen(req,timeout=5) as r:return r.status,json.load(r)
                except HTTPError as e:return e.code,json.load(e)
            try:
                self.assertEqual(call('/health')[1]['project'],'research')
                self.assertEqual(call('/tasks','controller')[1],[])
                self.assertEqual(call('/tasks',token='old-facebook-credential')[0],403)
                self.assertEqual(call('/tasks','research')[0],403)
                body={'project':'research','assigned_to':'research','kind':'test','dedup':'http-test','payload':{'objective':'Transport smoke'}}
                status,task=call('/tasks','controller',body);self.assertEqual(status,200)
                status,claim=call('/claim','research',{'capabilities':['test']});self.assertEqual(status,200)
                self.assertEqual(claim['id'],task['id']);self.assertEqual(claim['project'],'research')
                result={'lease':claim['lease'],'result':{'outcome':'ok','summary':'Transport test'}}
                self.assertEqual(call('/tasks/'+task['id']+'/result','research',result)[0],200)
                self.assertEqual(call('/tasks/'+task['id']+'/approve','controller',{})[0],200)
                body['dedup']='fb-rejected';body['payload']={'source_url':'http://100.67.236.124:8000/video-audit'}
                self.assertEqual(call('/tasks','controller',body)[0],400)
                with connect(root) as c:c.execute("UPDATE nodes SET status='REVOKED' WHERE id=?",(ids['controller'],))
                self.assertEqual(call('/tasks','controller')[0],403)
            finally:server.shutdown();server.server_close();thread.join(timeout=5)

if __name__=='__main__':unittest.main(verbosity=2)
