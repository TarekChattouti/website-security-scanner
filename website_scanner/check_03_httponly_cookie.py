def run(url, resp=None):
    cookies = resp.cookies if resp else []
    evidence = []
    for cookie in cookies:
        if not cookie.has_nonstandard_attr('HttpOnly'):
            evidence.append(cookie.name)
    status = 'fail' if evidence else 'pass'
    # Risk: 3 (Medium) if any cookies missing HttpOnly, 1 (Info) if all set
    risk = 3 if status == 'fail' else 1
    return {
        'name': 'HttpOnly flag of cookie',
        'status': status,
        'description': 'Checks if cookies have HttpOnly flag',
        'evidence': evidence,
        'risk': risk
    }
