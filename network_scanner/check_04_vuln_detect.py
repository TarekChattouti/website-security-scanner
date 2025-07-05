import subprocess

def run(target):
    '''Run nmap vulners script for vulnerability detection'''
    try:
        output = subprocess.run(['nmap', '-sV', '--script', 'vulners', target], capture_output=True, text=True, timeout=300)
        return {
            'name': 'Vulnerability Detection',
            'status': 'pass',
            'description': 'nmap vulners script output',
            'evidence': output.stdout.strip(),
            'risk': 4
        }
    except Exception as e:
        return {
            'name': 'Vulnerability Detection',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 4
        }
