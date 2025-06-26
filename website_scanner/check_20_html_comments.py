from bs4 import BeautifulSoup, Comment
import requests


def run(url, resp=None):
    '''Detect HTML code comments'''
    if resp is None:
        try:
            resp = requests.get(url, timeout=7, verify=False)
        except Exception as e:
            return {
                'name': 'Detect HTML code comments',
                'status': 'error',
                'description': 'Error fetching URL',
                'evidence': str(e)
            }
    soup = BeautifulSoup(resp.text, 'html.parser')
    comments = [comment for comment in soup.find_all(string=lambda text: isinstance(text, Comment))]
    status = 'fail' if comments else 'pass'
    risk = 2 if comments else 1  # Risk: 2 (Low) if comments found, 1 (Info) if not
    return {
        'name': 'Detect HTML code comments',
        'status': status,
        'description': 'Detects HTML comments in page source',
        'evidence': comments[:10] if comments else None,  # Show up to 10 comments
        'risk': risk
    }
