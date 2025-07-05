import subprocess
import re

def run(target):
    '''SSL/TLS configuration and certificate check using testssl.sh'''
    # Extract hostname (strip protocol)
    host = target.replace('https://', '').replace('http://', '').split('/')[0]
    try:
        output = subprocess.run(['testssl.sh', '--quiet', '--warnings', 'off', host], capture_output=True, text=True, timeout=120)
        findings = []
        for line in output.stdout.splitlines():
            # Example: parse lines for protocols, ciphers, cert info, vulnerabilities, etc.
            if re.search(r'(TLS|SSL|RC4|BEAST|POODLE|Heartbleed|certificate|vulnerab|error)', line, re.I):
                findings.append(line.strip())
        return {
            'name': 'SSL/TLS Configuration and Certificate Check',
            'status': 'fail' if any('vulnerable' in f.lower() or 'error' in f.lower() for f in findings) else 'pass',
            'description': 'Checks SSL/TLS configuration and certificate using testssl.sh',
            'evidence': findings if findings else output.stdout[:1000],
            'risk': 4 if any('vulnerable' in f.lower() or 'error' in f.lower() for f in findings) else 1
        }
    except Exception as e:
        return {
            'name': 'SSL/TLS Configuration and Certificate Check',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 2
        }
