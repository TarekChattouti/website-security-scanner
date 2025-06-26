import requests
import subprocess
import json

def run(url, resp=None):
    '''Search for WordPress core vulnerabilities using local WPScan Docker'''
    try:
        docker_cmd = [
            'docker', 'run', '--rm',
            'wpscanteam/wpscan',
            '--url', url,
            '--no-update',
            '--format', 'json',
            '--enumerate', 'v',  # 'v' for vulnerabilities
            '--random-user-agent',
            '--throttle', '1'
        ]
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=600)
        try:
            data = json.loads(result.stdout)
            vulns = data.get('version', {}).get('vulnerabilities', [])
            status = 'fail' if vulns else 'pass'
            description = f'Found {len(vulns)} core vulnerabilities' if vulns else 'No known core vulnerabilities found'
            evidence = vulns
            risk = 4 if vulns else 1
        except Exception as e:
            status = 'error'
            description = f'Could not parse WPScan output as JSON: {str(e)}'
            evidence = result.stdout[:1000]
            risk = 2
        return {
            'name': 'Search for WordPress vulnerabilities',
            'status': status,
            'description': description,
            'evidence': evidence,
            'risk': risk
        }
    except Exception as e:
        return {
            'name': 'Search for WordPress vulnerabilities',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 2
        }
