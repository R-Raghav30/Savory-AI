import urllib.request
import json

url = "http://127.0.0.1:5000/api/explain"
data = json.dumps({"dish_name": "Burrata"}).encode('utf-8')
headers = {'Content-Type': 'application/json'}

req = urllib.request.Request(url, data=data, headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    print("Explanation:", resp.read().decode('utf-8'))
