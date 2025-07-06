import requests
import importlib
import os
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urlparse
from .utils import safe_request

def run_all_checks(url, scan_id=None):
    results = []
    try:
        resp = safe_request(url)
    except Exception as e:
        return {'error': str(e)}
    # List all check files in the current directory (module's directory)
    check_dir = os.path.dirname(__file__)
    check_files = [f for f in os.listdir(check_dir) if f.startswith('check_') and f.endswith('.py')]
    check_files.sort()  # Ensure order
    total = len(check_files)
    for idx, check_file in enumerate(check_files):
        mod_name = f"website_scanner.{check_file[:-3]}"
        mod = importlib.import_module(mod_name)
        try:
            result = mod.run(url, resp)
        except Exception as e:
            result = {'name': check_file, 'status': 'error', 'description': str(e), 'evidence': None}
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
    parsed = urlparse(url)
    domain = parsed.netloc.replace(':', '_')
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{date_str}_{domain}.json"
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({'url': url, 'results': results}, f, indent=2)
    return {'url': url, 'results': results, 'saved_to': filepath}
