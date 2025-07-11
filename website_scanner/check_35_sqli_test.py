
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re
import os
import json

def run(url, resp=None):
    '''Test for SQLi via parameter injection (basic, safe)'''
    # Only test GET parameters
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if not query:
        # Load guide from help.json
        help_path = os.path.join(os.path.dirname(__file__), 'help.json')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            guide = help_data.get('check_35_sqli_test', '')
        except Exception:
            guide = ''
        return {
            'name': 'Test for SQLi via parameter injection',
            'status': 'info',
            'description': 'No query parameters to test for SQLi',
            'evidence': None,
            'risk': 1,
            'guide': guide
        }
    sqli_payload = "' OR '1'='1"
    sqli_results = {}
    for param in query:
        test_query = query.copy()
        test_query[param] = [sqli_payload]
        test_url = urlunparse(parsed._replace(query=urlencode(test_query, doseq=True)))
        try:
            r = requests.get(test_url, timeout=7, verify=False)
            # Look for common SQLi error patterns
            error_patterns = [
                'SQL syntax', 'mysql_fetch', 'ORA-01756', 'UNION SELECT',
                'You have an error in your SQL syntax', 'Warning: mysql_',
                'Unclosed quotation mark', 'quoted string not properly terminated',
                'ODBC SQL Server Driver', 'Microsoft OLE DB Provider for SQL Server',
                'PostgreSQL query failed', 'supplied argument is not a valid MySQL',
                'Syntax error', 'Fatal error', 'SQLite3::query', 'PDOException'
            ]
            found = []
            for pattern in error_patterns:
                if re.search(pattern, r.text, re.IGNORECASE):
                    found.append(pattern)
            if found:
                sqli_results[param] = {
                    'test_url': test_url,
                    'errors': found
                }
        except Exception as e:
            sqli_results[param] = {'test_url': test_url, 'error': str(e)}
    status = 'fail' if sqli_results else 'pass'
    # Risk: 5 (Critical) if SQLi found, 1 (Info) if not
    risk = 5 if sqli_results else 1
    # Load guide from help.json
    help_path = os.path.join(os.path.dirname(__file__), 'help.json')
    try:
        with open(help_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
        guide = help_data.get('check_35_sqli_test', '')
    except Exception:
        guide = ''
    return {
        'name': 'Test for SQLi via parameter injection',
        'status': status,
        'description': 'Performs basic SQL injection test on GET parameters',
        'evidence': sqli_results if sqli_results else None,
        'risk': risk,
        'guide': guide
    }
