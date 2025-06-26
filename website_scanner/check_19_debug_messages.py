import re
from bs4 import BeautifulSoup

def run(url, resp=None):
    '''Detect debug messages (console.log, stacktrace)'''
    if resp is None:
        try:
            import requests
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Detect debug messages',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e)
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    scripts = soup.find_all('script')
    debug_patterns = [
        r'console\.log\s*\(',
        r'console\.debug\s*\(',
        r'console\.warn\s*\(',
        r'console\.error\s*\(',
        r'Stacktrace',
        r'Traceback',
        r'Error:',
        r'Exception:',
        r'window\.alert\s*\(',
        r'debugger;'
    ]
    found = []
    # Check inline scripts
    for script in scripts:
        script_content = script.string or ''
        for pattern in debug_patterns:
            if re.search(pattern, script_content, re.IGNORECASE):
                found.append(pattern)
    # Check page text for stack traces
    text = soup.get_text() + resp.text
    for pattern in ['stack trace', 'traceback', 'exception', 'error at', 'uncaught exception']:
        if pattern.lower() in text.lower():
            found.append(pattern)
    found = list(set(found))
    status = 'fail' if found else 'pass'
    # Risk: 3 (Medium) if debug messages found, 1 (Info) if not
    risk = 3 if found else 1
    return {
        'name': 'Detect debug messages',
        'status': status,
        'description': 'Detects debug messages in HTML/JS',
        'evidence': found if found else None,
        'risk': risk
    }
