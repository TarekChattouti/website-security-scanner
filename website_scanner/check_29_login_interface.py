from bs4 import BeautifulSoup
import requests

def run(url, resp=None):
    '''Detect login interfaces'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Detect login interfaces',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1
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
    return {
        'name': 'Detect login interfaces',
        'status': status,
        'description': 'Detects login forms or endpoints',
        'evidence': evidence,
        'risk': risk
    }
