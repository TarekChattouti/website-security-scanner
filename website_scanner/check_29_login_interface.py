
from bs4 import BeautifulSoup
import requests
import os
import json

def run(url, resp=None):
    '''Detect login interfaces'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            # Load guide from help.json
            help_path = os.path.join(os.path.dirname(__file__), 'help.json')
            try:
                with open(help_path, 'r', encoding='utf-8') as f:
                    help_data = json.load(f)
                guide = help_data.get('check_29_login_interface', '')
            except Exception:
                guide = ''
            return {
                'name': 'Detect login interfaces',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1,
                'guide': guide
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    login_forms = []
    for form in soup.find_all('form'):
        # Look for password fields or typical login field names
        if form.find('input', {'type': 'password'}) or any(
            kw in (form.get('id','') + form.get('name','') + str(form.get('action',''))).lower() for kw in ['login', 'signin', 'auth']):
            login_forms.append({
                'action': form.get('action'),
                'id': form.get('id'),
                'name': form.get('name')
            })
    # Also look for common login endpoints in links
    login_links = []
    for a in soup.find_all('a', href=True):
        if any(kw in a['href'].lower() for kw in ['login', 'signin', 'auth']):
            login_links.append(a['href'])
    found = login_forms or login_links
    status = 'fail' if found else 'pass'
    evidence = {'forms': login_forms, 'links': login_links} if found else None
    # Risk: 2 (Low) if login interface found, 1 (Info) if not
    risk = 2 if found else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_29_login_interface', '')
    except Exception:
        guide = ''
    return {
        'name': 'Detect login interfaces',
        'status': status,
        'description': 'Detects login forms or endpoints',
        'evidence': evidence,
        'risk': risk,
        'guide': guide
    }
