import os
import json

def run(url, resp=None):
    '''Missing HTTP header - Strict-Transport-Security'''
    hsts = resp.headers.get('Strict-Transport-Security') if resp else None
    status = 'pass' if hsts else 'fail'
    # Risk: 3 (Medium) if missing, 1 (Info) if present
    risk = 3 if status == 'fail' else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_21_missing_hsts', '')
    except Exception:
        guide = ''
    return {
        'name': 'Missing HTTP header - Strict-Transport-Security',
        'status': status,
        'description': 'Checks for HSTS header',
        'evidence': hsts,
        'risk': risk,
        'guide': guide
    }
