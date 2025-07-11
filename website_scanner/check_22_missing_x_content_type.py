import os
import json

def run(url, resp=None):
    '''Missing HTTP header - X-Content-Type-Options'''
    x_content_type = resp.headers.get('X-Content-Type-Options') if resp else None
    status = 'pass' if x_content_type else 'fail'
    # Risk: 2 (Low) if missing, 1 (Info) if present
    risk = 2 if status == 'fail' else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_22_missing_x_content_type', '')
    except Exception:
        guide = ''
    return {
        'name': 'Missing HTTP header - X-Content-Type-Options',
        'status': status,
        'description': 'Checks for X-Content-Type-Options header',
        'evidence': x_content_type,
        'risk': risk,
        'guide': guide
    }
