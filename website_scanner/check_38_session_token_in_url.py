
from urllib.parse import urlparse, parse_qs
import os
import json


def run(url, resp=None):
    '''Session token in URL'''
    session_keys = ['session', 'sid', 'sessid', 'token', 'auth', 'jwt', 'jsessionid', 'phpsessid']
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    found = {}
    for key in query:
        if any(sk in key.lower() for sk in session_keys):
            found[key] = query[key]
    # Also check for session tokens in the fragment (after #)
    fragment = parse_qs(parsed.fragment)
    for key in fragment:
        if any(sk in key.lower() for sk in session_keys):
            found[f'fragment:{key}'] = fragment[key]
    status = 'fail' if found else 'pass'
    # Risk: 4 (High) if session token in URL, 1 (Info) if not
    risk = 4 if found else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_38_session_token_in_url', '')
    except Exception:
        guide = ''
    return {
        'name': 'Session token in URL',
        'status': status,
        'description': 'Detects session tokens in URL query or fragment',
        'evidence': found if found else None,
        'risk': risk,
        'guide': guide
    }
