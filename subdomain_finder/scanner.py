import importlib
import os
import json
from datetime import datetime

def run_all_checks(target, scan_id=None):
    results = []
    check_dir = os.path.dirname(__file__)
    check_files = [f for f in os.listdir(check_dir) if f.startswith('check_') and f.endswith('.py')]
    check_files.sort()
    total = len(check_files)
    for idx, check_file in enumerate(check_files):
        mod_name = f"subdomain_finder.{check_file[:-3]}"
        mod = importlib.import_module(mod_name)
        try:
            result = mod.run(target)
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
    domain = target.replace('https://', '').replace('http://', '').split('/')[0].replace(':', '_')
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"subfinder_{date_str}_{domain}.json"
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({'target': target, 'results': results}, f, indent=2)
    return {'target': target, 'results': results, 'saved_to': filepath, 'scan_id': filename}
