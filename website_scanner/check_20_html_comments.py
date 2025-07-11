
from bs4 import BeautifulSoup, Comment
import requests
import os
import json


def run(url, resp=None):
    '''Detect HTML code comments'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            # Load guide from help.json
            help_path = os.path.join(os.path.dirname(__file__), 'help.json')
            try:
                with open(help_path, 'r', encoding='utf-8') as f:
                    help_data = json.load(f)
                guide = help_data.get('check_20_html_comments', '')
            except Exception:
                guide = ''
            return {
                'name': 'Detect HTML code comments',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'guide': guide
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    comments = [comment for comment in soup.find_all(string=lambda text: isinstance(text, Comment))]
    status = 'fail' if comments else 'pass'
    risk = 2 if comments else 1  # Risk: 2 (Low) if comments found, 1 (Info) if not
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_20_html_comments', '')
    except Exception:
        guide = ''
    return {
        'name': 'Detect HTML code comments',
        'status': status,
        'description': 'Detects HTML comments in page source',
        'evidence': comments[:10] if comments else None,  # Show up to 10 comments
        'risk': risk,
        'guide': guide
    }
