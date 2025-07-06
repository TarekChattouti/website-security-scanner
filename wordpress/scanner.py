import importlib
import os
import json
from datetime import datetime

def run_wordpress_checks(url, save=True, scan_id=None):
    results = []
    import requests
    import subprocess
    from urllib.parse import urlparse
    # Get base response for header checks
    try:
        resp = requests.get(url, timeout=10, verify=False)
    except Exception:
        resp = None
    # Try WPScan with API key first, fallback to no API key
    docker_cmd = [
        'docker', 'run', '--rm',
        'wpscanteam/wpscan',
        '--url', url,
        '--no-update',
        '--format', 'json',
        '--enumerate', 'u',
        '--random-user-agent',
        '--throttle', '1',
        '--api-token', 'yuaBGak9WXHx6UPa6svSifZLFBEohwgEXYsl3dxdb3M'
    ]
    try:
        wpscan_result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=600)
        try:
            wpscan_output = json.loads(wpscan_result.stdout)
        except Exception:
            wpscan_output = wpscan_result.stdout
    except Exception as e:
        # Fallback: try again without API key
        docker_cmd_no_api = [
            'docker', 'run', '--rm',
            'wpscanteam/wpscan',
            '--url', url,
            '--no-update',
            '--format', 'json',
            '--enumerate', 'u',
            '--random-user-agent',
            '--throttle', '1'
        ]
        try:
            wpscan_result = subprocess.run(docker_cmd_no_api, capture_output=True, text=True, timeout=600)
            try:
                wpscan_output = json.loads(wpscan_result.stdout)
            except Exception:
                wpscan_output = wpscan_result.stdout
        except Exception as e2:
            wpscan_output = str(e2)
    # Prepare resp dict for passing WPScan output
    resp_dict = {'headers': resp.headers if resp else {}, 'text': resp.text if resp else '', 'wpscan_output': wpscan_output}
    wp_dir = os.path.dirname(__file__)
    check_files = [f for f in os.listdir(wp_dir) if f.startswith('check_') and f.endswith('.py')]
    check_files.sort()
    total = len(check_files)
    for idx, check_file in enumerate(check_files):
        mod_name = f"wordpress.{check_file[:-3]}"
        mod = importlib.import_module(mod_name)
        try:
            # Pass WPScan output to WPScan, core, and theme vuln checks
            if check_file in ['check_05_wpscan.py', 'check_06_wp_vulns.py', 'check_07_theme_vulns.py']:
                result = mod.run(url, resp_dict)
            else:
                result = mod.run(url, resp)
        except Exception as e:
            result = {'name': check_file, 'status': 'error', 'description': str(e), 'evidence': None, 'risk': 1}
        results.append(result)
        # --- Progress update ---
        if scan_id:
            try:
                from main import SCAN_STATUS
                if scan_id in SCAN_STATUS:
                    SCAN_STATUS[scan_id]['progress'] = max(1, min(99, int(((idx+1)/total)*100)))
            except Exception:
                pass
    # Save results to results folder with date and domain in filename
    if save:
        parsed = urlparse(url)
        domain = parsed.netloc.replace(':', '_')
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"wp_{date_str}_{domain}.json"
        results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(results_dir, exist_ok=True)
        filepath = os.path.join(results_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'url': url, 'results': results}, f, indent=2)
    return {'url': url, 'results': results, 'scan_id': scan_id}
