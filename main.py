from flask import Flask, request, render_template_string
import json
import requests
import subprocess
from datetime import datetime
from website_scanner.scanner import run_all_checks as run_website_checks
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
from scan_db import init_db, set_scan_status, get_scan_status
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)


SCAN_STATUS = {}

# Initialize the SQLite database
init_db()

# Helper: background scan runner
def start_scan(tool, target, scan_id=None):
    result = None
    if tool == 'website':
        result = run_website_checks(target, scan_id=scan_id)
    elif tool == 'wordpress':
        result = run_wordpress_checks(target, save=True, scan_id=scan_id)
    elif tool == 'network':
        result = run_network_checks(target, scan_id=scan_id)
    elif tool == 'ssl':
        result = run_ssl_checks(target, scan_id=scan_id)
    elif tool == 'subdomain':
        result = run_subfinder_checks(target, scan_id=scan_id)
    return result


def launch_scan_async(tool, target):
    scan_id = f"pending_{int(time.time()*1000)}_{tool}"
    set_scan_status(scan_id, status='running', progress=1, result=None)
    def runner():
        threading.current_thread().name = scan_id
        result = start_scan(tool, target, scan_id=scan_id)
        if result:
            set_scan_status(scan_id, status='done', progress=100, result=result)
        else:
            set_scan_status(scan_id, status='error', progress=0)
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
    status_row = get_scan_status(scan_id)
    if status_row:
        return jsonify({
            'status': status_row['status'],
            'result': status_row['result'],
            'scan_id': scan_id,
            'progress': status_row['progress']
        })
    return jsonify({'error': 'Scan ID not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
