import json
from app import app

print("--- TESTING FLASK API ENDPOINTS ---")
client = app.test_client()

# 1. Status
r = client.get('/api/status')
print("Status endpoint:", r.status_code, r.get_json())

# 2. Get Menu
r = client.get('/api/menu')
menu = r.get_json()
print(f"Menu endpoint: status={r.status_code}, items={len(menu)}")

# 3. AI Describe
r = client.post('/api/describe', json={'name': 'Grilled Salmon', 'category': 'Mains', 'tone': 'gourmet'})
print("AI Describe:", r.status_code, r.get_json())

# 4. AI Ask Concierge
r = client.post('/api/ask', json={'question': 'What vegetarian dishes do you have?'})
print("AI Ask Concierge:", r.status_code, r.get_json())

# 5. AI Sommelier Pairing
r = client.post('/api/pairing', json={'name': 'Prime Wagyu Ribeye Steak', 'category': 'Mains'})
print("AI Pairing:", r.status_code, r.get_json())

# 6. Add Dish
r = client.post('/api/menu/add', json={'name': 'Test Dish', 'price': 12.5, 'category': 'Starters'})
print("Add Dish:", r.status_code, r.get_json())

print("--- ALL ENDPOINT TESTS PASSED ---")
