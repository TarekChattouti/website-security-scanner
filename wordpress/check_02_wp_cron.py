import requests
import json
import os

def run(url, resp=None):
    '''Check whether wp-cron is enabled'''
    try:
        cron_url = url.rstrip('/') + '/wp-cron.php'
        r = requests.get(cron_url, timeout=7)
        enabled = r.status_code == 200 and 'do not access this file directly' not in r.text.lower()
        
        # Load guide from help.json
        help_file = os.path.join(os.path.dirname(__file__), 'help.json')
        guide = ""
        try:
            with open(help_file, 'r') as f:
                help_data = json.load(f)
                guide = help_data.get('check_02_wp_cron', '')
        except:
            pass
            
        return {
            'name': 'Check whether wp-cron is enabled',
            'status': 'fail' if enabled else 'pass',
            'description': 'Checks if wp-cron.php is accessible (should not be public)',
            'evidence': {'url': cron_url, 'status_code': r.status_code, 'body': r.text[:200]},
            'risk': 3 if enabled else 1,
            'guide': guide
        }
    except Exception as e:
        # Load guide from help.json
        help_file = os.path.join(os.path.dirname(__file__), 'help.json')
        guide = ""
        try:
            with open(help_file, 'r') as f:
                help_data = json.load(f)
                guide = help_data.get('check_02_wp_cron', '')
        except:
            pass
            
        return {
            'name': 'Check whether wp-cron is enabled',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1,
            'guide': guide
        }
