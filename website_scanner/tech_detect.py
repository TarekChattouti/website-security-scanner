import requests
from bs4 import BeautifulSoup

def detect_tech(url):
    tech = []
    try:
        res = requests.get(url, timeout=5)
        headers = res.headers
        html = res.text
        soup = BeautifulSoup(html, "html.parser")
        if "X-Powered-By" in headers:
            tech.append(headers["X-Powered-By"])
        for script in soup.find_all("script", src=True):
            if "jquery" in script["src"]:
                tech.append("jQuery detected in script src")
        return {"tech": tech}
    except Exception as e:
        return {"error": str(e)}
