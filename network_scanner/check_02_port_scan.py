import subprocess

def run(target):
    '''Scan for open ports using nmap'''
    try:
        output = subprocess.run(['nmap', '-T4', '-F', target], capture_output=True, text=True, timeout=60)
        return {
            'name': 'Port Scan',
            'status': 'pass',
            'description': 'Quick nmap scan for open ports',
            'evidence': output.stdout.strip(),
            'risk': 2
        }
    except Exception as e:
        return {
            'name': 'Port Scan',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 2
        }
