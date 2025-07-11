import requests
import json
import os
import re
from urllib.parse import quote
from .utils import safe_request

def query_nvd_api(product, version):
    # NVD API v2 endpoint
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    # NVD expects CPE format, but we'll use keyword search for simplicity
    params = {
        "keywordSearch": f"{product} {version}",
        "resultsPerPage": 5
    }
    try:
        # Use regular requests for NVD API (different domain)
        resp = requests.get(base_url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            cves = []
            for item in data.get("vulnerabilities", []):
                cve_id = item.get("cve", {}).get("id", "")
                desc = item.get("cve", {}).get("descriptions", [{}])[0].get("value", "")
                cves.append({"id": cve_id, "desc": desc})
            return cves
    except Exception as e:
        return [{"id": "NVD API error", "desc": str(e)}]
    return []

def run(url, resp=None):
    '''Check for server-side software vulnerabilities (CVE) using NVD API'''
    server = resp.headers.get('Server') if resp else None
    x_powered = resp.headers.get('X-Powered-By') if resp else None
    evidence = {'Server': server, 'X-Powered-By': x_powered}
    vulnerable = False
    cve_info = []
    nvd_cves = []
    patterns = [
        (r'Apache/(\d+\.\d+\.\d+)', 'Apache'),
        (r'nginx/(\d+\.\d+\.\d+)', 'nginx'),
        (r'PHP/(\d+\.\d+\.\d+)', 'PHP'),
        (r'OpenSSL/(\d+\.\d+\.\d+[a-z]*)', 'OpenSSL'),
        (r'IIS/(\d+\.\d+)', 'IIS'),
        (r'LiteSpeed/(\d+\.\d+\.\d+)', 'LiteSpeed'),
        (r'Microsoft-HTTPAPI/(\d+\.\d+)', 'Microsoft-HTTPAPI'),
        (r'Tomcat/(\d+\.\d+\.\d+)', 'Tomcat'),
        (r'Jetty/(\d+\.\d+\.\d+)', 'Jetty'),
        (r'Node\\.js/(\d+\.\d+\.\d+)', 'Node.js'),
        (r'Express/(\d+\.\d+\.\d+)', 'Express'),
        (r'gunicorn/(\d+\.\d+\.\d+)', 'gunicorn'),
        (r'Werkzeug/(\d+\.\d+\.\d+)', 'Werkzeug'),
        (r'Python/(\d+\.\d+\.\d+)', 'Python'),
        (r'Ruby/(\d+\.\d+\.\d+)', 'Ruby'),
        (r'Perl/(\d+\.\d+\.\d+)', 'Perl'),
        (r'Caddy/(\d+\.\d+\.\d+)', 'Caddy'),
        (r'GWS/(\d+\.\d+)', 'GWS'),
        (r'cloudflare', 'Cloudflare'),  # No version, but can still flag
    ]
    headers = f"{server or ''} {x_powered or ''}"
    found_software = False
    for pattern, name in patterns:
        m = re.search(pattern, headers)
        if m:
            found_software = True
            # Only use group(1) if the pattern has a capturing group
            if m.lastindex:
                version = m.group(1)
                nvd_cves = query_nvd_api(name, version)
                if nvd_cves:
                    vulnerable = True
                    cve_info.append(f"{name} {version} - CVEs found: {[c['id'] for c in nvd_cves]}")
                else:
                    cve_info.append(f"{name} {version} - No CVEs found in NVD.")
            else:
                # No version, just use the name
                nvd_cves = query_nvd_api(name, "")
                if nvd_cves:
                    vulnerable = True
                    cve_info.append(f"{name} - CVEs found: {[c['id'] for c in nvd_cves]}")
                else:
                    cve_info.append(f"{name} - No CVEs found in NVD.")
            break
    if not found_software:
        cve_info.append('No recognizable server software/version found in headers.')
    status = 'fail' if vulnerable else 'pass'
    risk = 5 if vulnerable else 1
    evidence['cve_info'] = cve_info
    if nvd_cves:
        evidence['nvd_cves'] = nvd_cves
        
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_08_cve_server_software', '')
    except:
        pass
        
    return {
        'name': 'Check for server-side software vulnerabilities (CVE)',
        'status': status,
        'description': 'Checks for known CVEs in server software using the NVD API',
        'evidence': evidence,
        'risk': risk,
        'guide': guide
    }
