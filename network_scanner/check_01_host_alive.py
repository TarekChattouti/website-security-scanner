import subprocess

def run(target):
    '''Check if host is alive using ping'''
    try:
        output = subprocess.run(['ping', '-c', '1', '-W', '2', target], capture_output=True, text=True)
        alive = output.returncode == 0
        return {
            'name': 'Host Alive Check',
            'status': 'pass' if alive else 'fail',
            'description': 'ICMP ping to check if host is alive',
            'evidence': output.stdout.strip(),
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
