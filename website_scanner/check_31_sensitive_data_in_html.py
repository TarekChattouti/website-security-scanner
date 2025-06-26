import re
from bs4 import BeautifulSoup
import requests

def run(url, resp=None):
    '''Detect sensitive data (SSNs, card numbers) in HTML'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Detect sensitive data in HTML',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e),
                'risk': 1
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text()
    # US SSN: 3-2-4 digits, not all 0s
    ssn_pattern = r'\b(?!000|666|9\d\d)\d{3}[- ]?(?!00)\d{2}[- ]?(?!0{4})\d{4}\b'
    # Credit card: 13-19 digits, optionally separated by spaces or dashes
    cc_pattern = r'\b(?:\d[ -]*?){13,19}\b'
    ssns = re.findall(ssn_pattern, text)
    ccs = [cc for cc in re.findall(cc_pattern, text) if len(re.sub(r'\D', '', cc)) in [13,14,15,16,17,18,19]]
    found = {'ssns': list(set(ssns)), 'credit_cards': list(set(ccs))}
    status = 'fail' if found['ssns'] or found['credit_cards'] else 'pass'
    # Risk: 5 (Critical) if any SSNs or card numbers found, 1 (Info) if not
    risk = 5 if found['ssns'] or found['credit_cards'] else 1
    return {
        'name': 'Detect sensitive data in HTML',
        'status': status,
        'description': 'Detects SSNs, card numbers in HTML',
        'evidence': found if status == 'fail' else None,
        'risk': risk
    }
