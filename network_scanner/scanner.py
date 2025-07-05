import importlib
import os

def run_all_checks(target):
    results = []
    check_dir = os.path.dirname(__file__)
    check_files = [f for f in os.listdir(check_dir) if f.startswith('check_') and f.endswith('.py')]
    check_files.sort()
    for check_file in check_files:
        mod_name = f"network_scanner.{check_file[:-3]}"
        mod = importlib.import_module(mod_name)
        try:
            result = mod.run(target)
            results.append(result)
        except Exception as e:
            results.append({'name': check_file, 'status': 'error', 'description': str(e)})
    return results
