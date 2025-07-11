
from urllib.parse import urlparse, parse_qs
import os
import json


def run(url, resp=None):
    '''Detect passwords in URL query string'''
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    password_keys = ['password', 'passwd', 'pwd', 'pass', 'secret', 'token']
    found = {}
    for key in query:
        if any(pw in key.lower() for pw in password_keys):
            found[key] = query[key]
    status = 'fail' if found else 'pass'
    risk = 4 if found else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_24_password_in_url', '')
    except Exception:
        guide = ''
    return {
        'name': 'Detect passwords in URL query string',
        'status': status,
        'description': 'Detects password values in URL',
        'evidence': found if found else None,
        'risk': risk,
        'guide': guide
    }
