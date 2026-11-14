"""Small, additive AgentNet registry. No LLM, media storage, or legacy changes."""
import argparse
import hashlib
import ipaddress
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from research_queue import ResearchQueue, QueueError

ROOT = Path(__file__).resolve().parent
ROLES = ('controller','research','verify','engineer')
LIMIT = 900_000_000  # margin below both decimal GB and GiB
LOCK = threading.RLock()

class ManagedConnection(sqlite3.Connection):
    def __exit__(self,*args):
        try:return super().__exit__(*args)
        finally:self.close()

def capacity(root=ROOT):
    total = sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink())
    if total > LIMIT: raise ValueError('Directory near 1 GB limit; writes disabled')
    return total

def connect(root=ROOT):
    root.mkdir(parents=True, exist_ok=True)
    state=root/'state';state.mkdir(exist_ok=True)
    db = sqlite3.connect(state/'registry.sqlite3', timeout=15,factory=ManagedConnection)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA max_page_count=65536')  # <=256 MiB at default 4096-byte pages
    db.executescript('''CREATE TABLE IF NOT EXISTS nodes(
        id TEXT PRIMARY KEY, device_id TEXT NOT NULL, ip TEXT NOT NULL,
        role TEXT NOT NULL, token_hash TEXT NOT NULL, status TEXT NOT NULL,
        created REAL NOT NULL, heartbeat REAL, generation INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS config(key TEXT PRIMARY KEY,value TEXT);''')
    return db

def node_identity(ip):
    addr = ipaddress.ip_address(ip)
    if addr not in ipaddress.ip_network('100.64.0.0/10'):
        raise ValueError('A verified Tailscale source is required')
    raw = subprocess.check_output(['tailscale','whois','--json',str(addr)], timeout=5)
    node = json.loads(raw).get('Node') or {}
    if not node.get('ID'): raise ValueError('Unresolved Tailscale node')
    return str(node['ID'])

