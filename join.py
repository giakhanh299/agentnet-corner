"""Run on each new node. Persists a node-specific enrollment secret outside prompts."""
import argparse, json, os, secrets
from pathlib import Path
from urllib.request import Request, urlopen

parser=argparse.ArgumentParser()
parser.add_argument('role',choices=['controller','research','verify','engineer'])
parser.add_argument('--master',required=True,help='Tailscale origin including registry port')
parser.add_argument('--state',default=str(Path.home()/'.agentnet-corner'))
args=parser.parse_args()
from urllib.parse import urlsplit
import ipaddress
origin=urlsplit(args.master)
if origin.scheme!='http' or not origin.hostname or origin.username or origin.password or origin.query or origin.fragment or origin.path not in ('','/'):
    raise SystemExit('Expected explicit Tailscale HTTP origin')
if ipaddress.ip_address(origin.hostname) not in ipaddress.ip_network('100.64.0.0/10'):
    raise SystemExit('Only Tailscale IPv4 accepted')
state=Path(args.state);state.mkdir(parents=True,exist_ok=True)
os.chmod(state,0o700)
identity=state/'identity.json'
if not identity.exists():
    fd=os.open(identity,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump({'role':args.role,'token':secrets.token_urlsafe(40)},f)
data=json.loads(identity.read_text())
if data['role']!=args.role:raise SystemExit('Role change requires a separately approved identity')
req=Request(args.master.rstrip('/')+'/enroll',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
with urlopen(req,timeout=15) as r:result=json.load(r)
print(json.dumps(result))
if result['status']=='APPROVED':
    req=Request(args.master.rstrip('/')+'/controller',headers={
        'Authorization':'Bearer '+data['token'],'X-AgentNet-Client':'join/2'})
    with urlopen(req,timeout=15) as r:connection=json.load(r)
    if connection.get('project') not in ('research','studio') or connection.get('mode') not in ('research-only','studio-auto99'):
        raise SystemExit('Refusing a non-research connection; existing identity kept unchanged')
    fd=os.open(state/'connection.json',os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w') as f:json.dump(connection,f)
    safe={k:v for k,v in connection.items() if k not in ('application_token','additional_roles')}
    print(json.dumps(safe))
