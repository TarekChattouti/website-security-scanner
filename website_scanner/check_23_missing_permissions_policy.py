import json
import os

def run(url, resp=None):
    '''Missing HTTP header - Feature/Permissions-Policy'''
    permissions_policy = resp.headers.get('Permissions-Policy') if resp else None
    feature_policy = resp.headers.get('Feature-Policy') if resp else None
    status = 'pass' if permissions_policy or feature_policy else 'fail'
    # Risk: 2 (Low) if both missing, 1 (Info) if either present
    risk = 2 if status == 'fail' else 1
    
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_23_missing_permissions_policy', '')
    except:
        pass
        
    return {
        'name': 'Missing HTTP header - Feature/Permissions-Policy',
        'status': status,
        'description': 'Checks for Permissions-Policy or Feature-Policy header',
        'evidence': {
            'Permissions-Policy': permissions_policy,
            'Feature-Policy': feature_policy
        },
        'risk': risk,
        'guide': guide
    }
