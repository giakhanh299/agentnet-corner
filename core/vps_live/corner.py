"""AgentNet Corner — Tailscale-verified Fleet Registry & Research Queue (10-100+ Muses)."""
import argparse
import hashlib
import hmac
import ipaddress
import json
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from research_queue import ResearchQueue, QueueError
from hub_portal import HubManager, make_hub_handler

ROOT = Path(__file__).resolve().parent
SINGLETON_ROLES = ('controller',)
POOL_ROLES = (
    'research', 'verify', 'engineer',
    'lead_research', 'lead_verify', 'lead_creative', 'lead_engineer',
)
ROLES = SINGLETON_ROLES + POOL_ROLES
LIMIT = 900_000_000  # margin below both decimal GB and GiB
MAX_ENROLLED_NODES = 512
DEFAULT_FLEET_MAX_NODES = 128
LOCK = threading.RLock()


class ManagedConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


def capacity(root=ROOT):
    total = sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink())
    if total > LIMIT:
        raise ValueError('Directory near 1 GB limit; writes disabled')
    return total


def connect(root=ROOT):
    root.mkdir(parents=True, exist_ok=True)
    state = root / 'state'
    state.mkdir(exist_ok=True)
    db = sqlite3.connect(state / 'registry.sqlite3', timeout=15, factory=ManagedConnection)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA synchronous=NORMAL')
    db.execute('PRAGMA busy_timeout=15000')
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
    raw = subprocess.check_output(['tailscale', 'whois', '--json', str(addr)], timeout=5)
    node = json.loads(raw).get('Node') or {}
    if not node.get('ID'):
        raise ValueError('Unresolved Tailscale node')
    return str(node['ID'])


