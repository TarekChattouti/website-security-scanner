def run(url, resp=None):
    '''Missing Secure flag on cookie'''
    cookies = resp.cookies if resp else []
    missing_secure = []
    for cookie in cookies:
        # The 'secure' attribute is True if the Secure flag is set
        if not getattr(cookie, 'secure', False):
            missing_secure.append({'name': cookie.name, 'domain': getattr(cookie, 'domain', None)})
    status = 'fail' if missing_secure else 'pass'
    # Risk: 3 (Medium) if missing Secure flag, 1 (Info) if not
    risk = 3 if missing_secure else 1
    return {
        'name': 'Missing Secure flag on cookie',
        'status': status,
        'description': 'Checks if cookies have Secure flag',
        'evidence': missing_secure if missing_secure else None,
        'risk': risk
    }
