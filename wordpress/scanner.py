import importlib
import os
import json
from datetime import datetime
from urllib.parse import urlparse
import requests
import subprocess
from scan_db import set_scan_status

def run_wordpress_checks(url, save=True, scan_id=None):
    results = []
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
    # Set progress to 5% before running WPScan
    if scan_id:
        set_scan_status(scan_id, progress=5, result={'url': url, 'results': results[:], 'scan_id': scan_id})
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
    # Set progress to 10% after WPScan completes
    if scan_id:
        set_scan_status(scan_id, progress=10, result={'url': url, 'results': results[:], 'scan_id': scan_id})
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
        # --- Progress and partial result update ---
        if scan_id:
            # Progress starts at 10% after WPScan, then increments through checks
            progress = 10 + int(((idx+1)/total)*89)  # 10-99%
            set_scan_status(scan_id, progress=progress, result={'url': url, 'results': results[:], 'scan_id': scan_id})
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
            json.dump({'url': url, 'results': results, 'scan_id': scan_id}, f, indent=2)
    set_scan_status(scan_id, progress=100, status='done', result={'url': url, 'results': results, 'scan_id': scan_id, 'severity': calculate_average_risk(results)})
    return {'url': url, 'results': results, 'scan_id': scan_id, 'severity': calculate_average_risk(results)}

def calculate_average_risk(results):
    risk_levels = [result.get('risk', 0) for result in results if 'risk' in result]
    if risk_levels:
        return sum(risk_levels) / len(risk_levels)
    return 0
