import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def run(url, resp=None):
    '''Detect unencrypted password forms'''
    # Fetch the page if not provided
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Detect unencrypted password forms',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e)
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    forms = soup.find_all('form')
    unencrypted_forms = []
    for form in forms:
        # Check if form has a password input
        if form.find('input', {'type': 'password'}):
            # Check form action
            action = form.get('action')
            if action:
                action_url = action if '://' in action else urlparse(url)._replace(path=action).geturl()
            else:
                action_url = url
            if action_url.startswith('http://'):
                unencrypted_forms.append({'form_action': action_url})
            elif url.startswith('http://'):
                unencrypted_forms.append({'form_action': action_url, 'reason': 'Page loaded over HTTP'})
    status = 'fail' if unencrypted_forms else 'pass'
    # Risk: 4 (High) if any unencrypted password forms, 1 (Info) if not
    risk = 4 if unencrypted_forms else 1
    return {
        'name': 'Detect unencrypted password forms',
        'status': status,
        'description': 'Detects password forms not using HTTPS',
        'evidence': unencrypted_forms if unencrypted_forms else None,
        'risk': risk
    }
