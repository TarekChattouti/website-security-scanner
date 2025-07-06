from flask import Flask, request, render_template_string
import json
from website_scanner.scanner import run_all_checks
from wordpress.scanner import run_wordpress_checks
from network_scanner.scanner import run_all_checks as run_network_checks
from ssl_scanner.scanner import run_all_checks as run_ssl_checks
from subdomain_finder.scanner import run_all_checks as run_subfinder_checks
import importlib
import os
from urllib.parse import urlparse
import threading
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)


SCAN_STATUS = {}

# Helper: background scan runner
def start_scan(tool, target):
    scan_id = None
    result = None
    pending_id = threading.current_thread().name if threading.current_thread().name.startswith('pending_') else None
    if tool == 'website':
        import os
        scan_id = pending_id if pending_id else f"website_{int(time.time()*1000)}"
        result = run_all_checks(target, scan_id=scan_id)
        scan_id = os.path.basename(result.get('saved_to', scan_id))
    elif tool == 'wordpress':
        scan_id = pending_id if pending_id else f"wordpress_{int(time.time()*1000)}"
        result = run_wordpress_checks(target, save=True, scan_id=scan_id)
        # scan_id is not a file, just keep as is
    elif tool == 'network':
        scan_id = pending_id if pending_id else f"network_{int(time.time()*1000)}"
        result = run_network_checks(target, scan_id=scan_id)
        if isinstance(result, list):
            from datetime import datetime
            import os
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = str(target).replace('https://', '').replace('http://', '').split('/')[0].replace(':', '_')
            scan_id_val = f"network_{date_str}_{domain}.json"
            results_dir = os.path.join(os.path.dirname(__file__), 'results')
            os.makedirs(results_dir, exist_ok=True)
            filepath = os.path.join(results_dir, scan_id_val)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({'target': target, 'results': result}, f, indent=2)
            result = {'target': target, 'results': result, 'scan_id': scan_id_val}
            scan_id = scan_id_val
        else:
            scan_id = result.get('scan_id', scan_id)
    elif tool == 'ssl':
        import os
        from datetime import datetime
        scan_id = pending_id if pending_id else f"ssl_{int(time.time()*1000)}"
        result = run_ssl_checks(target, scan_id=scan_id)
        if isinstance(result, list):
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = str(target).replace('https://', '').replace('http://', '').split('/')[0].replace(':', '_')
            scan_id_val = f"ssl_{date_str}_{domain}.json"
            results_dir = os.path.join(os.path.dirname(__file__), 'results')
            os.makedirs(results_dir, exist_ok=True)
            filepath = os.path.join(results_dir, scan_id_val)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({'target': target, 'results': result}, f, indent=2)
            result = {'target': target, 'results': result, 'scan_id': scan_id_val}
            scan_id = scan_id_val
        else:
            scan_id = result.get('scan_id', scan_id)
    elif tool == 'subdomain':
        scan_id = pending_id if pending_id else f"subdomain_{int(time.time()*1000)}"
        result = run_subfinder_checks(target, scan_id=scan_id)
        scan_id = result.get('scan_id', scan_id)
    if scan_id:
        # Only update status, don't overwrite result if already present
        if scan_id in SCAN_STATUS and SCAN_STATUS[scan_id]['result']:
            SCAN_STATUS[scan_id]['status'] = 'done'
        else:
            SCAN_STATUS[scan_id] = {'status': 'done', 'result': result}
        if pending_id:
            results_dir = os.path.join(os.path.dirname(__file__), 'results')
            os.makedirs(results_dir, exist_ok=True)
            mapping_path = os.path.join(results_dir, f"{pending_id}.map")
            with open(mapping_path, 'w', encoding='utf-8') as f:
                f.write(scan_id)
    return scan_id

