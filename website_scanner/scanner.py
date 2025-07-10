import importlib
import os
import json
from datetime import datetime
from urllib.parse import urlparse
from scan_db import set_scan_status
import requests

def run_all_checks(url, scan_id=None):
    results = []
    try:
        resp = requests.get(url, timeout=10, verify=False)
    except Exception as e:
        set_scan_status(scan_id, status='error', progress=0, result={'error': str(e)})
        return {'error': str(e)}
    check_dir = os.path.dirname(__file__)
    check_files = [f for f in os.listdir(check_dir) if f.startswith('check_') and f.endswith('.py')]
    check_files.sort()
    total = len(check_files)
    for idx, check_file in enumerate(check_files):
        mod_name = f"website_scanner.{check_file[:-3]}"
        mod = importlib.import_module(mod_name)
        try:
            result = mod.run(url, resp)
        except Exception as e:
            result = {'name': check_file, 'status': 'error', 'description': str(e), 'evidence': None}
        results.append(result)
        if scan_id:
            progress = max(1, min(99, int(((idx+1)/total)*100)))
            set_scan_status(scan_id, progress=progress, result={'url': url, 'results': results[:], 'scan_id': scan_id})
    set_scan_status(scan_id, progress=100, status='done', result={'url': url, 'results': results, 'scan_id': scan_id, 'severity': calculate_average_risk(results)})
    return {'url': url, 'results': results, 'scan_id': scan_id, 'severity': calculate_average_risk(results)}

def calculate_average_risk(results):
    risk_levels = [result.get('risk', 0) for result in results if 'risk' in result]
    if risk_levels:
        return sum(risk_levels) / len(risk_levels)
    return 0


