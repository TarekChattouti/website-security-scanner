from bs4 import BeautifulSoup
import requests


def run(url, resp=None):
    '''Detect file upload fields'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Detect file upload fields',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    upload_forms = []
    for form in soup.find_all('form'):
        for inp in form.find_all('input', {'type': 'file'}):
            upload_forms.append({
                'form_action': form.get('action'),
                'input_name': inp.get('name'),
                'input_id': inp.get('id')
            })
    status = 'fail' if upload_forms else 'pass'
    risk = 4 if upload_forms else 1
    return {
        'name': 'Detect file upload fields',
        'status': status,
        'description': 'Detects file upload forms',
        'evidence': upload_forms if upload_forms else None,
        'risk': risk
    }
