def run(url, resp=None):
    csp = resp.headers.get('Content-Security-Policy') if resp else None
    unsafe = []
    if csp:
        # Check for unsafe directives
        if "'unsafe-inline'" in csp or 'unsafe-inline' in csp:
            unsafe.append("'unsafe-inline'")
        if "'unsafe-eval'" in csp or 'unsafe-eval' in csp:
            unsafe.append("'unsafe-eval'")
        if '*' in csp:
            unsafe.append('* (wildcard)')
        if 'data:' in csp:
            unsafe.append('data:')
        if 'script-src' in csp and 'http:' in csp:
            unsafe.append('script-src allows http:')
        if 'object-src' in csp and ("'none'" not in csp and 'none' not in csp):
            unsafe.append('object-src not set to none')
    status = 'fail' if unsafe else ('pass' if csp else 'info')
    risk = 4 if unsafe else 1  # Risk: 4 if unsafe CSP config, 1 if safe or missing
    return {
        'name': 'Detect unsafe Content-Security-Policy config',
        'status': status,
        'description': 'Checks for unsafe CSP settings',
        'evidence': {'csp': csp, 'unsafe': unsafe} if csp else 'No CSP header present',
        'risk': risk
    }
