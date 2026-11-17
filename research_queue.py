"""Independent research & autonomous studio queue (V2.0 Auto-99%).
Preserves strict isolation from legacy Facebook ports/endpoints while adding:
- Task DAG dependencies (WAITING_DEPS -> QUEUED)
- GPU-preferred -> CPU-fallback capability routing
- Targeted Verify read access (GET /tasks/<target_id>)
- Closed-loop Auto-Verify, Auto-Approve, bounded Auto-Retry, and Escalation
- Staging Review & Lessons store for the 1% Human Telegram Gate
"""
from contextlib import contextmanager
import json
import sqlite3
import time
import uuid
from urllib.parse import urlsplit

PROJECT = 'research'
ALLOWED_PROJECTS = ('research', 'studio')
GPU_ACTIVE_WINDOW_S = 120.0
DEFAULT_FALLBACK_AFTER_S = 45.0


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
                if any(s in url.path for s in [
                    '/monetization-advisor',
                    '/video-audit',
                    '/submit-monetization-advice',
                    '/submit-audit-advice',
                ]):
                    raise QueueError(400, 'Facebook audit integration is disabled in this project')


def _json_load_or(raw, default):
    if not raw:
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


class ResearchQueue:
    EXTRA_TASK_COLUMNS = {
        'parent_id': 'TEXT',
        'depends_on': 'TEXT',
        'pipeline_id': 'TEXT',
        'required_capabilities': 'TEXT',
        'preferred_capabilities': 'TEXT',
        'fallback_after_seconds': 'REAL DEFAULT 45',
        'auto_verify': 'INTEGER DEFAULT 0',
        'auto_approve': 'INTEGER DEFAULT 0',
        'attempt': 'INTEGER DEFAULT 1',
        'max_retries': 'INTEGER DEFAULT 2',
        'target_task_id': 'TEXT',
        'queued_at': 'REAL',
    }

    def __init__(self, root):
        self.root = root
        with self.db() as c:
            c.executescript('''
                CREATE TABLE IF NOT EXISTS tasks(
                    id TEXT PRIMARY KEY,
                    dedup TEXT UNIQUE,
                    project TEXT,
                    assigned_to TEXT,
                    kind TEXT,
                    payload TEXT,
                    status TEXT,
                    created_at REAL,
                    started_at REAL,
                    completed_at REAL,
                    result TEXT,
                    lease TEXT,
                    lease_until REAL,
                    owner_node TEXT
                );
                CREATE TABLE IF NOT EXISTS activity(
                    node_id TEXT,
                    role TEXT,
                    last_seen REAL,
                    capabilities TEXT,
                    PRIMARY KEY(node_id, role)
                );
                CREATE TABLE IF NOT EXISTS staging_reviews(
                    id TEXT PRIMARY KEY,
                    task_id TEXT UNIQUE,
                    pipeline_id TEXT,
                    slug TEXT,
                    title TEXT,
                    video_path TEXT,
                    drive_url TEXT,
                    qc_score REAL,
                    qc_summary TEXT,
                    slot_hint TEXT,
                    status TEXT,
                    decision_note TEXT,
                    telegram_msg_id INTEGER,
                    created_at REAL,
                    decided_at REAL
                );
                CREATE TABLE IF NOT EXISTS lessons(
                    id TEXT PRIMARY KEY,
                    source_task_id TEXT,
                    slug TEXT,
                    category TEXT,
                    note TEXT,
                    created_at REAL
                );
            ''')
            existing_cols = {r['name'] for r in c.execute('PRAGMA table_info(tasks)').fetchall()}
            for col_name, col_type in self.EXTRA_TASK_COLUMNS.items():
                if col_name not in existing_cols:
                    c.execute(f'ALTER TABLE tasks ADD COLUMN {col_name} {col_type}')

    @contextmanager
    def db(self):
        state = self.root / 'state'
        state.mkdir(exist_ok=True)
        c = sqlite3.connect(state / 'research.sqlite3', timeout=15)
        c.row_factory = sqlite3.Row
        c.execute('PRAGMA max_page_count=65536')
        try:
            with c:
                yield c
        finally:
            c.close()

    def chief(self, node):
        if node['role'] != 'controller':
            raise QueueError(403, 'Chief only')

    def role(self, node, body, delegated):
        role = node['role']
        if role == 'controller':
            if body.get('as_role', body.get('role')) != 'engineer' or not delegated:
                raise QueueError(403, 'Chief must explicitly claim as delegated engineer')
            return 'engineer'
        return role

    def decode(self, row):
        data = dict(row)
        for k in ('payload', 'result'):
            if data.get(k):
                data[k] = json.loads(data[k])
        for k in ('depends_on', 'required_capabilities', 'preferred_capabilities'):
            if k in data:
                data[k] = _json_load_or(data.get(k), [])
        for k in ('auto_verify', 'auto_approve'):
            if k in data and data[k] is not None:
                data[k] = bool(data[k])
        return data

    def _unlock_ready_dependents(self, c, now):
        waiting = c.execute("SELECT id, depends_on FROM tasks WHERE status='WAITING_DEPS'").fetchall()
        for w in waiting:
            deps = _json_load_or(w['depends_on'], [])
            if not deps:
                c.execute("UPDATE tasks SET status='QUEUED', queued_at=? WHERE id=?", (now, w['id']))
                continue
            placeholders = ','.join('?' for _ in deps)
            rows = c.execute(
                f'SELECT id, status FROM tasks WHERE id IN ({placeholders})',
                tuple(deps),
            ).fetchall()
            if len(rows) == len(deps) and all(r['status'] == 'APPROVED' for r in rows):
                c.execute("UPDATE tasks SET status='QUEUED', queued_at=? WHERE id=?", (now, w['id']))

    def _has_active_preferred_worker(self, c, role, preferred_caps, now, exclude_node_id=None):
        rows = c.execute(
            'SELECT node_id, last_seen, capabilities FROM activity WHERE role=?',
            (role,),
        ).fetchall()
        pref = set(preferred_caps)
        for r in rows:
            if exclude_node_id and r['node_id'] == exclude_node_id:
                continue
            if r['last_seen'] is None or (now - r['last_seen']) > GPU_ACTIVE_WINDOW_S:
                continue
            node_caps = set(_json_load_or(r['capabilities'], []))
            if pref.issubset(node_caps):
                return True
        return False

    def _enqueue_staging(self, c, task_row, qc_result, status_label, now):
        payload = _json_load_or(task_row['payload'], {})
        prod_result = _json_load_or(task_row['result'], {})
        slug = prod_result.get('slug') or payload.get('slug') or task_row['id'][:8]
        title = prod_result.get('title') or payload.get('title') or slug
        video_path = prod_result.get('video_path') or prod_result.get('final_mp4') or ''
        drive_url = prod_result.get('drive_url') or ''
        slot_hint = payload.get('slot_hint') or '11:30 / 20:00'
        score = qc_result.get('score') if isinstance(qc_result, dict) else None
        summary = json.dumps(qc_result, ensure_ascii=False) if isinstance(qc_result, dict) else str(qc_result or '')
        existing = c.execute('SELECT id FROM staging_reviews WHERE task_id=?', (task_row['id'],)).fetchone()
        if existing:
            c.execute('''
                UPDATE staging_reviews
                SET video_path=?, drive_url=?, qc_score=?, qc_summary=?, status=?, created_at=?
                WHERE task_id=?
            ''', (video_path, drive_url, score, summary, status_label, now, task_row['id']))
            return existing['id']
        sid = str(uuid.uuid4())
        c.execute('''
            INSERT INTO staging_reviews(
                id, task_id, pipeline_id, slug, title, video_path, drive_url,
                qc_score, qc_summary, slot_hint, status, decision_note,
                telegram_msg_id, created_at, decided_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            sid, task_row['id'], task_row['pipeline_id'], slug, title,
            video_path, drive_url, score, summary, slot_hint,
            status_label, None, None, now, None,
        ))
        return sid

    def _insert_task(self, c, body, now):
        project = body.get('project', PROJECT)
        if project not in ALLOWED_PROJECTS:
            raise QueueError(400, 'Research or studio project only')
        role = body.get('assigned_to')
        if role not in ('research', 'verify', 'engineer'):
            raise QueueError(400, 'Invalid research role')
        dedup = body.get('dedup')
        kind = body.get('kind')
        payload = body.get('payload')
        if (
            not isinstance(dedup, str) or not 1 <= len(dedup) <= 200
            or not isinstance(kind, str) or not 1 <= len(kind) <= 80
            or not isinstance(payload, dict)
        ):
            raise QueueError(400, 'Invalid task')
        validate_payload(payload)

        depends_on = body.get('depends_on') or []
        req_caps = body.get('required_capabilities') or []
        pref_caps = body.get('preferred_capabilities') or []
        for lst in (depends_on, req_caps, pref_caps):
            if not isinstance(lst, list) or not all(isinstance(x, str) and len(x) < 100 for x in lst):
                raise QueueError(400, 'Invalid dependency or capability list')

        fallback_after = float(body.get('fallback_after_seconds', DEFAULT_FALLBACK_AFTER_S))
        auto_verify = 1 if body.get('auto_verify') else 0
        auto_approve = 1 if body.get('auto_approve') else 0
        max_retries = int(body.get('max_retries', 2))
        if max_retries < 0 or max_retries > 10:
            raise QueueError(400, 'Invalid max_retries')

        existing = c.execute('SELECT * FROM tasks WHERE dedup=?', (dedup,)).fetchone()
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        if existing:
            if (existing['assigned_to'], existing['kind'], existing['payload']) != (role, kind, encoded):
                raise QueueError(409, 'Dedup reused with different task')
            return {'id': existing['id'], 'project': existing['project'], 'status': existing['status']}

        initial_status = 'QUEUED'
        if depends_on:
            placeholders = ','.join('?' for _ in depends_on)
            dep_rows = c.execute(
                f'SELECT id, status FROM tasks WHERE id IN ({placeholders})',
                tuple(depends_on),
            ).fetchall()
            if len(dep_rows) != len(depends_on) or not all(r['status'] == 'APPROVED' for r in dep_rows):
                initial_status = 'WAITING_DEPS'

        tid = body.get('_preset_id') or str(uuid.uuid4())
        c.execute('''
            INSERT INTO tasks(
                id, dedup, project, assigned_to, kind, payload, status,
                created_at, started_at, completed_at, result, lease, lease_until, owner_node,
                parent_id, depends_on, pipeline_id, required_capabilities, preferred_capabilities,
                fallback_after_seconds, auto_verify, auto_approve, attempt, max_retries,
                target_task_id, queued_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            tid, dedup, project, role, kind, encoded, initial_status,
            now, None, None, None, None, None, None,
            body.get('parent_id'),
            json.dumps(depends_on),
            body.get('pipeline_id'),
            json.dumps(req_caps),
            json.dumps(pref_caps),
            fallback_after,
            auto_verify,
            auto_approve,
            1,
            max_retries,
            body.get('target_task_id'),
            now if initial_status == 'QUEUED' else None,
        ))
        return {'id': tid, 'project': project, 'status': initial_status}

    def get(self, node, path):
        clean = path.split('?', 1)[0]
        if clean.startswith('/tasks/'):
            tid = clean.split('/', 2)[2]
            with self.db() as c:
                row = c.execute('SELECT * FROM tasks WHERE id=?', (tid,)).fetchone()
                if not row:
                    raise QueueError(404, 'Research task not found')
                if node['role'] == 'controller':
                    return self.decode(row)
                if node['role'] == 'verify':
                    allowed = c.execute('''
                        SELECT 1 FROM tasks
                        WHERE assigned_to='verify' AND target_task_id=?
                        AND status IN ('QUEUED', 'RUNNING', 'SUBMITTED')
                    ''', (tid,)).fetchone()
                    if allowed:
                        return self.decode(row)
                raise QueueError(403, 'Chief or assigned Verify only')

        if clean == '/lessons':
            if node['role'] not in ('controller', 'research', 'verify', 'engineer'):
                raise QueueError(403, 'Authorized agent only')
            with self.db() as c:
                return [dict(r) for r in c.execute('SELECT * FROM lessons ORDER BY created_at DESC LIMIT 200')]

        self.chief(node)
        with self.db() as c:
            if clean == '/tasks':
                return [self.decode(r) for r in c.execute('SELECT * FROM tasks ORDER BY created_at DESC LIMIT 200')]
            if clean == '/agents':
                return [dict(r) for r in c.execute('SELECT * FROM activity')]
            if clean == '/staging':
                return [dict(r) for r in c.execute('SELECT * FROM staging_reviews ORDER BY created_at DESC LIMIT 100')]
        raise QueueError(404, 'Not found')

    def post(self, node, path, body, delegated=False):
        now = time.time()
        if path == '/tasks':
            self.chief(node)
            with self.db() as c:
                c.execute('BEGIN IMMEDIATE')
                res = self._insert_task(c, body, now)
            return {'id': res['id'], 'project': res['project'], 'status': res['status']}

        if path == '/pipelines':
            self.chief(node)
            steps = body.get('steps')
            if not isinstance(steps, list) or not 1 <= len(steps) <= 20:
                raise QueueError(400, 'Pipeline requires 1..20 steps')
            pipeline_id = body.get('pipeline_id') or str(uuid.uuid4())
            project = body.get('project', 'studio')
            key_to_id = {}
            created = []
            with self.db() as c:
                c.execute('BEGIN IMMEDIATE')
                for step in steps:
                    if not isinstance(step, dict) or not step.get('step_key'):
                        raise QueueError(400, 'Each step requires step_key')
                    step_key = step['step_key']
                    if step_key in key_to_id:
                        raise QueueError(400, 'Duplicate step_key')
                    preset_id = str(uuid.uuid4())
                    dep_ids = []
                    for dep_key in step.get('depends_on_steps', []):
                        if dep_key not in key_to_id:
                            raise QueueError(400, f'Unknown upstream step_key: {dep_key}')
                        dep_ids.append(key_to_id[dep_key])
                    task_spec = dict(step)
                    task_spec['project'] = step.get('project', project)
                    task_spec['pipeline_id'] = pipeline_id
                    task_spec['depends_on'] = dep_ids + list(step.get('depends_on', []))
                    task_spec['_preset_id'] = preset_id
                    out = self._insert_task(c, task_spec, now)
                    key_to_id[step_key] = out['id']
                    created.append({'step_key': step_key, **out})
            return {'pipeline_id': pipeline_id, 'project': project, 'steps': created}

        if path == '/lessons':
            if node['role'] not in ('controller', 'verify'):
                raise QueueError(403, 'Chief or Verify only')
            note = (body.get('note') or '').strip()
            if not note or len(note) > 4000:
                raise QueueError(400, 'Lesson note required')
            validate_payload(note)
            lid = str(uuid.uuid4())
            with self.db() as c:
                c.execute(
                    'INSERT INTO lessons VALUES(?,?,?,?,?,?)',
                    (lid, body.get('source_task_id'), body.get('slug', ''), body.get('category', 'general'), note, now),
                )
            return {'id': lid, 'status': 'recorded'}

        if path.startswith('/staging/') and path.endswith('/decision'):
            self.chief(node)
            parts = path.strip('/').split('/')
            if len(parts) != 3:
                raise QueueError(404, 'Not found')
            sid = parts[1]
            decision = body.get('decision')
            note = (body.get('note') or '').strip()
            tg_msg_id = body.get('telegram_msg_id')
            valid_decisions = ('approve_1130', 'approve_2000', 'approve_publish', 'rerender', 'reject', 'mark_notified')
            if decision not in valid_decisions:
                raise QueueError(400, 'Invalid staging decision')
            with self.db() as c:
                c.execute('BEGIN IMMEDIATE')
                srow = c.execute('SELECT * FROM staging_reviews WHERE id=? OR task_id=?', (sid, sid)).fetchone()
                if not srow:
                    raise QueueError(404, 'Staging item not found')
                if decision == 'mark_notified':
                    c.execute('UPDATE staging_reviews SET telegram_msg_id=? WHERE id=?', (tg_msg_id, srow['id']))
                    return {'id': srow['id'], 'status': srow['status'], 'telegram_msg_id': tg_msg_id}
                status_map = {
                    'approve_1130': 'APPROVED_SLOT_1130',
                    'approve_2000': 'APPROVED_SLOT_2000',
                    'approve_publish': 'APPROVED_PUBLISH',
                    'rerender': 'RERENDER_REQUESTED',
                    'reject': 'REJECTED',
                }
                new_status = status_map[decision]
                c.execute(
                    'UPDATE staging_reviews SET status=?, decision_note=?, decided_at=? WHERE id=?',
                    (new_status, note, now, srow['id']),
                )
                if note and decision in ('reject', 'rerender'):
                    c.execute(
                        'INSERT INTO lessons VALUES(?,?,?,?,?,?)',
                        (str(uuid.uuid4()), srow['task_id'], srow['slug'], f'human_{decision}', note, now),
                    )
                if decision == 'rerender':
                    trow = c.execute('SELECT * FROM tasks WHERE id=?', (srow['task_id'],)).fetchone()
                    if trow:
                        tpay = _json_load_or(trow['payload'], {})
                        tpay['last_qc_feedback'] = {'source': 'human_telegram', 'note': note or 'Owner requested re-render'}
                        c.execute('''
                            UPDATE tasks
                            SET status='QUEUED', queued_at=?, payload=?, result=NULL,
                                lease=NULL, lease_until=NULL, owner_node=NULL, attempt=attempt+1
                            WHERE id=?
                        ''', (now, json.dumps(tpay, ensure_ascii=False, sort_keys=True), trow['id']))
                return {'id': srow['id'], 'status': new_status}

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
                    "UPDATE tasks SET status='QUEUED', queued_at=?, lease=NULL, lease_until=NULL, owner_node=NULL "
                    "WHERE status='RUNNING' AND lease_until<?",
                    (now, now),
                )
                self._unlock_ready_dependents(c, now)
                row = c.execute(
                    "SELECT * FROM tasks WHERE assigned_to=? AND status='RUNNING' AND owner_node=? LIMIT 1",
                    (role, node['id']),
                ).fetchone()
                if not row:
                    candidates = c.execute(
                        "SELECT * FROM tasks WHERE assigned_to=? AND status='QUEUED' ORDER BY created_at",
                        (role,),
                    ).fetchall()
                    chosen = None
                    for cand in candidates:
                        req_caps = set(_json_load_or(cand['required_capabilities'], []))
                        if not req_caps.issubset(cap_set):
                            continue
                        pref_caps = _json_load_or(cand['preferred_capabilities'], [])
                        if pref_caps and not set(pref_caps).issubset(cap_set):
                            waited = now - (cand['queued_at'] or cand['created_at'] or now)
                            fallback_s = cand['fallback_after_seconds']
                            if fallback_s is None:
                                fallback_s = DEFAULT_FALLBACK_AFTER_S
                            if waited < fallback_s and self._has_active_preferred_worker(
                                c, role, pref_caps, now, exclude_node_id=node['id']
                            ):
                                continue
                        chosen = cand
                        break
                    if not chosen:
                        return {'id': None, 'project': PROJECT}
                    c.execute(
                        "UPDATE tasks SET status='RUNNING', started_at=COALESCE(started_at,?), "
                        "lease=?, lease_until=?, owner_node=? WHERE id=?",
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
                self._unlock_ready_dependents(c, now)
                return {'status': 'APPROVED', 'project': row['project']}

            role = self.role(node, body, delegated)
            if row['assigned_to'] != role or row['owner_node'] != node['id'] or row['lease'] != body.get('lease'):
                raise QueueError(403, 'Wrong role, node or lease')
            if action == 'heartbeat':
                if row['status'] != 'RUNNING' or row['lease_until'] < now:
                    raise QueueError(409, 'Lease expired or finished')
                c.execute('UPDATE tasks SET lease_until=? WHERE id=?', (now + 900, tid))
                return {'status': 'ok', 'project': row['project']}

            result = body.get('result')
            if not isinstance(result, dict):
                raise QueueError(400, 'Result object required')
            if row['project'] == 'studio' and result.get('outcome') == 'completed':
                result = dict(result, outcome='ok')
            validate_payload(result)
            data = json.dumps(result, sort_keys=True, ensure_ascii=False)
            if len(data.encode()) > 256000:
                raise QueueError(413, 'Use media links')
            if row['status'] in ('SUBMITTED', 'APPROVED'):
                if row['result'] != data:
                    raise QueueError(409, 'Different result already received')
                return {'status': row['status'], 'received': True, 'project': row['project']}
            if row['status'] != 'RUNNING' or row['lease_until'] < now:
                raise QueueError(409, 'Lease expired')

            c.execute("UPDATE tasks SET status='SUBMITTED', result=?, completed_at=? WHERE id=?", (data, now, tid))
            final_status = 'SUBMITTED'
            spawned_verify_id = None

            # Auto-spawn Verify task when worker finishes a task flagged with auto_verify
            if row['auto_verify'] and role != 'verify' and result.get('outcome') in ('ok', 'PASS'):
                src_payload = _json_load_or(row['payload'], {})
                v_out = self._insert_task(c, {
                    'project': row['project'],
                    'assigned_to': 'verify',
                    'kind': f"verify_{row['kind']}"[:80],
                    'dedup': f"auto-verify:{tid}:attempt-{row['attempt'] or 1}",
                    'parent_id': tid,
                    'pipeline_id': row['pipeline_id'],
                    'target_task_id': tid,
                    'auto_approve': bool(row['auto_approve']),
                    'payload': {
                        'objective': f"Automated QC verification for {row['kind']} ({tid})",
                        'target_task_id': tid,
                        'acceptance_criteria': src_payload.get('acceptance_criteria', {'min_score': 85}),
                    },
                }, now)
                spawned_verify_id = v_out['id']

            # Handle closed-loop Verify verdict against target_task_id
            if role == 'verify' and row['target_task_id']:
                target = c.execute('SELECT * FROM tasks WHERE id=?', (row['target_task_id'],)).fetchone()
                if target:
                    t_payload = _json_load_or(target['payload'], {})
                    criteria = t_payload.get('acceptance_criteria') or {}
                    min_score = float(criteria.get('min_score', 85)) if isinstance(criteria, dict) else 85.0
                    verdict = result.get('outcome')
                    score = float(result.get('score', 100.0))
                    hard_ok = bool(result.get('hard_gate_passed', True))

                    if verdict in ('PASS', 'ok') and hard_ok and score >= min_score:
                        if row['auto_approve'] or target['auto_approve']:
                            c.execute("UPDATE tasks SET status='APPROVED' WHERE id IN (?, ?)", (tid, target['id']))
                            final_status = 'APPROVED'
                            self._unlock_ready_dependents(c, now)
                            refreshed_target = c.execute('SELECT * FROM tasks WHERE id=?', (target['id'],)).fetchone()
                            if (
                                t_payload.get('stage') == 'staging_ready'
                                or target['kind'] in ('episode_produce', 'episode_compile')
                            ):
                                self._enqueue_staging(c, refreshed_target, result, 'PENDING_HUMAN', now)
                    elif verdict in ('RETRYABLE_FAIL', 'FAIL'):
                        attempt = int(target['attempt'] or 1)
                        max_ret = int(target['max_retries'] if target['max_retries'] is not None else 2)
                        if attempt < max_ret:
                            t_payload['last_qc_feedback'] = {
                                'attempt': attempt,
                                'score': score,
                                'reasons': result.get('reasons', []),
                                'failed_beats': result.get('failed_beats', []),
                            }
                            c.execute('''
                                UPDATE tasks
                                SET status='QUEUED', queued_at=?, payload=?, result=NULL,
                                    lease=NULL, lease_until=NULL, owner_node=NULL, attempt=?
                                WHERE id=?
                            ''', (now, json.dumps(t_payload, ensure_ascii=False, sort_keys=True), attempt + 1, target['id']))
                        else:
                            c.execute("UPDATE tasks SET status='ESCALATED' WHERE id=?", (target['id'],))
                            refreshed_target = c.execute('SELECT * FROM tasks WHERE id=?', (target['id'],)).fetchone()
                            self._enqueue_staging(c, refreshed_target, result, 'ESCALATED', now)

            resp = {'status': final_status, 'received': True, 'project': row['project']}
            if spawned_verify_id:
                resp['auto_verify_task_id'] = spawned_verify_id
            return resp
