import re
from bs4 import BeautifulSoup
import requests

def run(url, resp=None):
    '''Path disclosure in error messages'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Path disclosure in error messages',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text() + resp.text
    # Common path disclosure patterns (Linux, Windows, PHP, Python, Java, etc.)
    patterns = [
        r'/[\w\-_/]+/([\w\-_.]+\.(php|py|js|java|rb|pl|cgi|asp|aspx|jsp|html|htm|log|txt|conf|ini|sh|bat|dll|exe|so|jar|class))',
        r'[A-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)+[^\\/:*?"<>|\r\n]+',
        r'\\[\w\-_.]+\\[\w\-_.]+',
        r' in <b>(/[^<]+)</b>',
        r' in <b>([A-Z]:\\[^<]+)</b>'
    ]
    found = []
    for pattern in patterns:
        found += re.findall(pattern, text, re.IGNORECASE)
    # Flatten tuples and deduplicate
    flat = set()
    for f in found:
        if isinstance(f, tuple):
            flat.add(f[0])
        else:
            flat.add(f)
    status = 'fail' if flat else 'pass'
    # Risk: 3 (Medium) if path disclosure found, 1 (Info) if not
    risk = 3 if flat else 1
    return {
        'name': 'Path disclosure in error messages',
        'status': status,
        'description': 'Detects file path disclosure in errors',
        'evidence': list(flat) if flat else None,
        'risk': risk
    }
