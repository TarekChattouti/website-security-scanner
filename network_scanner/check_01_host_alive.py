import subprocess
import re

def run(target):
    '''Check if host is alive using ping and return structured evidence'''
    try:
        output = subprocess.run(['ping', '-c', '1', '-W', '2', target], capture_output=True, text=True)
        alive = output.returncode == 0
        latency = None
        for line in output.stdout.splitlines():
            if 'time=' in line:
                match = re.search(r'time=([\d.]+) ms', line)
                if match:
                    latency = float(match.group(1))
        evidence = {
            'alive': alive,
            'latency_ms': latency,
            'raw': output.stdout.strip()
        }
        return {
            'name': 'Host Alive Check',
            'status': 'pass' if alive else 'fail',
            'description': 'ICMP ping to check if host is alive',
            'evidence': evidence,
            'risk': 1
        }
    except Exception as e:
        return {
            'name': 'Host Alive Check',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1
        }
