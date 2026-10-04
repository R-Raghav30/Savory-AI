import urllib.request
import json

base_url = "http://127.0.0.1:5000"

def test_endpoint(path, method="GET", data=None):
    try:
        url = base_url + path
        headers = {'Content-Type': 'application/json'} if data else {}
        body = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            print(f"[{method} {path}] -> Status {response.status}")
            return res_body
    except Exception as e:
        print(f"[{method} {path}] FAILED:", e)
        return None

print("--- TESTING SEPARATE HTML PAGES ---")
test_endpoint("/")
test_endpoint("/menu")
test_endpoint("/sommelier")
test_endpoint("/admin")
test_endpoint("/styles.css")

print("\n--- TESTING API ENDPOINTS ---")
test_endpoint("/api/status")
test_endpoint("/api/menu")
test_endpoint("/api/ask", method="POST", data={"question": "What wine goes best with Wagyu steak?"})
