import requests
from requests.exceptions import SSLError

def run(url, resp=None):
    '''Check for untrusted SSL certificates'''
    try:
        requests.get(url, timeout=7, verify=True)
        status = 'pass'
        evidence = 'SSL certificate is trusted.'
        risk = 1
    except SSLError as e:
        status = 'fail'
        evidence = f'SSL certificate error: {e}'
        risk = 5
    except Exception as e:
        status = 'error'
        evidence = str(e)
        risk = 1
    return {
        'name': 'Check for untrusted SSL certificates',
        'status': status,
        'description': 'Checks for SSL certificate trust issues',
        'evidence': evidence,
        'risk': risk
    }
