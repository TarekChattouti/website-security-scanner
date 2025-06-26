import subprocess

def run(url, resp=None):
    '''Scan with WPScan (external tool)'''
    try:
        docker_cmd = [
            'docker', 'run', '--rm',
            'wpscanteam/wpscan',
            '--url', url,
            '--no-update',
            '--format', 'json',
            '--enumerate', 'u'
        ]
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=180)
        output = result.stdout[:2000]  # Limit output for evidence
        return {
            'name': 'Scan with WPScan',
            'status': 'pass' if result.returncode == 0 else 'fail',
            'description': 'Runs WPScan for deep WordPress vulnerability scanning',
            'evidence': output,
            'risk': 4
        }
    except Exception as e:
        return {
            'name': 'Scan with WPScan',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1
        }
