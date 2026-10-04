import urllib.request
import json

base_url = "http://127.0.0.1:5000"

def test_json(path, data=None):
    try:
        url = base_url + path
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            print(f"=== {path} ===")
            print(resp.read().decode('utf-8')[:300])
            print("\n")
    except Exception as e:
        print(f"FAILED {path}:", e)

print("--- TESTING POWER AI ENDPOINTS ---")
test_json("/api/ai/personal-dining-plan", {"budget": 70, "vibe": "Romantic Date Night", "dietary": "Gluten-Free"})
test_json("/api/ai/dish-sensory-breakdown", {"dish_name": "Prime Wagyu Ribeye Steak"})
test_json("/api/ai/revenue-upsell", {"cart_items": [{"name": "Prime Wagyu Ribeye Steak", "price": 48.50}]})
test_json("/api/ai/marketing-generator", {"dish_name": "Smoked Chocolate Lava Sphere"})
test_json("/api/ai/pricing-optimizer")
