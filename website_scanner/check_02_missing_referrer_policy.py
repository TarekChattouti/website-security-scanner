import json
import os

def run(url, resp=None):
    val = resp.headers.get('Referrer-Policy') if resp else None
    status = 'fail' if not val else 'pass'
    # Risk: 2 (Low) if missing, 1 (Info) if present
    risk = 2 if status == 'fail' else 1
    
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_02_missing_referrer_policy', '')
    except:
        pass
        
    return {
        'name': 'Missing HTTP header - Referrer-Policy',
        'status': status,
        'description': 'Checks for Referrer-Policy header',
        'evidence': val,
        'risk': risk,
        'guide': guide
    }
