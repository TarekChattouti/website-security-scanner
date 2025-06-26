def run(url, resp=None):
    '''Internal error code in response (500, etc.)'''
    code = resp.status_code if resp else None
    is_5xx = code is not None and 500 <= code < 600
    status = 'fail' if is_5xx else 'pass'
    # Risk: 4 (High) if 5xx error, 1 (Info) if not
    risk = 4 if is_5xx else 1
    return {
        'name': 'Internal error code in response',
        'status': status,
        'description': 'Checks for 5xx error codes',
        'evidence': code if is_5xx else None,
        'risk': risk
    }
