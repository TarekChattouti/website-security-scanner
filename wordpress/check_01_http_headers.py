def run(url, resp=None):
    '''Check for valuable information in HTTP headers'''
    headers = resp.headers if resp else {}
    info = {k: v for k, v in headers.items() if k.lower() in ['server', 'x-powered-by', 'set-cookie', 'x-frame-options', 'x-content-type-options', 'x-xss-protection']}
    return {
        'name': 'Check for valuable information in HTTP headers',
        'status': 'pass' if info else 'info',
        'description': 'Checks for potentially valuable information in HTTP headers',
        'evidence': info,
        'risk': 2 if info else 1
    }
