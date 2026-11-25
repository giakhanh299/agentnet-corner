"""Run on each node. Persists a node-specific enrollment secret outside prompts.
Automatically handles both direct Tailscale interfaces and Muse sandbox :3130 tailnet tunnels.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import secrets
from urllib.error import URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import ProxyHandler, Request, build_opener

ROLES = [
    'controller', 'research', 'verify', 'engineer',
    'lead_research', 'lead_verify', 'lead_creative', 'lead_engineer',
]

parser = argparse.ArgumentParser()
parser.add_argument('role', choices=ROLES)
parser.add_argument('--master', required=True, help='Tailscale origin including registry port')
parser.add_argument('--state', default=str(Path.home() / '.agentnet-corner'))
parser.add_argument('--fleet-key', default=os.environ.get('AGENTNET_FLEET_KEY', ''), help='Optional fleet passcode for instant worker approval')
parser.add_argument('--proxy', default=os.environ.get('AGENTNET_PROXY', ''), help='Optional explicit HTTP proxy URL for tailnet tunnel')
args = parser.parse_args()

origin = urlsplit(args.master)
if origin.scheme != 'http' or not origin.hostname or origin.username or origin.password or origin.query or origin.fragment or origin.path not in ('', '/'):
    raise SystemExit('Expected explicit Tailscale HTTP origin')
if ipaddress.ip_address(origin.hostname) not in ipaddress.ip_network('100.64.0.0/10'):
    raise SystemExit('Only Tailscale IPv4 accepted')


def derive_tunnel_proxy():
    for env_name in ('HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy'):
        raw = os.environ.get(env_name, '').strip()
        if not raw:
            continue
        p = urlsplit(raw)
        if p.port == 3128 and p.hostname:
            auth = ''
            if p.username:
                auth = p.username + (':' + p.password if p.password else '') + '@'
            netloc = f'{auth}{p.hostname}:3130'
            return urlunsplit((p.scheme or 'http', netloc, '', '', ''))
    return ''


def candidate_openers():
    if args.proxy:
        return [('explicit_proxy', build_opener(ProxyHandler({'http': args.proxy, 'https': args.proxy})))]
    items = [('direct_tailnet', build_opener(ProxyHandler({})))]
    tunnel = derive_tunnel_proxy()
    if tunnel:
        items.append(('muse_tunnel_3130', build_opener(ProxyHandler({'http': tunnel, 'https': tunnel}))))
    return items


OPENERS = candidate_openers()


def fetch_json(url, data=None, headers=None):
    last_err = None
    for mode_name, opener in OPENERS:
        req = Request(url, data=data, headers=headers or {})
        try:
            with opener.open(req, timeout=8 if len(OPENERS) > 1 and mode_name == 'direct_tailnet' else 15) as r:
                return json.load(r), mode_name
        except URLError as exc:
            last_err = exc
            continue
    raise last_err


state = Path(args.state)
state.mkdir(parents=True, exist_ok=True)
try:
    os.chmod(state, 0o700)
except OSError:
    pass

identity = state / 'identity.json'
if not identity.exists():
    fd = os.open(identity, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump({'role': args.role, 'token': secrets.token_urlsafe(40)}, f)

data = json.loads(identity.read_text())
if data['role'] != args.role:
    raise SystemExit('Role change requires a separately approved identity (use a separate --state dir if running multiple roles)')

enroll_body = {'role': data['role'], 'token': data['token']}
if args.fleet_key:
    enroll_body['fleet_key'] = args.fleet_key

result, transport_mode = fetch_json(
    args.master.rstrip('/') + '/enroll',
    data=json.dumps(enroll_body).encode(),
    headers={'Content-Type': 'application/json'},
)
print(json.dumps({**result, 'transport': transport_mode}))

if result['status'] == 'APPROVED':
    connection, _ = fetch_json(
        args.master.rstrip('/') + '/controller',
        headers={'Authorization': 'Bearer ' + data['token'], 'X-AgentNet-Client': 'join/2'},
    )
    if connection.get('project') != 'research' or connection.get('mode') != 'research-only':
        raise SystemExit('Refusing a non-research connection; existing identity kept unchanged')
    connection['transport_mode'] = transport_mode
    fd = os.open(state / 'connection.json', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(connection, f)
    safe = {k: v for k, v in connection.items() if k not in ('application_token', 'additional_roles')}
    print(json.dumps(safe))
