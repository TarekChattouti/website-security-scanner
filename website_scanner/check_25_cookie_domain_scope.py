def run(url, resp=None):
    '''Cookie domain too loosely scoped'''
    cookies = resp.cookies if resp else []
    loosely_scoped = []
    for cookie in cookies:
        domain = getattr(cookie, 'domain', None)
        if domain and (domain.startswith('.') or domain.count('.') > 1):
            loosely_scoped.append({'name': cookie.name, 'domain': domain})
    status = 'fail' if loosely_scoped else 'pass'
    risk = 2 if loosely_scoped else 1
    return {
        'name': 'Cookie domain too loosely scoped',
        'status': status,
        'description': 'Checks if cookie domain is too broad (e.g., .example.com)',
        'evidence': loosely_scoped if loosely_scoped else None,
        'risk': risk
    }
