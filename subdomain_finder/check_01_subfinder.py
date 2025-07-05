import subprocess
import json

def run(target):
    '''Subdomain enumeration using subfinder'''
    try:
        # Run subfinder with JSON output
        output = subprocess.run([
            'subfinder',
            '-d', target,
            '-silent',
            '-oJ'
        ], capture_output=True, text=True, timeout=120)
        subdomains = []
        for line in output.stdout.splitlines():
            try:
                data = json.loads(line)
                if 'host' in data:
                    subdomains.append(data['host'])
            except Exception:
                continue
        return {
            'name': 'Subdomain Enumeration (subfinder)',
            'status': 'pass' if subdomains else 'fail',
            'description': 'Enumerates subdomains using subfinder',
            'evidence': subdomains,
            'risk': 2 if subdomains else 1
        }
    except Exception as e:
        return {
            'name': 'Subdomain Enumeration (subfinder)',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 2
        }
