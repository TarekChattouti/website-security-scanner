import json

def run(url, resp=None):
    '''Return parsed WPScan output (do not run WPScan again)'''
    wpscan_data = None
    if resp and hasattr(resp, 'wpscan_output'):
        wpscan_data = resp.wpscan_output
    elif resp and isinstance(resp, dict) and 'wpscan_output' in resp:
        wpscan_data = resp['wpscan_output']
    if not wpscan_data:
        return {
            'name': 'Scan with WPScan (Docker)',
            'status': 'error',
            'description': 'No WPScan output available to parse.',
            'evidence': None,
            'risk': 2
        }
    try:
        data = wpscan_data if isinstance(wpscan_data, dict) else json.loads(wpscan_data)
        if data.get('scan_aborted'):
            status = 'fail'
            description = f"WPScan aborted: {data['scan_aborted']}"
            evidence = {
                'scan_aborted': data['scan_aborted'],
                'target_url': data.get('target_url')
            }
        else:
            status = 'pass'
            description = 'WPScan output parsed successfully'
            evidence = {k: v for k, v in data.items() if k != 'banner'}
    except Exception as e:
        status = 'error'
        description = f'Could not parse WPScan output as JSON: {str(e)}'
        evidence = str(wpscan_data)[:1000]
    return {
        'name': 'Scan with WPScan (Docker)',
        'status': status,
        'description': description,
        'evidence': evidence,
        'risk': 4
    }
