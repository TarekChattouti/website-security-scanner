import requests
import json
import os
from urllib.parse import urlparse, urlunparse
from .utils import safe_request

def run(url, resp=None):
    '''Enforce HTTPS-only (redirect from HTTP)'''
    parsed = urlparse(url)
    if parsed.scheme == 'https':
        # Convert to http for the test
        http_url = urlunparse(parsed._replace(scheme='http'))
    else:
        http_url = url
    try:
        r = safe_request(http_url)
        redirected = r.url.startswith('https://')
        status = 'pass' if redirected else 'fail'
        evidence = {
            'original_url': http_url,
            'final_url': r.url,
            'redirect_chain': [resp.url for resp in r.history] + [r.url] if r.history else [r.url]
        }
        risk = 4 if status == 'fail' else 1
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
            guide = help_data.get('check_15_https_redirect', '')
    except:
        pass
        
    return {
        'name': 'Enforce HTTPS-only',
        'status': status,
        'description': 'Checks if HTTP redirects to HTTPS',
        'evidence': evidence,
        'risk': risk,
        'guide': guide
    }
