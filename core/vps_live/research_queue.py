"""Independent research & multi-worker fleet queue (10-100+ Muses, 2/3-tier)."""
from contextlib import contextmanager
import json
import sqlite3
import time
import uuid
from urllib.parse import parse_qs, urlsplit

PROJECT = 'research'
STUDIO_ROLES = ('director', 'artist', 'animator', 'qa_critic', 'chief')
LEAD_ROLES = ('lead_research', 'lead_verify', 'lead_creative', 'lead_engineer', 'chief')
WORKER_ROLES = ('research', 'verify', 'engineer') + STUDIO_ROLES
ASSIGNABLE_ROLES = tuple(dict.fromkeys(WORKER_ROLES + LEAD_ROLES))


class QueueError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message


def validate_payload(value):
    if isinstance(value, dict):
        for item in value.values():
            validate_payload(item)
    elif isinstance(value, list):
        for item in value:
            validate_payload(item)
    elif isinstance(value, str):
        for part in value.split():
            if part.startswith(('http://', 'https://')):
                try:
                    url = urlsplit(part.rstrip('.,)'))
                    port = url.port
                except ValueError:
                    raise QueueError(400, 'Invalid source URL')
                if url.hostname == '100.67.236.124' and port in (8000, 8101):
                    raise QueueError(400, 'Facebook project endpoints are not research sources')
                if any(s in url.path for s in ['/monetization-advisor', '/video-audit', '/submit-monetization-advice', '/submit-audit-advice']):
                    raise QueueError(400, 'Facebook audit integration is disabled in this project')


