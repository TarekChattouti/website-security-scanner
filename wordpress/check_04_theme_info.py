import requests
import json
import os
import re

def run(url, resp=None):
    '''Search information for main theme (e.g., dooplay)'''
    try:
        r = requests.get(url, timeout=10)
        m = re.search(r'/wp-content/themes/([\w-]+)/', r.text)
        theme = m.group(1) if m else None
        
        # Load guide from help.json
        help_file = os.path.join(os.path.dirname(__file__), 'help.json')
        guide = ""
        try:
            with open(help_file, 'r') as f:
                help_data = json.load(f)
                guide = help_data.get('check_04_theme_info', '')
        except:
            pass
            
        return {
            'name': 'Search information for main theme',
            'status': 'pass' if theme else 'fail',
            'description': 'Detects the main WordPress theme in use',
            'evidence': {'theme': theme},
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
                guide = help_data.get('check_04_theme_info', '')
        except:
            pass
            
        return {
            'name': 'Search information for main theme',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1,
            'guide': guide
        }
