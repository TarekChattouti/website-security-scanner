
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import os
import json

def run(url, resp=None):
    '''Detect cross-domain JavaScript inclusions'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            # Load guide from help.json
            help_path = os.path.join(os.path.dirname(__file__), 'help.json')
            try:
                with open(help_path, 'r', encoding='utf-8') as f:
                    help_data = json.load(f)
                guide = help_data.get('check_26_cross_domain_js', '')
            except Exception:
                guide = ''
            return {
                'name': 'Detect cross-domain JavaScript inclusions',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1,
                'guide': guide
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    page_domain = urlparse(url).netloc
    cross_domain_js = []
    for script in soup.find_all('script', src=True):
        src = script['src']
        parsed_src = urlparse(src)
        if parsed_src.scheme in ['http', 'https']:
            src_domain = parsed_src.netloc
            if src_domain and src_domain != page_domain:
                cross_domain_js.append(src)
    status = 'fail' if cross_domain_js else 'pass'
    # Risk: 3 (Medium) if cross-domain JS found, 1 (Info) if not
    risk = 3 if cross_domain_js else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_26_cross_domain_js', '')
    except Exception:
        guide = ''
    return {
        'name': 'Detect cross-domain JavaScript inclusions',
        'status': status,
        'description': 'Detects JS loaded from other domains',
        'evidence': cross_domain_js if cross_domain_js else None,
        'risk': risk,
        'guide': guide
    }
