from Wappalyzer import Wappalyzer, WebPage
from requests_html import HTMLSession

def run(url, resp=None):
    '''Detect website technologies using Wappalyzer'''
    session = HTMLSession()
    try:
        r = session.get(url, timeout=15)
        webpage = WebPage.new_from_response(r)
        wappalyzer = Wappalyzer.latest()
        technologies = wappalyzer.analyze(webpage)
        status = 'pass'
        evidence = list(technologies)
    except Exception as e:
        status = 'fail'
        evidence = str(e)
    risk = 1  # Info only
    return {
        'name': 'Detect website technologies',
        'status': status,
        'description': 'Detects technologies used by the website (Wappalyzer)',
        'evidence': evidence,
        'risk': risk
    }
