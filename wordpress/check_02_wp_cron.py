import requests

def run(url, resp=None):
    '''Check whether wp-cron is enabled'''
    try:
        cron_url = url.rstrip('/') + '/wp-cron.php'
        r = requests.get(cron_url, timeout=7)
        enabled = r.status_code == 200 and 'do not access this file directly' not in r.text.lower()
        return {
            'name': 'Check whether wp-cron is enabled',
            'status': 'fail' if enabled else 'pass',
            'description': 'Checks if wp-cron.php is accessible (should not be public)',
            'evidence': {'url': cron_url, 'status_code': r.status_code, 'body': r.text[:200]},
            'risk': 3 if enabled else 1
        }
    except Exception as e:
        return {
            'name': 'Check whether wp-cron is enabled',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1
        }
