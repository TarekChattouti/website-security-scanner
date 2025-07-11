import re
import json
import os
from bs4 import BeautifulSoup

def run(url, resp=None):
    emails = set()
    if resp:
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Extract emails from visible text
        text = soup.get_text()
        emails.update(re.findall(r'[\w\.-]+@[\w\.-]+', text))
        # Extract emails from mailto: links
        for a in soup.find_all('a', href=True):
            if a['href'].startswith('mailto:'):
                mail = a['href'][7:].split('?')[0]
                if re.match(r'^[\w\.-]+@[\w\.-]+$', mail):
                    emails.add(mail)
        # Extract emails from HTML source (comments, scripts, etc.)
        emails.update(re.findall(r'[\w\.-]+@[\w\.-]+', resp.text))
    emails = list(set(emails))
    status = 'fail' if emails else 'pass'
    # Risk: 1 (Info) if only public/marketing emails, 2 (Low) if generic, 3 (Medium) if personal-looking
    risk = 1
    for email in emails:
        if re.search(r'(admin|info|support|contact|sales)', email, re.IGNORECASE):
            risk = max(risk, 2)
        elif re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+', email) and not email.endswith('@example.com'):
            risk = max(risk, 3)
    if not emails:
        risk = 1
        
    # Load guide from help.json
    help_file = os.path.join(os.path.dirname(__file__), 'help.json')
    guide = ""
    try:
        with open(help_file, 'r') as f:
            help_data = json.load(f)
            guide = help_data.get('check_05_detect_emails', '')
    except:
        pass
        
    return {
        'name': 'Detect email addresses on page',
        'status': status,
        'description': 'Detects email addresses in page content, mailto links, and source',
        'evidence': emails,
        'risk': risk,
        'guide': guide
    }
