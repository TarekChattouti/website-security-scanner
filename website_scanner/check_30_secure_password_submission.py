
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import os
import json

def run(url, resp=None):
    '''Verify secure password submission'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            # Load guide from help.json
            help_path = os.path.join(os.path.dirname(__file__), 'help.json')
            try:
                with open(help_path, 'r', encoding='utf-8') as f:
                    help_data = json.load(f)
                guide = help_data.get('check_30_secure_password_submission', '')
            except Exception:
                guide = ''
            return {
                'name': 'Verify secure password submission',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1,
                'guide': guide
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    insecure_forms = []
    for form in soup.find_all('form'):
        if form.find('input', {'type': 'password'}):
            action = form.get('action')
            if action:
                action_url = action if '://' in action else urlparse(url)._replace(path=action).geturl()
            else:
                action_url = url
            if action_url.startswith('http://'):
                insecure_forms.append({'form_action': action_url, 'reason': 'Form submits to HTTP'})
            elif url.startswith('http://'):
                insecure_forms.append({'form_action': action_url, 'reason': 'Page loaded over HTTP'})
    status = 'fail' if insecure_forms else 'pass'
    # Risk: 5 (Critical) if insecure password submission, 1 (Info) if not
    risk = 5 if insecure_forms else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_30_secure_password_submission', '')
    except Exception:
        guide = ''
    return {
        'name': 'Verify secure password submission',
        'status': status,
        'description': 'Checks if password forms submit over HTTPS',
        'evidence': insecure_forms if insecure_forms else None,
        'risk': risk,
        'guide': guide
    }
