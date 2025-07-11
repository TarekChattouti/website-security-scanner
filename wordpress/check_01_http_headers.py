import json
import os

def run(url, resp=None):
    '''Check for valuable information in HTTP headers'''
    headers = resp.headers if resp else {}
    info = {k: v for k, v in headers.items() if k.lower() in ['server', 'x-powered-by', 'set-cookie', 'x-frame-options', 'x-content-type-options', 'x-xss-protection']}
    
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_01_http_headers', '')
    except:
        pass
        
    return {
        'name': 'Check for valuable information in HTTP headers',
        'status': 'pass' if info else 'info',
        'description': 'Checks for potentially valuable information in HTTP headers',
        'evidence': info,
        'risk': 2 if info else 1,
        'guide': guide
    }
