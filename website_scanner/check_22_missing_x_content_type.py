def run(url, resp=None):
    '''Missing HTTP header - X-Content-Type-Options'''
    x_content_type = resp.headers.get('X-Content-Type-Options') if resp else None
    status = 'pass' if x_content_type else 'fail'
    # Risk: 2 (Low) if missing, 1 (Info) if present
    risk = 2 if status == 'fail' else 1
    return {
        'name': 'Missing HTTP header - X-Content-Type-Options',
        'status': status,
        'description': 'Checks for X-Content-Type-Options header',
        'evidence': x_content_type,
        'risk': risk
    }
