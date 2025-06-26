from urllib.parse import urlparse, parse_qs


def run(url, resp=None):
    '''Detect passwords in URL query string'''
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    password_keys = ['password', 'passwd', 'pwd', 'pass', 'secret', 'token']
    found = {}
    for key in query:
        if any(pw in key.lower() for pw in password_keys):
            found[key] = query[key]
    status = 'fail' if found else 'pass'
    risk = 4 if found else 1
    return {
        'name': 'Detect passwords in URL query string',
        'status': status,
        'description': 'Detects password values in URL',
        'evidence': found if found else None,
        'risk': risk
    }
