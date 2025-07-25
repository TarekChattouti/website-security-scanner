import requests
import json
import os

def run(url, resp=None):
    '''Check if OPTIONS method is enabled'''
    try:
        r = requests.options(url, timeout=7)
        allow = r.headers.get('Allow', '')
        status = 'fail' if r.status_code == 200 and allow else 'pass'
        evidence = {'status_code': r.status_code, 'allow_header': allow}
        risk = 2 if status == 'fail' else 1
    except Exception as e:
        status = 'error'
        evidence = str(e)
        risk = 1
        
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_14_options_method', '')
    except:
        pass
        
    return {
        'name': 'Check if OPTIONS method is enabled',
        'status': status,
        'description': 'Checks for OPTIONS HTTP method and reports Allow header',
        'evidence': evidence,
        'risk': risk,
        'guide': guide
    }
