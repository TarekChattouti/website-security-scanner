import importlib
import os

def run_all_checks(target, scan_id=None):
    results = []
    check_dir = os.path.dirname(__file__)
    check_files = [f for f in os.listdir(check_dir) if f.startswith('check_') and f.endswith('.py')]
    check_files.sort()
    total = len(check_files)
    for idx, check_file in enumerate(check_files):
        mod_name = f"network_scanner.{check_file[:-3]}"
        mod = importlib.import_module(mod_name)
        try:
            result = mod.run(target)
            results.append(result)
        except Exception as e:
            results.append({'name': check_file, 'status': 'error', 'description': str(e)})
        # --- Progress update ---
        if scan_id:
            try:
                from main import SCAN_STATUS
                if scan_id in SCAN_STATUS:
                    SCAN_STATUS[scan_id]['progress'] = max(1, min(99, int(((idx+1)/total)*100)))
            except Exception:
                pass
    return results
