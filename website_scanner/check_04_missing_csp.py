import requests
import json
import os


def run(url, resp=None):
    val = resp.headers.get('Content-Security-Policy') if resp else None
    # Check for .well-known/security.txt
    sec_url = url.rstrip('/') + '/.well-known/security.txt'
    try:
        sec_resp = requests.get(sec_url, timeout=5)
        sec_present = sec_resp.status_code == 200
    except Exception:
        sec_present = False
    status = 'fail' if not val or not sec_present else 'pass'
    # Risk: 4 (High) if missing CSP, 2 (Low) if only security.txt missing, 1 if both present
    if not val and not sec_present:
        risk = 4
    elif not val or not sec_present:
        risk = 2
    else:
        risk = 1
        
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_04_missing_csp', '')
    except:
        pass
        
    return {
        'name': 'Missing HTTP header - Content-Security-Policy and Security.txt',
        'status': status,
        'description': 'Checks for Content-Security-Policy header and .well-known/security.txt file',
        'evidence': {
            'Content-Security-Policy': val,
            'security.txt_present': sec_present
        },
        'risk': risk,
        'guide': guide
    }
