import json
import os

def run(url, resp=None):
    '''Parse WPScan output for main theme vulnerabilities'''
    wpscan_data = None
    if resp and hasattr(resp, 'wpscan_output'):
        wpscan_data = resp.wpscan_output
    elif resp and isinstance(resp, dict) and 'wpscan_output' in resp:
        wpscan_data = resp['wpscan_output']
    if not wpscan_data:
        # Load guide from help.json
        help_file = os.path.join(os.path.dirname(__file__), 'help.json')
        guide = ""
        try:
            with open(help_file, 'r') as f:
                help_data = json.load(f)
                guide = help_data.get('check_07_theme_vulns', '')
        except:
            pass
            
        return {
            'name': 'Search for main theme vulnerabilities',
            'status': 'error',
            'description': 'No WPScan output available to parse.',
            'evidence': None,
            'risk': 2,
            'guide': guide
        }
    try:
        data = wpscan_data if isinstance(wpscan_data, dict) else json.loads(wpscan_data)
        main_theme = data.get('main_theme', {})
        theme_vulns = main_theme.get('vulnerabilities', [])
        theme_name = main_theme.get('slug') or main_theme.get('style_name') or 'unknown'
        status = 'fail' if theme_vulns else 'pass'
        description = f'Found {len(theme_vulns)} vulnerabilities for theme {theme_name}' if theme_vulns else f'No known vulnerabilities for theme {theme_name}'
        evidence = theme_vulns
        risk = 4 if theme_vulns else 1
    except Exception as e:
        status = 'error'
        description = f'Could not parse WPScan output as JSON: {str(e)}'
        evidence = str(wpscan_data)[:1000]
        risk = 2
    return {
        'name': 'Search for main theme vulnerabilities',
        'status': status,
        'description': description,
        'evidence': evidence,
        'risk': risk
    }
