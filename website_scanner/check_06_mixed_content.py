import json
import os
from bs4 import BeautifulSoup

def run(url, resp=None):
    mixed = []
    if resp and url.startswith('https://'):
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup.find_all(['img', 'script', 'iframe', 'link', 'video', 'audio', 'source']):
            src = tag.get('src') or tag.get('href')
            if src and src.startswith('http://'):
                mixed.append(src)
    status = 'fail' if mixed else 'pass'
    # Risk: 3 (Medium) for mixed content, 1 (Info) if none
    risk = 3 if mixed else 1
    
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_06_mixed_content', '')
    except:
        pass
    
    return {
        'name': 'Detect mixed content (HTTP inside HTTPS)',
        'status': status,
        'description': 'Detects HTTP resources loaded in HTTPS pages',
        'evidence': mixed,
        'risk': risk,
        'guide': guide
    }