class Registry:
    def __init__(self, root=ROOT, verifier=node_identity):
        self.root, self.verifier = Path(root), verifier
        db=connect(self.root);db.close()

    def enroll(self, ip, role, token):
        if role not in ROLES or not isinstance(token,str) or not 40 <= len(token) <= 160:
            raise ValueError('Invalid role or bootstrap credential')
        device=self.verifier(ip)
        digest=hashlib.sha256(token.encode()).hexdigest()
        with LOCK, connect(self.root) as db:
            capacity(self.root)
            old=db.execute('SELECT * FROM nodes WHERE token_hash=?',(digest,)).fetchone()
            if old:
                if old['device_id']!=device or old['role']!=role: raise PermissionError('Identity mismatch')
                return {'id':old['id'],'status':old['status']}
            if db.execute('SELECT count(*) FROM nodes').fetchone()[0]>=256:
                raise ValueError('Enrollment capacity reached; operator review required')
            nid=secrets.token_hex(12)
            db.execute('INSERT INTO nodes VALUES(?,?,?,?,?,?,?,?,?)',
                (nid,device,ip,role,digest,'REPLACEMENT_PENDING',time.time(),None,0))
            return {'id':nid,'status':'REPLACEMENT_PENDING'}

    def authenticate(self, ip, token):
        device=self.verifier(ip)
        digest=hashlib.sha256(token.encode()).hexdigest()
        with connect(self.root) as db:
            row=db.execute('SELECT * FROM nodes WHERE token_hash=?',(digest,)).fetchone()
        if not row or row['device_id']!=device: raise PermissionError('Invalid device credential')
        if row['status']!='APPROVED': raise PermissionError(row['status'])
        return dict(row)

    def resolve(self, ip, token, include_delegation=False):
        row=self.authenticate(ip,token)
        with LOCK,connect(self.root) as db:
            capacity(self.root)
            db.execute('UPDATE nodes SET heartbeat=?,ip=? WHERE id=?',(time.time(),ip,row['id']))
            current=db.execute("SELECT value FROM config WHERE key='controller'").fetchone()
            delegation=db.execute("SELECT value FROM config WHERE key='engineering_delegate'").fetchone()
        if not current: return {'status':'WAITING_CONTROLLER','role':row['role']}
        config=json.loads(current['value'])
        if config.get('mode')!='research-only':
            raise PermissionError('Research endpoint migration required; legacy routes disabled')
        result={'status':'READY','role':row['role'],'project':'research',
            'controller_url':config['url'],'controller_generation':config['generation'],
            'application_token':token,'mode':'research-only'}
        if row['role']=='controller' and delegation and delegation['value']=='controller' and include_delegation:
            result['additional_roles']={'engineer':{'as_role':'engineer',
                'application_token':token,'temporary':True}}
        return result

    def delegate_engineering(self, enabled):
        with LOCK,connect(self.root) as db:
            capacity(self.root)
            if enabled and db.execute("SELECT 1 FROM nodes WHERE role='engineer' AND status='APPROVED'").fetchone():
                raise ValueError('An Engineer node is already approved; resolve ownership first')
            db.execute('INSERT OR REPLACE INTO config VALUES(?,?)',
                ('engineering_delegate','controller' if enabled else 'none'))

    def approve(self,nid):
        with LOCK,connect(self.root) as db:
            capacity(self.root)
            row=db.execute('SELECT * FROM nodes WHERE id=?',(nid,)).fetchone()
            if not row: raise ValueError('Unknown enrollment')
            if row['status']=='APPROVED': return
            if row['status']!='REPLACEMENT_PENDING': raise ValueError('Revoked requests cannot be approved again')
            delegation=db.execute("SELECT value FROM config WHERE key='engineering_delegate'").fetchone()
            if row['role']=='engineer' and delegation and delegation['value']=='controller':
                raise ValueError('Disable temporary Chief engineering delegation before approving an Engineer node')
            # Replacing the role explicitly revokes the predecessor in the registry.
            # Legacy API credentials also need rotation before production replacement.
            predecessor=db.execute("SELECT 1 FROM nodes WHERE role=? AND status='APPROVED'",(row['role'],)).fetchone()
            if predecessor: raise ValueError('Replacement requires credential rotation and explicit revoke first')
            generation=db.execute('SELECT COALESCE(MAX(generation),0)+1 FROM nodes WHERE role=?',(row['role'],)).fetchone()[0]
            db.execute("UPDATE nodes SET status='APPROVED',generation=? WHERE id=?",(generation,nid))

    def status(self):
        with connect(self.root) as db: rows=db.execute('SELECT id,device_id,ip,role,status,heartbeat,generation FROM nodes').fetchall()
        result=[]
        for row in rows:
            d=dict(row)
            age=time.time()-d['heartbeat'] if d['heartbeat'] else None
            d['registry_heartbeat_age_seconds']=round(age) if age is not None else None
            d['availability']=('REGISTRY_RECENT' if age is not None and age<180 else 'REGISTRY_STALE') if d['status']=='APPROVED' else d['status']
            result.append(d)
        return result

