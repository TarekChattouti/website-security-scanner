
import subprocess
import json
import os

def run(target):
    '''Subdomain enumeration using subfinder (active only)'''
    try:
        output = subprocess.run([
            'subfinder',
            '-d', target,
            '-silent',
            '-oJ',
            '-active'  # Only include live subdomains
        ], capture_output=True, text=True, timeout=120)
        subdomains = []
        for line in output.stdout.splitlines():
            try:
                data = json.loads(line)
                if 'host' in data:
                    subdomains.append(data['host'])
            except Exception:
                continue
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_01_subfinder', '')
        except Exception:
            guide = ''
        return {
            'name': 'Subdomain Enumeration (subfinder)',
            'status': 'pass' if subdomains else 'fail',
            'description': 'Enumerates live subdomains using subfinder -active',
            'evidence': subdomains,
            'risk': 2 if subdomains else 1,
            'guide': guide
        }
    except Exception as e:
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_01_subfinder', '')
        except Exception:
            guide = ''
        return {
            'name': 'Subdomain Enumeration (subfinder)',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 2,
            'guide': guide
        }