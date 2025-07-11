
import subprocess
import os
import json

def run(target):
    '''Detect services using nmap and return structured evidence'''
    try:
        output = subprocess.run(['nmap', '-sV', '--version-light', target], capture_output=True, text=True, timeout=120)
        services = []
        in_ports = False
        for line in output.stdout.splitlines():
            if line.startswith("PORT"):
                in_ports = True
                continue
            if in_ports:
                if line.strip() == "" or line.startswith("Service detection performed") or line.startswith("Nmap done:"):
                    break
                parts = line.split()
                if len(parts) >= 4:
                    port = parts[0]
                    state = parts[1]
                    service = parts[2]
                    version = " ".join(parts[3:])
                    services.append({
                        "port": port,
                        "state": state,
                        "service": service,
                        "version": version
                    })
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_03_service_detect', '')
        except Exception:
            guide = ''
        return {
            'name': 'Service Detection',
            'status': 'pass',
            'description': 'nmap service version detection',
            'evidence': services,
            'risk': 2,
            'guide': guide
        }
    except Exception as e:
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_03_service_detect', '')
        except Exception:
            guide = ''
        return {
            'name': 'Service Detection',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 2,
            'guide': guide
        }