class Handler(BaseHTTPRequestHandler):
    registry=None
    queue=None
    def authenticated(self):
        token=self.headers.get('Authorization','').removeprefix('Bearer ')
        return self.registry.authenticate(self.client_address[0],token)
    def delegated(self):
        with connect(self.registry.root) as db:
            row=db.execute("SELECT value FROM config WHERE key='engineering_delegate'").fetchone()
        return bool(row and row['value']=='controller')
    def log_message(self,*args): pass  # never log credentials or bodies
    def respond(self,status,body,kind='application/json'):
        data=json.dumps(body).encode() if kind=='application/json' else body
        self.send_response(status);self.send_header('Content-Type',kind)
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        try:
            if self.path=='/health':
                return self.respond(200,{'status':'ok','directory_bytes':capacity(self.registry.root),
                    'project':'research','limit_bytes':LIMIT,'function':'independent research registry and queue'})
            pages={'/':'README.md','/prompts/chief':'PROMPT_CHIEF.md',
                '/prompts/worker':'PROMPT_WORKER.md','/prompts/master':'MASTER_PROMPT_V1_2.md',
                '/prompts/master-v1.2':'MASTER_PROMPT_V1_2.md'}
            if self.path in pages:
                return self.respond(200,(self.registry.root/pages[self.path]).read_bytes(),'text/plain; charset=utf-8')
            if self.path=='/controller':
                token=self.headers.get('Authorization','').removeprefix('Bearer ')
                return self.respond(200,self.registry.resolve(self.client_address[0],token,
                    include_delegation=self.headers.get('X-AgentNet-Client')=='join/2'))
            if self.path in ('/tasks','/agents'):
                return self.respond(200,self.queue.get(self.authenticated(),self.path))
            self.respond(404,{'error':'not_found'})
        except QueueError as e:self.respond(e.code,{'error':e.message})
        except PermissionError as e:self.respond(403,{'error':str(e)})
        except ValueError as e:self.respond(400,{'error':str(e)})
        except Exception:self.respond(503,{'error':'registry_unavailable'})
    def do_POST(self):
        try:
            size=int(self.headers.get('Content-Length','0'))
            limit=16384 if self.path=='/enroll' else 262144
            if not 1<=size<=limit:return self.respond(413,{'error':'request_size_limit'})
            self.connection.settimeout(10)
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict):raise ValueError('JSON object required')
            capacity(self.registry.root)
            if self.path=='/enroll':
                return self.respond(200,self.registry.enroll(self.client_address[0],data.get('role'),data.get('token')))
            self.respond(200,self.queue.post(self.authenticated(),self.path,data,self.delegated()))
        except QueueError as e:self.respond(e.code,{'error':e.message})
        except PermissionError as e:self.respond(403,{'error':str(e)})
        except (ValueError,TypeError):self.respond(400,{'error':'invalid_request'})
        except Exception:self.respond(503,{'error':'registry_unavailable'})

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest='cmd',required=True)
    serve=sub.add_parser('serve');serve.add_argument('--bind',required=True);serve.add_argument('--port',type=int,default=8110)
    sub.add_parser('status')
    approve=sub.add_parser('approve');approve.add_argument('id')
    delegate=sub.add_parser('delegate-engineering');delegate.add_argument('mode',choices=['on','off'])
    revoke=sub.add_parser('revoke');revoke.add_argument('id')
    route=sub.add_parser('route');route.add_argument('url');route.add_argument('--research-only',action='store_true',required=True)
    args=parser.parse_args();registry=Registry()
    if args.cmd=='serve':
        if ipaddress.ip_address(args.bind) not in ipaddress.ip_network('100.64.0.0/10'):raise SystemExit('Bind must be Tailscale IPv4')
        Handler.registry=registry
        Handler.queue=ResearchQueue(ROOT)
        ThreadingHTTPServer((args.bind,args.port),Handler).serve_forever()
    elif args.cmd=='status':print(json.dumps(registry.status(),indent=2))
    elif args.cmd=='approve':registry.approve(args.id);print('Approved; role credential can be retrieved by this verified device')
    elif args.cmd=='delegate-engineering':
        registry.delegate_engineering(args.mode=='on');print('Temporary Chief engineering delegation: '+args.mode)
    elif args.cmd=='revoke':
        with connect() as db:db.execute("UPDATE nodes SET status='REVOKED' WHERE id=?",(args.id,))
        print('Registry revoked. Rotate the old application credential before approving a replacement.')
    elif args.cmd=='route':
        from urllib.parse import urlsplit
        url=urlsplit(args.url)
        if url.scheme!='http' or not url.hostname or url.path not in ('','/') or url.username or url.password or url.query or url.fragment:raise SystemExit('Explicit Tailscale HTTP origin required')
        if ipaddress.ip_address(url.hostname) not in ipaddress.ip_network('100.64.0.0/10'):raise SystemExit('Only Tailscale origins accepted')
        if url.port in (8000,8101):raise SystemExit('Legacy Facebook ports cannot be research controllers')
        with connect() as db:
            old=db.execute("SELECT value FROM config WHERE key='controller'").fetchone()
            gen=json.loads(old['value'])['generation']+1 if old else 1
            db.execute('INSERT OR REPLACE INTO config VALUES(?,?)',('controller',json.dumps({'url':args.url.rstrip('/'),'generation':gen,'mode':'research-only'})))
        print('Controller route updated; future nodes must refresh it before claiming jobs')

if __name__=='__main__':main()