class ResearchQueue:
    def __init__(self, root):
        self.root = root
        with self.db() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS tasks(
                id TEXT PRIMARY KEY,dedup TEXT UNIQUE,project TEXT,assigned_to TEXT,
                kind TEXT,payload TEXT,status TEXT,created_at REAL,started_at REAL,
                completed_at REAL,result TEXT,lease TEXT,lease_until REAL,owner_node TEXT);
                CREATE INDEX IF NOT EXISTS idx_tasks_claim ON tasks(assigned_to, status, created_at);
                CREATE TABLE IF NOT EXISTS activity(node_id TEXT,role TEXT,last_seen REAL,
                capabilities TEXT,PRIMARY KEY(node_id,role));''')

    @contextmanager
    def db(self):
        state = self.root / 'state'
        state.mkdir(exist_ok=True)
        c = sqlite3.connect(state / 'research.sqlite3', timeout=15)
        c.row_factory = sqlite3.Row
        c.execute('PRAGMA journal_mode=WAL')
        c.execute('PRAGMA synchronous=NORMAL')
        c.execute('PRAGMA busy_timeout=15000')
        c.execute('PRAGMA max_page_count=65536')
        try:
            with c:
                yield c
        finally:
            c.close()

    def chief(self, node):
        if node['role'] not in ('controller', 'chief'):
            raise QueueError(403, 'Chief only')

    def coordinator(self, node):
        if node['role'] not in ('controller', 'chief') and node['role'] not in LEAD_ROLES:
            raise QueueError(403, 'Chief or Squad Lead only')

    def role(self, node, body, delegated):
        role = node['role']
        if role == 'controller':
            if body.get('as_role', body.get('role')) != 'engineer' or not delegated:
                raise QueueError(403, 'Chief must explicitly claim as delegated engineer')
            return 'engineer'
        return role

    def decode(self, row):
        data = dict(row)
        for k in ['payload', 'result']:
            if data[k]:
                data[k] = json.loads(data[k])
        return data

    def _validate_task_spec(self, spec, creator_role):
        if not isinstance(spec, dict):
            raise QueueError(400, 'Invalid task')
        if spec.get('project', PROJECT) != PROJECT:
            raise QueueError(400, 'Research project only')
        role = spec.get('assigned_to')
        allowed_targets = ASSIGNABLE_ROLES if creator_role in ('controller', 'chief') else WORKER_ROLES
        if role not in allowed_targets:
            raise QueueError(400, 'Invalid research role')
        dedup = spec.get('dedup')
        kind = spec.get('kind')
        payload = spec.get('payload')
        if (
            not isinstance(dedup, str) or not 1 <= len(dedup) <= 200
            or not isinstance(kind, str) or not 1 <= len(kind) <= 80
            or not isinstance(payload, dict)
        ):
            raise QueueError(400, 'Invalid task')
        req_caps = payload.get('required_capabilities')
        if req_caps is not None:
            if not isinstance(req_caps, list) or len(req_caps) > 32 or not all(isinstance(v, str) and len(v) < 100 for v in req_caps):
                raise QueueError(400, 'Invalid required_capabilities')
        if spec.get('auto_verify') is True and 'auto_verify' not in payload:
            payload = dict(payload)
            payload['auto_verify'] = True
        validate_payload(payload)
        return role, kind, dedup, payload

    def _insert_task_tx(self, c, role, kind, dedup, payload, now):
        existing = c.execute('SELECT * FROM tasks WHERE dedup=?', (dedup,)).fetchone()
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        if existing:
            if (existing['assigned_to'], existing['kind'], existing['payload']) != (role, kind, encoded):
                raise QueueError(409, 'Dedup reused with different task')
            return existing['id'], False
        tid = str(uuid.uuid4())
        c.execute(
            'INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (tid, dedup, PROJECT, role, kind, encoded, 'QUEUED', now, None, None, None, None, None, None),
        )
        return tid, True

    def get(self, node, full_path):
        parsed = urlsplit(full_path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        now = time.time()

        # Direct task lookup: Chief, Squad Leads, Verify workers, or the task's owner_node
        parts = path.strip('/').split('/')
        if len(parts) == 2 and parts[0] == 'tasks':
            tid = parts[1]
            with self.db() as c:
                row = c.execute('SELECT * FROM tasks WHERE id=?', (tid,)).fetchone()
            if not row:
                raise QueueError(404, 'Research task not found')
            can_read = (
                node['role'] in ('controller', 'chief', 'verify', 'qa_critic', 'director')
                or node['role'] in LEAD_ROLES
                or row['owner_node'] == node['id']
            )
            if not can_read:
                raise QueueError(403, 'Task read not permitted for this role')
            return self.decode(row)

        self.coordinator(node)
        with self.db() as c:
            if path == '/tasks':
                clauses = []
                params = []
                if 'status' in qs and qs['status'][0]:
                    clauses.append('status=?')
                    params.append(qs['status'][0])
                if 'assigned_to' in qs and qs['assigned_to'][0]:
                    clauses.append('assigned_to=?')
                    params.append(qs['assigned_to'][0])
                try:
                    limit = max(1, min(1000, int(qs.get('limit', ['500'])[0])))
                except ValueError:
                    limit = 500
                where = (' WHERE ' + ' AND '.join(clauses)) if clauses else ''
                rows = c.execute(
                    f'SELECT * FROM tasks{where} ORDER BY created_at DESC LIMIT ?',
                    (*params, limit),
                ).fetchall()
                return [self.decode(r) for r in rows]
            if path == '/agents':
                rows = c.execute('SELECT * FROM activity ORDER BY last_seen DESC').fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    d['last_seen_age_seconds'] = round(now - d['last_seen']) if d['last_seen'] else None
                    out.append(d)
                return out
            if path == '/fleet':
                counts = [
                    dict(r) for r in c.execute(
                        'SELECT assigned_to, status, count(*) AS count FROM tasks GROUP BY assigned_to, status'
                    ).fetchall()
                ]
                active_5m = c.execute('SELECT count(*) FROM activity WHERE last_seen > ?', (now - 300,)).fetchone()[0]
                active_15m = c.execute('SELECT count(*) FROM activity WHERE last_seen > ?', (now - 900,)).fetchone()[0]
                return {
                    'project': PROJECT,
                    'active_workers_5m': active_5m,
                    'active_workers_15m': active_15m,
                    'task_counts': counts,
                }
        raise QueueError(404, 'Not found')

    def post(self, node, path, body, delegated=False):
        now = time.time()
        if path == '/tasks':
            self.coordinator(node)
            role, kind, dedup, payload = self._validate_task_spec(body, node['role'])
            with self.db() as c:
                c.execute('BEGIN IMMEDIATE')
                tid, _ = self._insert_task_tx(c, role, kind, dedup, payload, now)
            return {'id': tid, 'project': PROJECT}

        if path == '/tasks/batch':
            self.coordinator(node)
            if body.get('project', PROJECT) != PROJECT:
                raise QueueError(400, 'Research project only')
            items = body.get('tasks')
            if not isinstance(items, list) or not (1 <= len(items) <= 200):
                raise QueueError(400, 'Batch requires 1..200 tasks')
            validated = [self._validate_task_spec(item, node['role']) for item in items]
            seen_dedups = {}
            for role, kind, dedup, payload in validated:
                enc = json.dumps(payload, ensure_ascii=False, sort_keys=True)
                if dedup in seen_dedups and seen_dedups[dedup] != (role, kind, enc):
                    raise QueueError(409, 'Duplicate conflicting dedup inside batch')
                seen_dedups[dedup] = (role, kind, enc)
            results = []
            with self.db() as c:
                c.execute('BEGIN IMMEDIATE')
                for role, kind, dedup, payload in validated:
                    tid, created = self._insert_task_tx(c, role, kind, dedup, payload, now)
                    results.append({'id': tid, 'dedup': dedup, 'created': created})
            return {'tasks': results, 'count': len(results), 'project': PROJECT}

        if path == '/claim':
            role = self.role(node, body, delegated)
            caps = body.get('capabilities', [])
            if not isinstance(caps, list) or len(caps) > 32 or not all(isinstance(v, str) and len(v) < 100 for v in caps):
                raise QueueError(400, 'Invalid capabilities')
            cap_set = set(caps)
            with self.db() as c:
                c.execute('BEGIN IMMEDIATE')
                c.execute('INSERT OR REPLACE INTO activity VALUES(?,?,?,?)', (node['id'], role, now, json.dumps(caps)))
                c.execute(
                    "UPDATE tasks SET status='QUEUED',lease=NULL,lease_until=NULL,owner_node=NULL WHERE status='RUNNING' AND lease_until<?",
                    (now,),
                )
                row = c.execute(
                    "SELECT * FROM tasks WHERE status='RUNNING' AND owner_node=? LIMIT 1",
                    (node['id'],),
                ).fetchone()
                if not row:
                    # Check if this node recently hit video quota exhaustion or submitted non-.mp4 to muse_make_videos
                    vid_exhausted = False
                    recent_vid_rows = c.execute(
                        "SELECT result FROM tasks WHERE kind='muse_make_videos' AND owner_node=? AND completed_at>? LIMIT 5",
                        (node['id'], now - 21600),
                    ).fetchall()
                    for rvr in recent_vid_rows:
                        rtxt = (rvr['result'] or '').lower()
                        if ('video_daily_budget_exhausted' in rtxt or 'video quota exhausted' in rtxt
                                or 'outside the research-only role' in rtxt):
                            vid_exhausted = True
                            break

                    if role == 'artist':
                        candidates = c.execute(
                            "SELECT * FROM tasks WHERE status='QUEUED' AND (assigned_to='artist' OR (assigned_to='research' AND kind='muse_draw_images')) ORDER BY CASE WHEN assigned_to='artist' THEN 0 ELSE 1 END, created_at LIMIT 80"
                        ).fetchall()
                    elif role == 'animator':
                        candidates = c.execute(
                            "SELECT * FROM tasks WHERE status='QUEUED' AND (assigned_to='animator' OR (assigned_to='research' AND kind='muse_make_videos')) ORDER BY CASE WHEN assigned_to='animator' THEN 0 ELSE 1 END, created_at LIMIT 80"
                        ).fetchall()
                    elif role == 'qa_critic':
                        candidates = c.execute(
                            "SELECT * FROM tasks WHERE status='QUEUED' AND assigned_to IN ('qa_critic', 'verify') ORDER BY created_at LIMIT 80"
                        ).fetchall()
                    elif role == 'director':
                        candidates = c.execute(
                            "SELECT * FROM tasks WHERE status='QUEUED' AND assigned_to='director' ORDER BY created_at LIMIT 80"
                        ).fetchall()
                    else:
                        candidates = c.execute(
                            "SELECT * FROM tasks WHERE assigned_to=? AND status='QUEUED' ORDER BY created_at LIMIT 80",
                            (role,),
                        ).fetchall()
                    chosen = None
                    for cand in candidates:
                        p = json.loads(cand['payload']) if cand['payload'] else {}
                        if node['id'] in (p.get('excluded_nodes') or []):
                            continue
                        if vid_exhausted and cand['kind'] == 'muse_make_videos':
                            continue
                        req = p.get('required_capabilities') or []
                        if all(r in cap_set for r in req):
                            chosen = cand
                            break
                    if not chosen:
                        return {'id': None, 'project': PROJECT}
                    c.execute(
                        "UPDATE tasks SET status='RUNNING',started_at=COALESCE(started_at,?),lease=?,lease_until=?,owner_node=? WHERE id=?",
                        (now, str(uuid.uuid4()), now + 900, node['id'], chosen['id']),
                    )
                    row = c.execute('SELECT * FROM tasks WHERE id=?', (chosen['id'],)).fetchone()
                return self.decode(row)

        parts = path.strip('/').split('/')
        if len(parts) != 3 or parts[0] != 'tasks' or parts[2] not in ('heartbeat', 'result', 'approve'):
            raise QueueError(404, 'Not found')
        tid, action = parts[1:]
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            row = c.execute('SELECT * FROM tasks WHERE id=?', (tid,)).fetchone()
            if not row:
                raise QueueError(404, 'Research task not found')
            if action == 'approve':
                self.chief(node)
                if row['status'] not in ('SUBMITTED', 'APPROVED'):
                    raise QueueError(409, 'No submitted result')
                result = json.loads(row['result'])
                if result.get('outcome') not in ('ok', 'PASS'):
                    raise QueueError(409, 'Cannot approve a blocked or failed result')
                c.execute("UPDATE tasks SET status='APPROVED' WHERE id=?", (tid,))
                return {'status': 'APPROVED', 'project': PROJECT}
            role = self.role(node, body, delegated)
            if row['owner_node'] != node['id'] or row['lease'] != body.get('lease'):
                raise QueueError(403, 'Wrong role, node or lease')
            if action == 'heartbeat':
                if row['status'] != 'RUNNING' or row['lease_until'] < now:
                    raise QueueError(409, 'Lease expired or finished')
                c.execute('UPDATE tasks SET lease_until=? WHERE id=?', (now + 900, tid))
                return {'status': 'ok', 'project': PROJECT}
            result = body.get('result')
            if not isinstance(result, dict):
                raise QueueError(400, 'Result object required')
            validate_payload(result)
            data = json.dumps(result, sort_keys=True, ensure_ascii=False)
            if len(data.encode()) > 256000:
                raise QueueError(413, 'Use media links')
            if row['status'] in ('SUBMITTED', 'APPROVED'):
                if row['result'] != data:
                    raise QueueError(409, 'Different result already received')
                return {'status': row['status'], 'received': True, 'project': PROJECT}
            if row['status'] != 'RUNNING' or row['lease_until'] < now:
                raise QueueError(409, 'Lease expired')
            c.execute("UPDATE tasks SET status='SUBMITTED',result=?,completed_at=? WHERE id=?", (data, now, tid))

            # Optional Auto-Verify pipeline trigger: spawns paired verify task automatically
            auto_verify_tid = None
            task_payload = json.loads(row['payload']) if row['payload'] else {}
            if (
                task_payload.get('auto_verify') is True
                and role != 'verify'
                and result.get('outcome') in ('ok', 'PASS', 'completed')
            ):
                v_dedup = f'auto-verify:{tid}'
                v_payload = {
                    'objective': f'Independent verification of submitted task {tid} ({row["kind"]}). Read GET /tasks/{tid} for full payload and result.',
                    'target_task_id': tid,
                    'parent_role': role,
                    'parent_kind': row['kind'],
                    'acceptance_criteria': task_payload.get('acceptance_criteria', 'Cross-check sources, claims, numbers, and limitations.'),
                }
                auto_verify_tid, _ = self._insert_task_tx(c, 'verify', 'verification', v_dedup, v_payload, now)

            resp = {'status': 'SUBMITTED', 'received': True, 'project': PROJECT}
            if auto_verify_tid:
                resp['verify_task_id'] = auto_verify_tid
            return resp
