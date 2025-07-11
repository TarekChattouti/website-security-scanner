
import subprocess
import re
import os
import json

def run(target):
    '''Run nmap vulners script for vulnerability detection and return structured evidence'''
    try:
        output = subprocess.run(['nmap', '-sV', '--script', 'vulners', target], capture_output=True, text=True, timeout=300)
        vulns = []
        current_port = None
        for line in output.stdout.splitlines():
            port_match = re.match(r'^(\d+/\w+)\s+open\s+([\w-]+)', line)
            if port_match:
                current_port = port_match.group(1)
                continue
            cve_match = re.search(r'(CVE-\d{4}-\d+)', line)
            if cve_match and current_port:
                vulns.append({
                    "port": current_port,
                    "cve": cve_match.group(1),
                    "line": line.strip()
                })
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_04_vuln_detect', '')
        except Exception:
            guide = ''
        return {
            'name': 'Vulnerability Detection',
            'status': 'pass',
            'description': 'nmap vulners script output',
            'evidence': vulns,
            'risk': 4 if vulns else 1,
            'guide': guide
        }
    except Exception as e:
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_04_vuln_detect', '')
        except Exception:
            guide = ''
        return {
            'name': 'Vulnerability Detection',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1,
            'guide': guide
        }
