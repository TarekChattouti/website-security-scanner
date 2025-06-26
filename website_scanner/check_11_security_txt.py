import requests
from .utils import safe_request


def run(url, resp=None):
    '''Check if .well-known/security.txt exists'''
    sec_url = url.rstrip('/') + '/.well-known/security.txt'
    try:
        r = safe_request(sec_url)
        if r.status_code == 200:
            status = 'pass'
            evidence = r.text[:500]  # Show first 500 chars
            risk = 1
        elif r.status_code == 404:
            status = 'fail'
            evidence = 'security.txt missing'
            risk = 2
        else:
            status = 'info'
            evidence = f'HTTP {r.status_code}'
            risk = 1
    except Exception as e:
        status = 'error'
        evidence = str(e)
        risk = 1
    return {
        'name': 'Check if .well-known/security.txt exists',
        'status': status,
        'description': 'Checks for .well-known/security.txt file and reports its presence/content',
        'evidence': evidence,
        'risk': risk
    }
