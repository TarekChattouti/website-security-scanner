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

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Vulnerability Scan Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #f4f4f4; }
        .pass { background: #e0ffe0; }
        .fail { background: #ffe0e0; }
        .info { background: #e0e7ff; }
        .risk-1 { color: #888; }
        .risk-2 { color: #2d7b2d; }
        .risk-3 { color: #e6a700; }
        .risk-4 { color: #e67e22; }
        .risk-5 { color: #c0392b; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Vulnerability Scan Results</h1>
    <form method="post">
        <input type="text" name="url" placeholder="Enter URL to scan" style="width: 400px;" required>
        <button type="submit">Scan</button>
    </form>
    {% if results %}
    <h2>Results for: {{ url }}</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Description</th>
            <th>Evidence</th>
            <th>Risk</th>
        </tr>
        {% for r in results %}
        <tr class="{{ r.status }} risk-{{ r.risk }}">
            <td>{{ r.name }}</td>
            <td>{{ r.status }}</td>
            <td>{{ r.description }}</td>
            <td><pre style="white-space:pre-wrap;">{{ r.evidence|tojson(indent=2) }}</pre></td>
            <td class="risk-{{ r.risk }}">{{ r.risk }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
</body>
</html>
'''

WORDPRESS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WordPress Scan Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #f4f4f4; }
        .pass { background: #e0ffe0; }
        .fail { background: #ffe0e0; }
        .info { background: #e0e7ff; }
        .risk-1 { color: #888; }
        .risk-2 { color: #2d7b2d; }
        .risk-3 { color: #e6a700; }
        .risk-4 { color: #e67e22; }
        .risk-5 { color: #c0392b; font-weight: bold; }
    </style>
</head>
<body>
    <h1>WordPress Scan Results</h1>
    <form method="post">
        <input type="text" name="url" placeholder="Enter WordPress site URL" style="width: 400px;" required>
        <button type="submit">Scan WordPress</button>
    </form>
    {% if results %}
    <h2>Results for: {{ url }}</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Description</th>
            <th>Evidence</th>
            <th>Risk</th>
        </tr>
        {% for r in results %}
        <tr class="{{ r.status }} risk-{{ r.risk }}">
            <td>{{ r.name }}</td>
            <td>{{ r.status }}</td>
            <td>{{ r.description }}</td>
            <td><pre style="white-space:pre-wrap;">{{ r.evidence|tojson(indent=2) }}</pre></td>
            <td class="risk-{{ r.risk }}">{{ r.risk }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
    <p><a href="/">Back to main scan</a></p>
</body>
</html>
'''

SCAN_STATUS = {}

# Helper: background scan runner
def start_scan(tool, target):
    scan_id = None
    result = None
    pending_id = threading.current_thread().name if threading.current_thread().name.startswith('pending_') else None
    if tool == 'website':
        import os  # Ensure os is imported in this scope
        result = run_all_checks(target)
        scan_id = os.path.basename(result.get('saved_to', ''))
    elif tool == 'wordpress':
        result = run_wordpress_checks(target, save=True)
        scan_id = result.get('scan_id')
    elif tool == 'network':
        result = run_network_checks(target)
        # If result is a list, wrap in dict and add scan_id
        if isinstance(result, list):
            from datetime import datetime
            import os
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = str(target).replace('https://', '').replace('http://', '').split('/')[0].replace(':', '_')
            scan_id_val = f"network_{date_str}_{domain}.json"
            # Save to results folder
            results_dir = os.path.join(os.path.dirname(__file__), 'results')
            os.makedirs(results_dir, exist_ok=True)
            filepath = os.path.join(results_dir, scan_id_val)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({'target': target, 'results': result}, f, indent=2)
            result = {'target': target, 'results': result, 'scan_id': scan_id_val}
            scan_id = scan_id_val
        else:
            scan_id = result.get('scan_id')
    elif tool == 'ssl':
        import os  # Ensure os is available in this scope
        from datetime import datetime
        result = run_ssl_checks(target)
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
            scan_id = result.get('scan_id')
    elif tool == 'subdomain':
        result = run_subfinder_checks(target)
        scan_id = result.get('scan_id')
    if scan_id:
        SCAN_STATUS[scan_id] = {'status': 'done', 'result': result}
        # Save a mapping file from pending_id to scan_id if running in async
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
        if status == 'done' and result and result.get('scan_id'):
            final_id = result['scan_id']
            results_dir = os.path.join(os.path.dirname(__file__), 'results')
            filepath = os.path.join(results_dir, final_id)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return jsonify({'status': 'done', 'result': data, 'scan_id': scan_id})
            else:
                return jsonify({'status': 'done', 'result': result, 'scan_id': scan_id})
        return jsonify({'status': status, 'result': result, 'scan_id': scan_id})
    # Try loading from file (support both pending and final IDs)
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    filepath = os.path.join(results_dir, scan_id)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'status': 'done', 'result': data, 'scan_id': scan_id})
    # If not found, try to find a mapping file for this scan (for pending IDs)
    mapping_path = os.path.join(results_dir, f"{scan_id}.map")
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r', encoding='utf-8') as f:
            final_id = f.read().strip()
        final_path = os.path.join(results_dir, final_id)
        if os.path.exists(final_path):
            with open(final_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'status': 'done', 'result': data, 'scan_id': scan_id})
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

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    url = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            scan = run_all_checks(url)
            results = scan.get('results', [])
    return render_template_string(HTML_TEMPLATE, results=results, url=url)

@app.route('/wordpress', methods=['GET', 'POST'])
def wordpress_scan():
    results = None
    url = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            results = run_wordpress_checks(url)
    return render_template_string(WORDPRESS_TEMPLATE, results=results, url=url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
