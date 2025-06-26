from flask import Flask, request, render_template_string
import json
from website_scanner.scanner import run_all_checks
import importlib
import os
from urllib.parse import urlparse

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

def run_wordpress_checks(url):
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
