import requests
import re

def run(url, resp=None):
    '''Search information for main theme (e.g., dooplay)'''
    try:
        r = requests.get(url, timeout=10)
        m = re.search(r'/wp-content/themes/([\w-]+)/', r.text)
        theme = m.group(1) if m else None
        return {
            'name': 'Search information for main theme',
            'status': 'pass' if theme else 'fail',
            'description': 'Detects the main WordPress theme in use',
            'evidence': {'theme': theme},
            'risk': 1
        }
    except Exception as e:
        return {
            'name': 'Search information for main theme',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1
        }
