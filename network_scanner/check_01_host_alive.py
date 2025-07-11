
import subprocess
import re
import os
import json

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
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_01_host_alive', '')
        except Exception:
            guide = ''
        return {
            'name': 'Host Alive Check',
            'status': 'pass' if alive else 'fail',
            'description': 'ICMP ping to check if host is alive',
            'evidence': evidence,
            'risk': 1,
            'guide': guide
        }
    except Exception as e:
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_01_host_alive', '')
        except Exception:
            guide = ''
        return {
            'name': 'Host Alive Check',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1,
            'guide': guide
        }
