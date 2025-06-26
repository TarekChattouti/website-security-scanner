import requests
from urllib.parse import urljoin

def run(url, resp=None):
    '''Discovery of exposed API endpoints (/api, /v1, etc.)'''
    api_paths = [
        'api/', 'api/v1/', 'api/v2/', 'v1/', 'v2/', 'rest/', 'graphql', 'openapi', 'swagger',
        'api.php', 'api.json', 'api/v1/openapi.json', 'api/v1/swagger.json', 'v1/openapi.json', 'v1/swagger.json'
    ]
    found = {}
    for path in api_paths:
        test_url = urljoin(url, '/' + path)
        try:
            r = requests.get(test_url, timeout=5, verify=False)
            if r.status_code == 200 and r.text.strip():
                found[test_url] = r.text[:500]  # Show a preview
            elif r.status_code == 401:
                found[test_url] = '401 Unauthorized (endpoint exists)'
            elif r.status_code == 403:
                found[test_url] = '403 Forbidden (endpoint exists)'
        except Exception as e:
            continue
    status = 'fail' if found else 'pass'
    # Risk: 3 (Medium) if exposed API endpoint, 1 (Info) if not
    risk = 3 if found else 1
    return {
        'name': 'Discovery of exposed API endpoints',
        'status': status,
        'description': 'Detects exposed API endpoints (e.g., /api, /v1, /graphql)',
        'evidence': found if found else None,
        'risk': risk
    }
