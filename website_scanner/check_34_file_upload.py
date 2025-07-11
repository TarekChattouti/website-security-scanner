
from bs4 import BeautifulSoup
import requests
import os
import json


def run(url, resp=None):
    '''Detect file upload fields'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            # Load guide from help.json
            help_path = os.path.join(os.path.dirname(__file__), 'help.json')
            try:
                with open(help_path, 'r', encoding='utf-8') as f:
                    help_data = json.load(f)
                guide = help_data.get('check_34_file_upload', '')
            except Exception:
                guide = ''
            return {
                'name': 'Detect file upload fields',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1,
                'guide': guide
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
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_34_file_upload', '')
    except Exception:
        guide = ''
    return {
        'name': 'Detect file upload fields',
        'status': status,
        'description': 'Detects file upload forms',
        'evidence': upload_forms if upload_forms else None,
        'risk': risk,
        'guide': guide
    }
