
import subprocess
import os
import json

def run(target):
    '''Scan for open ports using nmap and return structured evidence'''
    try:
        output = subprocess.run(['nmap', '-T4', '-F', target], capture_output=True, text=True, timeout=60)
        ports = []
        in_ports = False
        for line in output.stdout.splitlines():
            if line.startswith("PORT"):
                in_ports = True
                continue
            if in_ports:
                if line.strip() == "" or line.startswith("Nmap done:"):
                    break
                parts = line.split()
                if len(parts) >= 3:
                    ports.append({
                        "port": parts[0],
                        "state": parts[1],
                        "service": parts[2]
                    })
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_02_port_scan', '')
        except Exception:
            guide = ''
        return {
            'name': 'Port Scan',
            'status': 'pass',
            'description': 'Quick nmap scan for open ports',
            'evidence': ports,
            'risk': 2,
            'guide': guide
        }
    except Exception as e:
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_02_port_scan', '')
        except Exception:
            guide = ''
        return {
            'name': 'Port Scan',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 2,
            'guide': guide
        }
