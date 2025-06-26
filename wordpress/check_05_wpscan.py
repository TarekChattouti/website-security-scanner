import subprocess
import json

def run(url, resp=None):
    '''Scan with WPScan (external tool via Docker)'''
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
        try:
            data = json.loads(result.stdout)
            # If scan_aborted, show a clear message
            if data.get('scan_aborted'):
                status = 'fail'
                description = f"WPScan aborted: {data['scan_aborted']}"
                evidence = {
                    'scan_aborted': data['scan_aborted'],
                    'target_url': data.get('target_url')
                }
            else:
                status = 'pass' if result.returncode == 0 else 'fail'
                description = 'Runs WPScan in Docker for deep WordPress vulnerability scanning'
                # Clean evidence: remove banner, keep findings
                evidence = {k: v for k, v in data.items() if k not in ['banner']}
        except Exception as e:
            status = 'error'
            description = f'Could not parse WPScan output as JSON: {str(e)}'
            evidence = result.stdout[:1000]
        return {
            'name': 'Scan with WPScan (Docker)',
            'status': status,
            'description': description,
            'evidence': evidence,
            'risk': 4
        }
    except Exception as e:
        return {
            'name': 'Scan with WPScan (Docker)',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 1
        }
