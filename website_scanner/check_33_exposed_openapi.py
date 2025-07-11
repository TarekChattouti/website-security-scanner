
import requests
from urllib.parse import urljoin
import os
import json

def run(url, resp=None):
    '''Detect exposed OpenAPI or Swagger files'''
    candidates = [
        'openapi.json',
        'swagger.json',
        'swagger/v1/swagger.json',
        'api/openapi.json',
        'api/swagger.json',
        'v1/openapi.json',
        'v1/swagger.json',
        '.well-known/openapi.json',
        '.well-known/swagger.json'
    ]
    found = {}
    for path in candidates:
        test_url = urljoin(url, '/' + path)
        try:
            r = requests.get(test_url, timeout=5, verify=False)
            if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('application/json'):
                # Only show a preview of the file
                found[test_url] = r.text[:500]
        except Exception as e:
            continue
    status = 'fail' if found else 'pass'
    # Risk: 4 (High) if exposed OpenAPI/Swagger, 1 (Info) if not
    risk = 4 if found else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_33_exposed_openapi', '')
    except Exception:
        guide = ''
    return {
        'name': 'Detect exposed OpenAPI or Swagger files',
        'status': status,
        'description': 'Checks for openapi.json or swagger.json',
        'evidence': found if found else None,
        'risk': risk,
        'guide': guide
    }
