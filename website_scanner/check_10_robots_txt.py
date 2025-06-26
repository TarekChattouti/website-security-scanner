import requests
from .utils import safe_request

def run(url, resp=None):
    '''Check if robots.txt exists'''
    robots_url = url.rstrip('/') + '/robots.txt'
    try:
        r = safe_request(robots_url)
        if r.status_code == 200:
            status = 'fail'  # Fail if present (may expose sensitive paths)
            evidence = r.text[:500]  # Show first 500 chars
            risk = 2  # Low risk if present
        elif r.status_code == 404:
            status = 'pass'
            evidence = 'robots.txt missing'
            risk = 1  # Info risk if not present
        else:
            status = 'info'
            evidence = f'HTTP {r.status_code}'
            risk = 1  # Info risk for other statuses
    except Exception as e:
        status = 'error'
        evidence = str(e)
        risk = 1  # Info risk on error
    return {
        'name': 'Check if robots.txt exists',
        'status': status,
        'description': 'Checks for robots.txt file and reports its presence/content',
        'evidence': evidence,
        'risk': risk
    }
