"""Independent research queue. No Facebook adapters, fetching, or periodic jobs."""
from contextlib import contextmanager
import json, sqlite3, time, uuid
from urllib.parse import urlsplit

PROJECT='research'

class QueueError(Exception):
    def __init__(self, code, message): self.code,self.message=code,message

def validate_payload(value):
    if isinstance(value,dict):
        for item in value.values():validate_payload(item)
    elif isinstance(value,list):
        for item in value:validate_payload(item)
    elif isinstance(value,str):
        for part in value.split():
            if part.startswith(('http://','https://')):
                try: url=urlsplit(part.rstrip('.,)'));port=url.port
                except ValueError: raise QueueError(400,'Invalid source URL')
                if url.hostname=='100.67.236.124' and port in (8000,8101):
                    raise QueueError(400,'Facebook project endpoints are not research sources')
                if any(s in url.path for s in ['/monetization-advisor','/video-audit','/submit-monetization-advice','/submit-audit-advice']):
                    raise QueueError(400,'Facebook audit integration is disabled in this project')

class ResearchQueue:
    def __init__(self,root):
        self.root=root
        with self.db() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS tasks(
                id TEXT PRIMARY KEY,dedup TEXT UNIQUE,project TEXT,assigned_to TEXT,
                kind TEXT,payload TEXT,status TEXT,created_at REAL,started_at REAL,
                completed_at REAL,result TEXT,lease TEXT,lease_until REAL,owner_node TEXT);
                CREATE TABLE IF NOT EXISTS activity(node_id TEXT,role TEXT,last_seen REAL,
                capabilities TEXT,PRIMARY KEY(node_id,role));''')
    @contextmanager
    def db(self):
        state=self.root/'state';state.mkdir(exist_ok=True)
        c=sqlite3.connect(state/'research.sqlite3',timeout=15);c.row_factory=sqlite3.Row
        c.execute('PRAGMA max_page_count=65536')
        try:
            with c:yield c
        finally:c.close()
    def chief(self,node):
        if node['role']!='controller':raise QueueError(403,'Chief only')
    def role(self,node,body,delegated):
        role=node['role']
        if role=='controller':
            if body.get('as_role',body.get('role'))!='engineer' or not delegated:
                raise QueueError(403,'Chief must explicitly claim as delegated engineer')
            return 'engineer'
        return role
    def decode(self,row):
        data=dict(row)
        for k in ['payload','result']:
            if data[k]:data[k]=json.loads(data[k])
        return data
    def get(self,node,path):
        self.chief(node)
        with self.db() as c:
            if path=='/tasks':return [self.decode(r) for r in c.execute('SELECT * FROM tasks ORDER BY created_at DESC LIMIT 200')]
            if path=='/agents':return [dict(r) for r in c.execute('SELECT * FROM activity')]
        raise QueueError(404,'Not found')
    def post(self,node,path,body,delegated=False):
        now=time.time()
        if path=='/tasks':
            self.chief(node)
            if body.get('project',PROJECT)!=PROJECT:raise QueueError(400,'Research project only')
            role=body.get('assigned_to')
            if role not in ('research','verify','engineer'):raise QueueError(400,'Invalid research role')
            dedup=body.get('dedup');kind=body.get('kind');payload=body.get('payload')
            if not isinstance(dedup,str) or not 1<=len(dedup)<=200 or not isinstance(kind,str) or not 1<=len(kind)<=80 or not isinstance(payload,dict):raise QueueError(400,'Invalid task')
            validate_payload(payload)
            with self.db() as c:
                c.execute('BEGIN IMMEDIATE')
                existing=c.execute('SELECT * FROM tasks WHERE dedup=?',(dedup,)).fetchone()
                encoded=json.dumps(payload,ensure_ascii=False,sort_keys=True)
                if existing:
                    if (existing['assigned_to'],existing['kind'],existing['payload'])!=(role,kind,encoded):raise QueueError(409,'Dedup reused with different task')
                    return {'id':existing['id'],'project':PROJECT}
                tid=str(uuid.uuid4())
                c.execute('INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (tid,dedup,PROJECT,role,kind,encoded,'QUEUED',now,None,None,None,None,None,None))
            return {'id':tid,'project':PROJECT}
        if path=='/claim':
            role=self.role(node,body,delegated)
            caps=body.get('capabilities',[])
            if not isinstance(caps,list) or len(caps)>32 or not all(isinstance(v,str) and len(v)<100 for v in caps):raise QueueError(400,'Invalid capabilities')
            with self.db() as c:
                c.execute('BEGIN IMMEDIATE')
                c.execute('INSERT OR REPLACE INTO activity VALUES(?,?,?,?)',(node['id'],role,now,json.dumps(caps)))
                c.execute("UPDATE tasks SET status='QUEUED',lease=NULL,lease_until=NULL,owner_node=NULL WHERE status='RUNNING' AND lease_until<?",(now,))
                row=c.execute("SELECT * FROM tasks WHERE assigned_to=? AND status='RUNNING' AND owner_node=? LIMIT 1",(role,node['id'])).fetchone()
                if not row:
                    row=c.execute("SELECT * FROM tasks WHERE assigned_to=? AND status='QUEUED' ORDER BY created_at LIMIT 1",(role,)).fetchone()
                    if not row:return {'id':None,'project':PROJECT}
                    c.execute("UPDATE tasks SET status='RUNNING',started_at=COALESCE(started_at,?),lease=?,lease_until=?,owner_node=? WHERE id=?",(now,str(uuid.uuid4()),now+900,node['id'],row['id']))
                    row=c.execute('SELECT * FROM tasks WHERE id=?',(row['id'],)).fetchone()
                return self.decode(row)
        parts=path.strip('/').split('/')
        if len(parts)!=3 or parts[0]!='tasks' or parts[2] not in ('heartbeat','result','approve'):raise QueueError(404,'Not found')
        tid,action=parts[1:]
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT * FROM tasks WHERE id=?',(tid,)).fetchone()
            if not row:raise QueueError(404,'Research task not found')
            if action=='approve':
                self.chief(node)
                if row['status'] not in ('SUBMITTED','APPROVED'):raise QueueError(409,'No submitted result')
                result=json.loads(row['result'])
                if result.get('outcome') not in ('ok','PASS'):raise QueueError(409,'Cannot approve a blocked or failed result')
                c.execute("UPDATE tasks SET status='APPROVED' WHERE id=?",(tid,))
                return {'status':'APPROVED','project':PROJECT}
            role=self.role(node,body,delegated)
            if row['assigned_to']!=role or row['owner_node']!=node['id'] or row['lease']!=body.get('lease'):raise QueueError(403,'Wrong role, node or lease')
            if action=='heartbeat':
                if row['status']!='RUNNING' or row['lease_until']<now:raise QueueError(409,'Lease expired or finished')
                c.execute('UPDATE tasks SET lease_until=? WHERE id=?',(now+900,tid))
                return {'status':'ok','project':PROJECT}
            result=body.get('result')
            if not isinstance(result,dict):raise QueueError(400,'Result object required')
            validate_payload(result)
            data=json.dumps(result,sort_keys=True,ensure_ascii=False)
            if len(data.encode())>256000:raise QueueError(413,'Use media links')
            if row['status'] in ('SUBMITTED','APPROVED'):
                if row['result']!=data:raise QueueError(409,'Different result already received')
                return {'status':row['status'],'received':True,'project':PROJECT}
            if row['status']!='RUNNING' or row['lease_until']<now:raise QueueError(409,'Lease expired')
            c.execute("UPDATE tasks SET status='SUBMITTED',result=?,completed_at=? WHERE id=?",(data,now,tid))
            return {'status':'SUBMITTED','received':True,'project':PROJECT}
