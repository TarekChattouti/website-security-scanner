def run(url, resp=None):
    val = resp.headers.get('Referrer-Policy') if resp else None
    status = 'fail' if not val else 'pass'
    # Risk: 2 (Low) if missing, 1 (Info) if present
    risk = 2 if status == 'fail' else 1
    return {
        'name': 'Missing HTTP header - Referrer-Policy',
        'status': status,
        'description': 'Checks for Referrer-Policy header',
        'evidence': val,
        'risk': risk
    }
