import requests
import json
import os


def run(url, resp=None):
    '''Check if HTTP TRACE/DEBUG methods are enabled'''
    results = {}
    for method in ['TRACE', 'DEBUG']:
        try:
            r = requests.request(method, url, timeout=7)
            if r.status_code == 200:
                results[method] = 'enabled'
            elif r.status_code in (405, 501):
                results[method] = 'not allowed'
            else:
                results[method] = f'HTTP {r.status_code}'
        except Exception as e:
            results[method] = f'Error: {e}'
    status = 'fail' if results.get('TRACE') == 'enabled' or results.get('DEBUG') == 'enabled' else 'pass'
    # Risk: 4 (High) if enabled, 1 if not
    risk = 4 if status == 'fail' else 1
    
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_13_trace_debug', '')
    except:
        pass
        
    return {
        'name': 'Check if HTTP TRACE/DEBUG methods are enabled',
        'status': status,
        'description': 'Checks for TRACE/DEBUG HTTP methods',
        'evidence': results,
        'risk': risk,
        'guide': guide
    }
