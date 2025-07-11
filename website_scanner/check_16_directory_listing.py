import requests
import json
import os
from bs4 import BeautifulSoup

def run(url, resp=None):
    '''Detect directory listing'''
    # Try to fetch the URL if not provided
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Detect directory listing',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1
            }
    indicators = [
        'Index of /',
        '<title>Index of',
        'Parent Directory',
        'Directory listing for',
        'To Parent Directory'
    ]
    found = False
    evidence = []
    if resp is not None:
        soup = BeautifulSoup(resp.text, 'html.parser')
        page_text = soup.get_text() + resp.text
        for indicator in indicators:
            if indicator in page_text:
                found = True
                evidence.append(indicator)
    status = 'fail' if found else 'pass'
    risk = 3 if found else 1
    
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_16_directory_listing', '')
    except:
        pass
        
    return {
        'name': 'Detect directory listing',
        'status': status,
        'description': 'Detects if directory listing is enabled',
        'evidence': evidence if found else None,
        'risk': risk,
        'guide': guide
    }
