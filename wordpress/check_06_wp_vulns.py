import json
import os

def run(url, resp=None):
    '''Parse WPScan output for WordPress core vulnerabilities'''
    # Try to get WPScan output from resp.evidence if passed, or from a file if needed
    wpscan_data = None
    if resp and hasattr(resp, 'wpscan_output'):
        wpscan_data = resp.wpscan_output
    elif resp and isinstance(resp, dict) and 'wpscan_output' in resp:
        wpscan_data = resp['wpscan_output']
    # Optionally, you could load from a file if you save the main scan output
    if not wpscan_data:
        # Load guide from help.json
        help_file = os.path.join(os.path.dirname(__file__), 'help.json')
        guide = ""
        try:
            with open(help_file, 'r') as f:
                help_data = json.load(f)
                guide = help_data.get('check_06_wp_vulns', '')
        except:
            pass
            
        return {
            'name': 'Search for WordPress vulnerabilities',
            'status': 'error',
            'description': 'No WPScan output available to parse.',
            'evidence': None,
            'risk': 2,
            'guide': guide
        }
    try:
        data = wpscan_data if isinstance(wpscan_data, dict) else json.loads(wpscan_data)
        version = data.get('version', {})
        vulns = version.get('vulnerabilities', [])
        status = 'fail' if vulns else 'pass'
        description = f'Found {len(vulns)} core vulnerabilities' if vulns else 'No known core vulnerabilities found'
        evidence = vulns
        risk = 4 if vulns else 1
    except Exception as e:
        status = 'error'
        description = f'Could not parse WPScan output as JSON: {str(e)}'
        evidence = str(wpscan_data)[:1000]
        risk = 2
        
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_06_wp_vulns', '')
    except:
        pass
        
    return {
        'name': 'Search for WordPress vulnerabilities',
        'status': status,
        'description': description,
        'evidence': evidence,
        'risk': risk,
        'guide': guide
    }
