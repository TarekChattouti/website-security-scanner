import requests

def run(url, resp=None):
    '''Check for robots.txt file'''
    robots_url = url.rstrip('/') + '/robots.txt'
    try:
        r = requests.get(robots_url, timeout=5)
        found = r.status_code == 200
        return {
            'name': 'Check for robots.txt file',
            'status': 'pass' if found else 'fail',
            'description': 'Checks if robots.txt file is present',
            'evidence': {'url': robots_url, 'status_code': r.status_code, 'content': r.text[:200]},
            'risk': 1
        }
    except Exception as e:
        return {
            'name': 'Check for robots.txt file',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1
        }
