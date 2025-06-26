def run(url, resp=None):
    '''Missing HTTP header - Strict-Transport-Security'''
    hsts = resp.headers.get('Strict-Transport-Security') if resp else None
    status = 'pass' if hsts else 'fail'
    # Risk: 3 (Medium) if missing, 1 (Info) if present
    risk = 3 if status == 'fail' else 1
    return {
        'name': 'Missing HTTP header - Strict-Transport-Security',
        'status': status,
        'description': 'Checks for HSTS header',
        'evidence': hsts,
        'risk': risk
    }
