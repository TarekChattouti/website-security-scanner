import json
import os

def run(url, resp=None):
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_01_start_scan', '')
    except:
        pass
        
    return {
        'name': 'Start scan',
        'status': 'pass',
        'description': 'Scan started',
        'evidence': url,
        'risk': 1,  # Info only
        'guide': guide
    }
