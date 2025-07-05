import subprocess
import re

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
        return {
            'name': 'Vulnerability Detection',
            'status': 'pass',
            'description': 'nmap vulners script output',
            'evidence': vulns,
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
