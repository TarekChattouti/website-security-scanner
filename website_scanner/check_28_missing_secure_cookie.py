import os
import json

def run(url, resp=None):
    '''Missing Secure flag on cookie'''
    cookies = resp.cookies if resp else []
    missing_secure = []
    for cookie in cookies:
        # The 'secure' attribute is True if the Secure flag is set
        if not getattr(cookie, 'secure', False):
            missing_secure.append({'name': cookie.name, 'domain': getattr(cookie, 'domain', None)})
    status = 'fail' if missing_secure else 'pass'
    # Risk: 3 (Medium) if missing Secure flag, 1 (Info) if not
    risk = 3 if missing_secure else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_28_missing_secure_cookie', '')
    except Exception:
        guide = ''
    return {
        'name': 'Missing Secure flag on cookie',
        'status': status,
        'description': 'Checks if cookies have Secure flag',
        'evidence': missing_secure if missing_secure else None,
        'risk': risk,
        'guide': guide
    }
