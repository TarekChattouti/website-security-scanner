import re
from bs4 import BeautifulSoup
import requests

def run(url, resp=None):
    '''Detect password values in later response'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Detect password values in later response',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text() + resp.text
    # Look for common password patterns in the response
    patterns = [
        r'password\s*[=:]\s*([\w!@#$%^&*()_+\-={}:;\'\"\[\]<>.,?/\\|]+)',
        r'pwd\s*[=:]\s*([\w!@#$%^&*()_+\-={}:;\'\"\[\]<>.,?/\\|]+)',
        r'pass\s*[=:]\s*([\w!@#$%^&*()_+\-={}:;\'\"\[\]<>.,?/\\|]+)',
        r'"password"\s*:\s*"([^"]+)"',
        r'\'password\'\s*:\s*\'([^\']+)\'',
        r'passwd\s*[=:]\s*([\w!@#$%^&*()_+\-={}:;\'\"\[\]<>.,?/\\|]+)',
        r'login\s*[=:]\s*([\w!@#$%^&*()_+\-={}:;\'\"\[\]<>.,?/\\|]+)',
        r'username\s*[=:]\s*([\w!@#$%^&*()_+\-={}:;\'\"\[\]<>.,?/\\|]+)',
        r'email\s*[=:]\s*([\w!#$%^&*()_+\-={}:;\'\"\[\]<>.,?/\\|]+)'
    ]
    found = []
    for pattern in patterns:
        found += re.findall(pattern, text, re.IGNORECASE)
    found = list(set(found))
    status = 'fail' if found else 'pass'
    # Risk: 5 (Critical) if password values found, 1 (Info) if not
    risk = 5 if found else 1
    return {
        'name': 'Detect password values in later response',
        'status': status,
        'description': 'Detects password values in HTTP response',
        'evidence': found if found else None,
        'risk': risk
    }
