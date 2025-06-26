from bs4 import BeautifulSoup

def run(url, resp=None):
    mixed = []
    if resp and url.startswith('https://'):
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup.find_all(['img', 'script', 'iframe', 'link', 'video', 'audio', 'source']):
            src = tag.get('src') or tag.get('href')
            if src and src.startswith('http://'):
                mixed.append(src)
    status = 'fail' if mixed else 'pass'
    # Risk: 3 (Medium) for mixed content, 1 (Info) if none
    risk = 3 if mixed else 1
    return {
        'name': 'Detect mixed content (HTTP inside HTTPS)',
        'status': status,
        'description': 'Detects HTTP resources loaded in HTTPS pages',
        'evidence': mixed,
        'risk': risk
    }
