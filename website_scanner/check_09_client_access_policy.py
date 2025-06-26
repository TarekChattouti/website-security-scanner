import requests


def run(url, resp=None):
    '''Client access policies (crossdomain.xml, clientaccesspolicy.xml)'''
    results = {}
    for fname in ['crossdomain.xml', 'clientaccesspolicy.xml']:
        test_url = url.rstrip('/') + '/' + fname
        try:
            r = requests.get(test_url, timeout=5)
            if r.status_code == 200:
                results[fname] = 'Present'
            elif r.status_code == 403:
                results[fname] = 'Forbidden'
            elif r.status_code == 404:
                results[fname] = 'Missing'
            else:
                results[fname] = f'HTTP {r.status_code}'
        except Exception as e:
            results[fname] = f'Error: {e}'
    status = 'fail' if any(v == 'Present' for v in results.values()) else 'pass'
    # Risk: 3 (Medium) if present, 1 (Info) if not
    risk = 3 if status == 'fail' else 1
    return {
        'name': 'Client access policies',
        'status': status,
        'description': 'Checks for crossdomain.xml and clientaccesspolicy.xml',
        'evidence': results,
        'risk': risk
    }
