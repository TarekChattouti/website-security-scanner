import subprocess

def run(target):
    '''Detect services using nmap'''
    try:
        output = subprocess.run(['nmap', '-sV', '--version-light', target], capture_output=True, text=True, timeout=120)
        return {
            'name': 'Service Detection',
            'status': 'pass',
            'description': 'nmap service version detection',
            'evidence': output.stdout.strip(),
            'risk': 2
        }
    except Exception as e:
        return {
            'name': 'Service Detection',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 2
        }
