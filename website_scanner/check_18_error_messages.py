import requests
from bs4 import BeautifulSoup

def run(url, resp=None):
    '''Detect error messages in responses'''
    # Fetch the page if not provided
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Detect error messages in responses',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e)
            }
    # Common error message patterns
    error_patterns = [
        'error', 'exception', 'not found', 'fatal', 'warning', 'traceback',
        'stack trace', 'undefined', 'failed', 'unhandled', 'parse error',
        'syntax error', 'sql syntax', 'permission denied', 'access denied',
        'segmentation fault', 'internal server error', 'application error',
        'server error', 'runtime error', 'invalid', 'missing', 'cannot',
        'unavailable', 'timeout', 'crash', 'abort', 'broken', 'denied'
    ]
    found = []
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text().lower()
    for pattern in error_patterns:
        if pattern in text:
            found.append(pattern)
    status = 'fail' if found else 'pass'
    # Risk: 3 (Medium) if error messages found, 1 (Info) if not
    risk = 3 if found else 1
    return {
        'name': 'Detect error messages in responses',
        'status': status,
        'description': 'Detects error messages in HTTP responses',
        'evidence': list(set(found)) if found else None,
        'risk': risk
    }
