import importlib
import os
import json
from datetime import datetime

def run_all_checks(target):
    results = []
    check_dir = os.path.dirname(__file__)
    check_files = [f for f in os.listdir(check_dir) if f.startswith('check_') and f.endswith('.py')]
    check_files.sort()
    for check_file in check_files:
        mod_name = f"subdomain_finder.{check_file[:-3]}"
        mod = importlib.import_module(mod_name)
        try:
            result = mod.run(target)
        except Exception as e:
            result = {'name': check_file, 'status': 'error', 'description': str(e), 'evidence': None}
        results.append(result)
    # Save results to results folder with date and domain in filename
    domain = target.replace('https://', '').replace('http://', '').split('/')[0].replace(':', '_')
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"subfinder_{date_str}_{domain}.json"
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({'target': target, 'results': results}, f, indent=2)
    return {'target': target, 'results': results, 'saved_to': filepath, 'scan_id': filename}
