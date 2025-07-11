import requests
import json
import os

def run(url, resp=None):
    '''Check for robots.txt file'''
    robots_url = url.rstrip('/') + '/robots.txt'
    try:
        r = requests.get(robots_url, timeout=5)
        found = r.status_code == 200
        
        # Load guide from help.json
        help_file = os.path.join(os.path.dirname(__file__), 'help.json')
        guide = ""
        try:
            with open(help_file, 'r') as f:
                help_data = json.load(f)
                guide = help_data.get('check_03_robots_txt', '')
        except:
            pass
            
        return {
            'name': 'Check for robots.txt file',
            'status': 'pass' if found else 'fail',
            'description': 'Checks if robots.txt file is present',
            'evidence': {'url': robots_url, 'status_code': r.status_code, 'content': r.text[:200]},
            'risk': 1,
            'guide': guide
        }
    except Exception as e:
        # Load guide from help.json
        help_file = os.path.join(os.path.dirname(__file__), 'help.json')
        guide = ""
        try:
            with open(help_file, 'r') as f:
                help_data = json.load(f)
                guide = help_data.get('check_03_robots_txt', '')
        except:
            pass
            
        return {
            'name': 'Check for robots.txt file',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1,
            'guide': guide
        }