class Registry:
    def __init__(self, root=ROOT, verifier=node_identity):
        self.root, self.verifier = Path(root), verifier
        db = connect(self.root)
        db.close()

    def _fleet_auto_approve_allowed(self, db, role, fleet_key):
        if role in SINGLETON_ROLES or not isinstance(fleet_key, str) or not (16 <= len(fleet_key) <= 200):
            return False
        row = db.execute("SELECT value FROM config WHERE key='fleet_key_hash'").fetchone()
        if not row:
            return False
        cfg = json.loads(row['value'])
        if not cfg.get('enabled', False):
            return False
        supplied_hash = hashlib.sha256(fleet_key.encode()).hexdigest()
        if not hmac.compare_digest(supplied_hash, cfg.get('sha256', '')):
            return False
        max_nodes = int(cfg.get('max_nodes', DEFAULT_FLEET_MAX_NODES))
        approved_count = db.execute("SELECT count(*) FROM nodes WHERE status='APPROVED'").fetchone()[0]
        return approved_count < max_nodes

    def set_fleet_key(self, fleet_key, max_nodes=DEFAULT_FLEET_MAX_NODES, enabled=True):
        if enabled and (not isinstance(fleet_key, str) or not (16 <= len(fleet_key) <= 200)):
            raise ValueError('Fleet key must be 16..200 characters')
        if not (1 <= int(max_nodes) <= MAX_ENROLLED_NODES):
            raise ValueError('Invalid max_nodes')
        with LOCK, connect(self.root) as db:
            capacity(self.root)
            if not enabled:
                db.execute("DELETE FROM config WHERE key='fleet_key_hash'")
                return
            payload = {
                'sha256': hashlib.sha256(fleet_key.encode()).hexdigest(),
                'max_nodes': int(max_nodes),
                'enabled': True,
                'updated_at': time.time(),
            }
            db.execute('INSERT OR REPLACE INTO config VALUES(?,?)', ('fleet_key_hash', json.dumps(payload)))

    def enroll(self, ip, role, token, fleet_key=None):
        if role not in ROLES or not isinstance(token, str) or not (40 <= len(token) <= 160):
            raise ValueError('Invalid role or bootstrap credential')
        device = self.verifier(ip)
        digest = hashlib.sha256(token.encode()).hexdigest()
        now = time.time()
        with LOCK, connect(self.root) as db:
            capacity(self.root)
            auto_ok = self._fleet_auto_approve_allowed(db, role, fleet_key)
            old = db.execute('SELECT * FROM nodes WHERE token_hash=?', (digest,)).fetchone()
            if old:
                if old['device_id'] != device or old['role'] != role:
                    raise PermissionError('Identity mismatch')
                if old['status'] == 'REPLACEMENT_PENDING' and auto_ok:
                    gen = db.execute(
                        'SELECT COALESCE(MAX(generation),0)+1 FROM nodes WHERE role=?', (role,)
                    ).fetchone()[0]
                    db.execute(
                        "UPDATE nodes SET status='APPROVED',generation=?,heartbeat=?,ip=? WHERE id=?",
                        (gen, now, ip, old['id']),
                    )
                    return {'id': old['id'], 'status': 'APPROVED'}
                return {'id': old['id'], 'status': old['status']}
            if db.execute('SELECT count(*) FROM nodes').fetchone()[0] >= MAX_ENROLLED_NODES:
                raise ValueError('Enrollment capacity reached; operator review required')
            nid = secrets.token_hex(12)
            if auto_ok:
                gen = db.execute(
                    'SELECT COALESCE(MAX(generation),0)+1 FROM nodes WHERE role=?', (role,)
                ).fetchone()[0]
                db.execute(
                    'INSERT INTO nodes VALUES(?,?,?,?,?,?,?,?,?)',
                    (nid, device, ip, role, digest, 'APPROVED', now, now, gen),
                )
                return {'id': nid, 'status': 'APPROVED'}
            db.execute(
                'INSERT INTO nodes VALUES(?,?,?,?,?,?,?,?,?)',
                (nid, device, ip, role, digest, 'REPLACEMENT_PENDING', now, None, 0),
            )
            return {'id': nid, 'status': 'REPLACEMENT_PENDING'}

    def authenticate(self, ip, token):
        device = self.verifier(ip)
        digest = hashlib.sha256(token.encode()).hexdigest()
        with connect(self.root) as db:
            row = db.execute('SELECT * FROM nodes WHERE token_hash=?', (digest,)).fetchone()
        if not row or row['device_id'] != device:
            raise PermissionError('Invalid device credential')
        if row['status'] != 'APPROVED':
            raise PermissionError(row['status'])
        return dict(row)

    def resolve(self, ip, token, include_delegation=False):
        row = self.authenticate(ip, token)
        with LOCK, connect(self.root) as db:
            capacity(self.root)
            db.execute('UPDATE nodes SET heartbeat=?,ip=? WHERE id=?', (time.time(), ip, row['id']))
            current = db.execute("SELECT value FROM config WHERE key='controller'").fetchone()
            delegation = db.execute("SELECT value FROM config WHERE key='engineering_delegate'").fetchone()
        if not current:
            return {'status': 'WAITING_CONTROLLER', 'role': row['role'], 'node_id': row['id']}
        config = json.loads(current['value'])
        if config.get('mode') != 'research-only':
            raise PermissionError('Research endpoint migration required; legacy routes disabled')
        result = {
            'status': 'READY',
            'node_id': row['id'],
            'role': row['role'],
            'project': 'research',
            'controller_url': config['url'],
            'controller_generation': config['generation'],
            'application_token': token,
            'mode': 'research-only',
        }
        if row['role'] == 'controller' and delegation and delegation['value'] == 'controller' and include_delegation:
            result['additional_roles'] = {
                'engineer': {'as_role': 'engineer', 'application_token': token, 'temporary': True}
            }
        return result

    def delegate_engineering(self, enabled):
        with LOCK, connect(self.root) as db:
            capacity(self.root)
            db.execute(
                'INSERT OR REPLACE INTO config VALUES(?,?)',
                ('engineering_delegate', 'controller' if enabled else 'none'),
            )

    def approve(self, nid, allow_pool=True):
        with LOCK, connect(self.root) as db:
            capacity(self.root)
            row = db.execute('SELECT * FROM nodes WHERE id=?', (nid,)).fetchone()
            if not row:
                raise ValueError('Unknown enrollment')
            if row['status'] == 'APPROVED':
                return
            if row['status'] != 'REPLACEMENT_PENDING':
                raise ValueError('Revoked requests cannot be approved again')
            # Controller (Chief) is strictly singleton to prevent split-brain command.
            # Worker/lead roles support multi-node pools when allow_pool=True.
            if row['role'] in SINGLETON_ROLES or not allow_pool:
                predecessor = db.execute(
                    "SELECT 1 FROM nodes WHERE role=? AND status='APPROVED'", (row['role'],)
                ).fetchone()
                if predecessor:
                    raise ValueError('Replacement requires credential rotation and explicit revoke first')
            generation = db.execute(
                'SELECT COALESCE(MAX(generation),0)+1 FROM nodes WHERE role=?', (row['role'],)
            ).fetchone()[0]
            db.execute("UPDATE nodes SET status='APPROVED',generation=? WHERE id=?", (generation, nid))

    def status(self):
        with connect(self.root) as db:
            rows = db.execute(
                'SELECT id,device_id,ip,role,status,heartbeat,generation FROM nodes ORDER BY role, created'
            ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            age = time.time() - d['heartbeat'] if d['heartbeat'] else None
            d['registry_heartbeat_age_seconds'] = round(age) if age is not None else None
            d['availability'] = (
                ('REGISTRY_RECENT' if age is not None and age < 180 else 'REGISTRY_STALE')
                if d['status'] == 'APPROVED'
                else d['status']
            )
            result.append(d)
        return result


class Handler(BaseHTTPRequestHandler):
    registry = None
    queue = None

    def authenticated(self):
        token = self.headers.get('Authorization', '').removeprefix('Bearer ')
        return self.registry.authenticate(self.client_address[0], token)

    def delegated(self):
        with connect(self.registry.root) as db:
            row = db.execute("SELECT value FROM config WHERE key='engineering_delegate'").fetchone()
        return bool(row and row['value'] == 'controller')

    def log_message(self, *args):
        pass  # never log credentials or bodies

    def respond(self, status, body, kind='application/json'):
        data = json.dumps(body).encode() if kind == 'application/json' else body
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            parsed = urlsplit(self.path)
            route = parsed.path
            if route == '/health':
                with connect(self.registry.root) as db:
                    approved_total = db.execute("SELECT count(*) FROM nodes WHERE status='APPROVED'").fetchone()[0]
                    fleet_cfg = db.execute("SELECT 1 FROM config WHERE key='fleet_key_hash'").fetchone() is not None
                return self.respond(200, {
                    'status': 'ok',
                    'version': '1.3-fleet',
                    'directory_bytes': capacity(self.registry.root),
                    'project': 'research',
                    'limit_bytes': LIMIT,
                    'approved_nodes': approved_total,
                    'fleet_auto_enroll': fleet_cfg,
                    'function': 'independent research registry and multi-worker queue',
                })
            pages = {
                '/': 'README.md',
                '/join.py': 'join.py',
                '/prompts/chief': 'PROMPT_CHIEF.md',
                '/prompts/worker': 'PROMPT_WORKER.md',
                '/prompts/master': 'MASTER_PROMPT_V1_2.md',
                '/prompts/master-v1.2': 'MASTER_PROMPT_V1_2.md',
            }
            if route in pages:
                return self.respond(200, (self.registry.root / pages[route]).read_bytes(), 'text/plain; charset=utf-8')
            if route == '/controller':
                token = self.headers.get('Authorization', '').removeprefix('Bearer ')
                return self.respond(200, self.registry.resolve(
                    self.client_address[0], token,
                    include_delegation=self.headers.get('X-AgentNet-Client') == 'join/2',
                ))
            if route in ('/tasks', '/agents', '/fleet') or route.startswith('/tasks/'):
                return self.respond(200, self.queue.get(self.authenticated(), self.path))
            self.respond(404, {'error': 'not_found'})
        except QueueError as e:
            self.respond(e.code, {'error': e.message})
        except PermissionError as e:
            self.respond(403, {'error': str(e)})
        except ValueError as e:
            self.respond(400, {'error': str(e)})
        except Exception:
            self.respond(503, {'error': 'registry_unavailable'})

    def do_POST(self):
        try:
            size = int(self.headers.get('Content-Length', '0'))
            limit = 16384 if self.path == '/enroll' else 1048576
            if not 1 <= size <= limit:
                return self.respond(413, {'error': 'request_size_limit'})
            self.connection.settimeout(15)
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError('JSON object required')
            capacity(self.registry.root)
            if self.path == '/enroll':
                return self.respond(200, self.registry.enroll(
                    self.client_address[0],
                    data.get('role'),
                    data.get('token'),
                    fleet_key=data.get('fleet_key'),
                ))
            self.respond(200, self.queue.post(self.authenticated(), self.path, data, self.delegated()))
        except QueueError as e:
            self.respond(e.code, {'error': e.message})
        except PermissionError as e:
            self.respond(403, {'error': str(e)})
        except (ValueError, TypeError):
            self.respond(400, {'error': 'invalid_request'})
        except Exception:
            self.respond(503, {'error': 'registry_unavailable'})


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)
    serve = sub.add_parser('serve')
    serve.add_argument('--bind', required=True)
    serve.add_argument('--port', type=int, default=8110)
    serve.add_argument('--hub-bind', default='127.0.0.1')
    serve.add_argument('--hub-port', type=int, default=8111)
    sub.add_parser('status')
    approve = sub.add_parser('approve')
    approve.add_argument('id')
    approve.add_argument('--singleton', action='store_true', help='Enforce single active node for this role')
    sub.add_parser('approve-all-pending')
    delegate = sub.add_parser('delegate-engineering')
    delegate.add_argument('mode', choices=['on', 'off'])
    revoke = sub.add_parser('revoke')
    revoke.add_argument('id')
    fkey = sub.add_parser('fleet-key')
    fkey.add_argument('action', choices=['generate', 'disable'])
    fkey.add_argument('--max-nodes', type=int, default=DEFAULT_FLEET_MAX_NODES)
    hadm = sub.add_parser('hub-admin')
    hadm.add_argument('action', choices=['generate'])
    hinv = sub.add_parser('hub-invite')
    hinv.add_argument('action', choices=['create'])
    hinv.add_argument('--ttl', type=int, default=180)
    hinv.add_argument('--max-uses', type=int, default=20)
    route = sub.add_parser('route')
    route.add_argument('url')
    route.add_argument('--research-only', action='store_true', required=True)
    args = parser.parse_args()
    registry = Registry()
    queue = ResearchQueue(ROOT)
    hub = HubManager(registry, queue, connect, capacity, LOCK)
    if args.cmd == 'serve':
        if ipaddress.ip_address(args.bind) not in ipaddress.ip_network('100.64.0.0/10'):
            raise SystemExit('Bind must be Tailscale IPv4')
        if ipaddress.ip_address(args.hub_bind) != ipaddress.ip_address('127.0.0.1'):
            raise SystemExit('Hub listener must bind to 127.0.0.1 behind TLS reverse proxy')
        Handler.registry = registry
        Handler.queue = queue
        if args.hub_port > 0:
            hub_srv = ThreadingHTTPServer((args.hub_bind, args.hub_port), make_hub_handler(hub))
            threading.Thread(target=hub_srv.serve_forever, daemon=True).start()
        ThreadingHTTPServer((args.bind, args.port), Handler).serve_forever()
    elif args.cmd == 'status':
        print(json.dumps(registry.status(), indent=2))
    elif args.cmd == 'approve':
        registry.approve(args.id, allow_pool=not args.singleton)
        print('Approved; role credential can be retrieved by this verified device')
    elif args.cmd == 'approve-all-pending':
        approved_ids = []
        for n in registry.status():
            if n['status'] == 'REPLACEMENT_PENDING' and n['role'] not in SINGLETON_ROLES:
                registry.approve(n['id'], allow_pool=True)
                approved_ids.append(n['id'])
        print(json.dumps({'approved_worker_ids': approved_ids}))
    elif args.cmd == 'delegate-engineering':
        registry.delegate_engineering(args.mode == 'on')
        print('Temporary Chief engineering delegation: ' + args.mode)
    elif args.cmd == 'fleet-key':
        if args.action == 'disable':
            registry.set_fleet_key('', enabled=False)
            print('Fleet auto-enrollment disabled')
        else:
            raw_key = 'fleet_' + secrets.token_urlsafe(24)
            registry.set_fleet_key(raw_key, max_nodes=args.max_nodes, enabled=True)
            print(json.dumps({'fleet_key': raw_key, 'max_nodes': args.max_nodes}))
    elif args.cmd == 'hub-admin':
        adm_key = 'adm_' + secrets.token_urlsafe(28)
        hub.set_admin_key(adm_key)
        print(json.dumps({'admin_key': adm_key}))
    elif args.cmd == 'hub-invite':
        inv = hub.create_invite(ttl_minutes=args.ttl, max_uses=args.max_uses)
        print(json.dumps(inv))
    elif args.cmd == 'revoke':
        with connect() as db:
            db.execute("UPDATE nodes SET status='REVOKED' WHERE id=?", (args.id,))
        print('Registry revoked. Rotate the old application credential before approving a replacement.')
    elif args.cmd == 'route':
        url = urlsplit(args.url)
        if url.scheme != 'http' or not url.hostname or url.path not in ('', '/') or url.username or url.password or url.query or url.fragment:
            raise SystemExit('Explicit Tailscale HTTP origin required')
        if ipaddress.ip_address(url.hostname) not in ipaddress.ip_network('100.64.0.0/10'):
            raise SystemExit('Only Tailscale origins accepted')
        if url.port in (8000, 8101):
            raise SystemExit('Legacy Facebook ports cannot be research controllers')
        with connect() as db:
            old = db.execute("SELECT value FROM config WHERE key='controller'").fetchone()
            gen = json.loads(old['value'])['generation'] + 1 if old else 1
            db.execute(
                'INSERT OR REPLACE INTO config VALUES(?,?)',
                ('controller', json.dumps({'url': args.url.rstrip('/'), 'generation': gen, 'mode': 'research-only'})),
            )
        print('Controller route updated; future nodes must refresh it before claiming jobs')


if __name__ == '__main__':
    main()
