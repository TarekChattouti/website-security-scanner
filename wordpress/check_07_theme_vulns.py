import requests
import subprocess
import json
import re

def run(url, resp=None):
    '''Search for main theme vulnerabilities using local WPScan Docker'''
    try:
        # Try to detect main theme from HTML
        theme = None
        if resp and resp.text:
            m = re.search(r'/wp-content/themes/([\w-]+)/', resp.text)
            if m:
                theme = m.group(1)
        if not theme:
            return {
                'name': 'Search for main theme vulnerabilities',
                'status': 'info',
                'description': 'Could not detect main theme. Vulnerability lookup skipped.',
                'evidence': None,
                'risk': 2
            }
        docker_cmd = [
            'docker', 'run', '--rm',
            'wpscanteam/wpscan',
            '--url', url,
            '--no-update',
            '--format', 'json',
            '--enumerate', f't:{theme}',
            '--random-user-agent',
            '--throttle', '1'
        ]
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=600)
        try:
            data = json.loads(result.stdout)
            themes = data.get('themes', [])
            theme_vulns = []
            for t in themes:
                if t.get('slug') == theme:
                    theme_vulns = t.get('vulnerabilities', [])
                    break
            status = 'fail' if theme_vulns else 'pass'
            description = f'Found {len(theme_vulns)} vulnerabilities for theme {theme}' if theme_vulns else f'No known vulnerabilities for theme {theme}'
            evidence = theme_vulns
            risk = 4 if theme_vulns else 1
        except Exception as e:
            status = 'error'
            description = f'Could not parse WPScan output as JSON: {str(e)}'
            evidence = result.stdout[:1000]
            risk = 2
        return {
            'name': 'Search for main theme vulnerabilities',
            'status': status,
            'description': description,
            'evidence': evidence,
            'risk': risk
        }
    except Exception as e:
        return {
            'name': 'Search for main theme vulnerabilities',
            'status': 'error',
            'description': str(e),
            'evidence': None,
            'risk': 2
        }
