import requests
import time

API_TOKEN = "Rk9vMAd9yebitEuZxAlYcvN3niTm0yOYts9HvbGR96f4a791"
BASE_URL = "https://app.pentest-tools.com/api/v2/scans"
HEADERS_JSON = {
    "accept": "application/json",
    "authorization": f"Bearer {API_TOKEN}"
}
HEADERS_PDF = {
    "accept": "application/pdf",
    "authorization": f"Bearer {API_TOKEN}"
}

def start_scan(target, tool_id):
    data = {
        "target_name": target,
        "tool_id": tool_id
    }
    response = requests.post(BASE_URL, headers=HEADERS_JSON, json=data)
    response.raise_for_status()
    print(response.json())
    return response.json()["data"]["created_id"]

def wait_for_completion(scan_id, timeout=9000, interval=10):
    print(f"Waiting for scan {scan_id} to complete...")
    elapsed = 0
    while elapsed < timeout:
        response = requests.get(f"{BASE_URL}/{scan_id}", headers=HEADERS_JSON)
        response.raise_for_status()
        status = response.json()["data"]["status_name"]
        print(f"Status: {status}")
        if status == "completed":
            return True
        time.sleep(interval)
        elapsed += interval
    raise TimeoutError("Scan did not complete in time.")

def download_report(scan_id):
    response = requests.get(f"{BASE_URL}/{scan_id}/output", headers=HEADERS_PDF)
    if response.status_code == 200:
        with open("scan_report.pdf", "wb") as f:
            f.write(response.content)
        print("PDF report saved as scan_report.pdf")
    else:
        print("Failed to download report:", response.text)

def run_full_scan():
    domain = "http://movieparadise.org"
    tool_id = 170

    try:
        scan_id = 36823024
        print(f"Scan started with ID: {scan_id}")

        if wait_for_completion(scan_id):
            download_report(scan_id)

    except requests.RequestException as e:
        print("Request failed:", e)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    run_full_scan()
