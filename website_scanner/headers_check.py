import requests

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "Referrer-Policy",
    "X-Content-Type-Options",
    "X-Frame-Options"
]

def check_headers(url):
    try:
        res = requests.get(url, timeout=5)
        headers = res.headers
        missing = [h for h in SECURITY_HEADERS if h not in headers]
        return {"missing_headers": missing, "present": list(headers.keys())}
    except Exception as e:
        return {"error": str(e)}