def launch_scan_async(tool, target):
    scan_id = f"pending_{int(time.time()*1000)}_{tool}"
    SCAN_STATUS[scan_id] = {'status': 'running', 'result': None}
    def runner():
        threading.current_thread().name = scan_id
        real_id = start_scan(tool, target)
        if real_id:
            SCAN_STATUS[real_id] = SCAN_STATUS.pop(scan_id)
            SCAN_STATUS[real_id]['status'] = 'done'
        else:
            SCAN_STATUS[scan_id]['status'] = 'error'
    threading.Thread(target=runner, daemon=True).start()
    return scan_id

from flask import jsonify

@app.route('/api/v1/<tool>/scan', methods=['POST'])
def api_scan_launch(tool):
    data = request.get_json(force=True)
    target = data.get('target')
    if not target or tool not in ['website', 'wordpress', 'network', 'ssl', 'subdomain']:
        return jsonify({'error': 'Invalid tool or target'}), 400
    scan_id = launch_scan_async(tool, target)
    return jsonify({'scan_id': scan_id, 'status': 'started'})

@app.route('/api/v1/<tool>/scan', methods=['GET'])
def api_scan_result(tool):
    scan_id = request.args.get('scan_id')
    if not scan_id:
        return jsonify({'error': 'Missing scan_id'}), 400
    # Try in-memory first
    if scan_id in SCAN_STATUS:
        status = SCAN_STATUS[scan_id]['status']
        result = SCAN_STATUS[scan_id]['result']
        # Estimate progress
        if status == 'done':
            progress = 100
        elif status == 'running':
            progress = 1  # Start from 1
            if result:
                # If result is a dict with 'results' as a list, estimate by number of checks done
                if isinstance(result, dict) and 'results' in result and isinstance(result['results'], list):
                    total = 30  # Default: website_scanner has ~30 checks, adjust as needed
                    done = len(result['results'])
                    if total > 0:
                        progress = max(1, min(99, int((done / total) * 100)))
                # If result is a list (network/ssl), estimate by length
                elif isinstance(result, list):
                    total = 10  # Default for network/ssl, adjust as needed
                    done = len(result)
                    if total > 0:
                        progress = max(1, min(99, int((done / total) * 100)))
        else:
            progress = 0
        if status == 'done' and result and result.get('scan_id'):
            final_id = result['scan_id']
            results_dir = os.path.join(os.path.dirname(__file__), 'results')
            filepath = os.path.join(results_dir, final_id)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return jsonify({'status': 'done', 'result': data, 'scan_id': scan_id, 'progress': 100})
            else:
                return jsonify({'status': 'done', 'result': result, 'scan_id': scan_id, 'progress': 100})
        return jsonify({'status': status, 'result': result, 'scan_id': scan_id, 'progress': progress})
    # Try loading from file (support both pending and final IDs)
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    filepath = os.path.join(results_dir, scan_id)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'status': 'done', 'result': data, 'scan_id': scan_id, 'progress': 100})
    # If not found, try to find a mapping file for this scan (for pending IDs)
    mapping_path = os.path.join(results_dir, f"{scan_id}.map")
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r', encoding='utf-8') as f:
            final_id = f.read().strip()
        final_path = os.path.join(results_dir, final_id)
        if os.path.exists(final_path):
            with open(final_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'status': 'done', 'result': data, 'scan_id': scan_id, 'progress': 100})
    return jsonify({'error': 'Scan ID not found'}), 404

def run_wordpress_checks(url, save=False):
    results = []
    import requests
    import json
    from datetime import datetime
    from urllib.parse import urlparse
    import os
    import subprocess
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
    wp_dir = os.path.join(os.path.dirname(__file__), 'wordpress')
    check_files = [f for f in os.listdir(wp_dir) if f.startswith('check_') and f.endswith('.py')]
    check_files.sort()
    for check_file in check_files:
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
    if save:
        # Save results to results folder with date and domain in filename
        parsed = urlparse(url)
        domain = parsed.netloc.replace(':', '_')
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"wp_{date_str}_{domain}.json"
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        filepath = os.path.join(results_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'url': url, 'results': results}, f, indent=2)
    return results

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
