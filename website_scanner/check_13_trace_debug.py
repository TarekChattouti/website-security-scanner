import requests


def run(url, resp=None):
    '''Check if HTTP TRACE/DEBUG methods are enabled'''
    results = {}
    for method in ['TRACE', 'DEBUG']:
        try:
            r = requests.request(method, url, timeout=7)
            if r.status_code == 200:
                results[method] = 'enabled'
            elif r.status_code in (405, 501):
                results[method] = 'not allowed'
            else:
                results[method] = f'HTTP {r.status_code}'
        except Exception as e:
            results[method] = f'Error: {e}'
    status = 'fail' if results.get('TRACE') == 'enabled' or results.get('DEBUG') == 'enabled' else 'pass'
    # Risk: 4 (High) if enabled, 1 if not
    risk = 4 if status == 'fail' else 1
    return {
        'name': 'Check if HTTP TRACE/DEBUG methods are enabled',
        'status': status,
        'description': 'Checks for TRACE/DEBUG HTTP methods',
        'evidence': results,
        'risk': risk
    }
