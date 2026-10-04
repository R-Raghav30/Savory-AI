import base64
import json
import os
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from openai import OpenAI

# ============================================================
# LOAD ENVIRONMENT VARIABLES (DO NOT MODIFY ENV KEYS)
# ============================================================

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "").strip()

TEXT_MODEL = os.getenv("TEXT_MODEL_DEPLOYMENT", "gpt-4.1-mini").strip()
VISION_MODEL = os.getenv("VISION_MODEL_DEPLOYMENT", "gpt-4.1-mini").strip()
IMAGE_MODEL = os.getenv("IMAGE_MODEL_DEPLOYMENT", "FLUX-1.1-pro").strip()

SPEECH_ENDPOINT = os.getenv("SPEECH_ENDPOINT", "").strip()
SPEECH_API_KEY = os.getenv("SPEECH_API_KEY", "").strip()
SPEECH_REGION = os.getenv("SPEECH_REGION", "eastus").strip()

AI_ENABLED = bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY)

# ============================================================
# AZURE OPENAI CLIENT
# ============================================================

client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    default_headers={"api-key": AZURE_OPENAI_API_KEY}
) if AI_ENABLED else None

# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__, template_folder=".", static_folder=".")

# ============================================================
# INITIAL IN-MEMORY RESTAURANT MENU
# ============================================================

MENU = [
    {
        "id": 1,
        "name": "Truffle Burrata & Heirloom Tomatoes",
        "category": "Starters",
        "price": 16.50,
        "calories": 420,
        "dietary": ["Vegetarian", "Gluten-Free"],
        "description": "Creamy Italian burrata cheese infused with white truffle oil, served alongside vine-ripened heirloom tomatoes, aged balsamic reduction, and fresh basil.",
        "pairing": "Crisp Sauvignon Blanc or Sparkling Prosecco",
        "image_url": "https://images.unsplash.com/photo-1592417817098-8f3d69201944?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": 2,
        "name": "Pan-Seared Chilean Sea Bass",
        "category": "Mains",
        "price": 38.00,
        "calories": 580,
        "dietary": ["Gluten-Free", "Chef Special"],
        "description": "Sustainably caught sea bass with crispy golden skin over saffron risotto, roasted baby carrots, and lemon-herb butter sauce.",
        "pairing": "Chablis or Oaked Chardonnay",
        "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": 3,
        "name": "Prime Wagyu Ribeye Steak",
        "category": "Mains",
        "price": 48.50,
        "calories": 820,
        "dietary": ["Chef Special"],
        "description": "10oz Wagyu ribeye steak grilled over oak charcoal, topped with rich bone marrow butter, served with roasted garlic potatoes and asparagus.",
        "pairing": "Cabernet Sauvignon or Aged Pinot Noir",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": 4,
        "name": "Charred Fiery Paneer Tikka",
        "category": "Starters",
        "price": 14.00,
        "calories": 390,
        "dietary": ["Vegetarian", "Spicy"],
        "description": "Cottage cheese cubes marinated in Kashmiri chili, yogurt, and warm spices, roasted in a clay tandoor oven with fresh mint chutney.",
        "pairing": "Riesling or Craft Amber Ale",
        "image_url": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": 5,
        "name": "Artisanal Wild Mushroom Gnocchi",
        "category": "Mains",
        "price": 24.00,
        "calories": 510,
        "dietary": ["Vegetarian"],
        "description": "Soft handmade potato gnocchi tossed with wild chanterelles, porcini mushroom cream, toasted pine nuts, and shaved parmesan.",
        "pairing": "Pinot Noir or Nebbiolo",
        "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": 6,
        "name": "Smoked Chocolate Lava Sphere",
        "category": "Desserts",
        "price": 12.50,
        "calories": 490,
        "dietary": ["Vegetarian"],
        "description": "Rich Valrhona dark chocolate dome melted table-side with warm caramel, vanilla gelato, and hazelnut crumbles.",
        "pairing": "Vintage Port or Espresso Martini",
        "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": 7,
        "name": "Smoked Rosemary Old Fashioned",
        "category": "Beverages",
        "price": 15.00,
        "calories": 180,
        "dietary": ["Vegan", "Gluten-Free"],
        "description": "Kentucky bourbon, charred rosemary syrup, Angostura bitters, served over a crystal ice sphere.",
        "pairing": "Pairs perfectly with Prime Wagyu Ribeye",
        "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=600&q=80"
    },
    {
        "id": 8,
        "name": "Spiced Mango Dragonfruit Elixir",
        "category": "Beverages",
        "price": 8.50,
        "calories": 120,
        "dietary": ["Vegan", "Gluten-Free", "Non-Alcoholic"],
        "description": "Fresh Alphonso mango puree, pink dragonfruit, lime juice, elderflower tonic, and crushed mint.",
        "pairing": "Refreshing companion for spicy starters",
        "image_url": "https://images.unsplash.com/photo-1546171753-97d7676e4602?auto=format&fit=crop&w=600&q=80"
    }
]

def get_next_id():
    if not MENU:
        return 1
    return max(item["id"] for item in MENU) + 1

# ============================================================
# AZURE OPENAI HELPER
# ============================================================

def chat(system_prompt, user_prompt, model=TEXT_MODEL, temperature=0.7):
    if not AI_ENABLED or client is None:
        raise RuntimeError("Azure OpenAI API is not configured.")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature
    )
    return response.choices[0].message.content

# ============================================================
# HTML PAGE ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/menu")
def menu_page():
    return render_template("menu.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/sommelier")
def sommelier_page():
    return render_template("sommelier.html")

@app.route("/styles.css")
def serve_styles():
    return send_file("styles.css", mimetype="text/css")

# ============================================================
# BASIC API ENDPOINTS
# ============================================================

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "ai_enabled": AI_ENABLED,
        "text_model": TEXT_MODEL,
        "vision_model": VISION_MODEL,
        "image_model": IMAGE_MODEL,
        "speech_configured": bool(SPEECH_API_KEY and SPEECH_REGION),
        "menu_items_count": len(MENU)
    })

@app.route("/api/menu", methods=["GET"])
def get_menu():
    return jsonify(MENU)

@app.route("/api/menu/add", methods=["POST"])
def add_menu_item():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Dish name is required."}), 400

    new_item = {
        "id": get_next_id(),
        "name": name,
        "category": data.get("category", "Mains").strip() or "Mains",
        "price": float(data.get("price", 15.0)),
        "calories": int(data.get("calories", 450)),
        "dietary": data.get("dietary", []),
        "description": data.get("description", "").strip() or f"Chef's specialty {name} prepared with fresh seasonal ingredients.",
        "pairing": data.get("pairing", "").strip() or "Recommended with house wine or artisanal cocktail.",
        "image_url": data.get("image_url", "").strip() or "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"
    }

    MENU.append(new_item)
    return jsonify({"success": True, "item": new_item}), 201

@app.route("/api/menu/<int:dish_id>", methods=["PUT"])
def update_menu_item(dish_id):
    data = request.get_json(silent=True) or {}
    for item in MENU:
        if item["id"] == dish_id:
            item["name"] = data.get("name", item["name"])
            item["category"] = data.get("category", item["category"])
            item["price"] = float(data.get("price", item["price"]))
            item["calories"] = int(data.get("calories", item["calories"]))
            item["dietary"] = data.get("dietary", item["dietary"])
            item["description"] = data.get("description", item["description"])
            item["pairing"] = data.get("pairing", item["pairing"])
            if "image_url" in data and data["image_url"].strip():
                item["image_url"] = data["image_url"].strip()
            return jsonify({"success": True, "item": item})
    return jsonify({"error": "Dish not found."}), 404

@app.route("/api/menu/<int:dish_id>", methods=["DELETE"])
def delete_menu_item(dish_id):
    global MENU
    original_len = len(MENU)
    MENU = [item for item in MENU if item["id"] != dish_id]
    if len(MENU) < original_len:
        return jsonify({"success": True, "message": f"Dish #{dish_id} removed."})
    return jsonify({"error": "Dish not found."}), 404

# ============================================================
# CUSTOMER AI FEATURE 1: PERSONALIZED DINING TASTE PROFILER
# ============================================================

@app.route("/api/ai/personal-dining-plan", methods=["POST"])
def personal_dining_plan():
    data = request.get_json(silent=True) or {}
    budget = float(data.get("budget", 60.0))
    dietary_pref = data.get("dietary", "Any").strip()
    vibe = data.get("vibe", "Romantic Dinner").strip()
    max_calories = int(data.get("max_calories", 1200))

    if not AI_ENABLED:
        return jsonify({
            "plan_name": "Chef's Signature Tasting Plan",
            "items": [MENU[0]["name"], MENU[2]["name"], MENU[5]["name"]],
            "total_price": 77.50,
            "total_calories": 1730,
            "reasoning": "A balanced gourmet dining experience featuring our finest Wagyu steak and Truffle Burrata.",
            "demo": True
        })

    try:
        sys_prompt = (
            "You are an AI Master Culinary Sommelier & Personal Dining Planner.\n"
            "Select 2 to 4 items from the active menu below to create the PERFECT dining menu for a guest.\n"
            "Respond ONLY in valid JSON with format:\n"
            "{\n"
            '  "plan_name": "Short Creative Menu Title",\n'
            '  "items": ["Dish Name 1", "Dish Name 2"],\n'
            '  "total_price": 45.00,\n'
            '  "total_calories": 950,\n'
            '  "reasoning": "Clear 2-sentence explanation in English why this combination perfectly matches the guest preference."\n'
            "}\n\n"
            f"ACTIVE MENU:\n{json.dumps(MENU, indent=2)}"
        )
        user_prompt = f"Guest Request:\nBudget: ${budget}\nDietary Preference: {dietary_pref}\nDining Vibe: {vibe}\nMax Calories: {max_calories} kcal"
        
        raw = chat(sys_prompt, user_prompt, temperature=0.5)

        if raw.startswith("```json"): raw = raw[7:]
        elif raw.startswith("```"): raw = raw[3:]
        if raw.endswith("```"): raw = raw[:-3]

        parsed = json.loads(raw.strip())
        return jsonify({"success": True, "plan": parsed})
    except Exception as e:
        return jsonify({"error": f"Failed to generate dining plan: {str(e)}"}), 500

# ============================================================
# CUSTOMER AI FEATURE 2: SENSORY TASTE & FLAVOR PROFILE RADAR
# ============================================================

@app.route("/api/ai/dish-sensory-breakdown", methods=["POST"])
def sensory_breakdown():
    data = request.get_json(silent=True) or {}
    dish_name = data.get("dish_name", "").strip()

    if not dish_name:
        return jsonify({"error": "Dish name is required."}), 400

    dish_info = next((d for d in MENU if d["name"].lower() == dish_name.lower()), None)
    if not dish_info:
        dish_info = {"name": dish_name, "description": "Artisanal gourmet creation."}

    if not AI_ENABLED:
        return jsonify({
            "umami": 9, "richness": 8, "spice": 2, "sweetness": 3, "acidity": 5, "crunch": 6,
            "sensory_notes": "Rich, creamy, highly savory with subtle earthy truffle undertones.",
            "demo": True
        })

    try:
        sys_prompt = (
            "You are an expert Flavor Scientist and Sensory Sommelier.\n"
            "Analyze the given dish and return a JSON object evaluating flavor scores (out of 10) and sensory notes in clear English.\n"
            "Return ONLY valid JSON with keys: umami, richness, spice, sweetness, acidity, crunch, sensory_notes."
        )
        raw = chat(sys_prompt, f"Analyze dish: {json.dumps(dish_info)}", temperature=0.3)
        if raw.startswith("```json"): raw = raw[7:]
        elif raw.startswith("```"): raw = raw[3:]
        if raw.endswith("```"): raw = raw[:-3]
        return jsonify({"success": True, "sensory": json.loads(raw.strip())})
    except Exception as e:
        return jsonify({"error": f"Sensory analysis failed: {str(e)}"}), 500

# ============================================================
# CLIENT (RESTAURANT OWNER) AI FEATURE 1: HIGH-MARGIN REVENUE UPSELL ENGINE
# ============================================================

@app.route("/api/ai/revenue-upsell", methods=["POST"])
def revenue_upsell():
    data = request.get_json(silent=True) or {}
    cart_items = data.get("cart_items", [])

    if not cart_items:
        return jsonify({"error": "Cart items required."}), 400

    if not AI_ENABLED:
        return jsonify({
            "upsell_item": "Smoked Rosemary Old Fashioned",
            "pitch": "Pair your Wagyu Ribeye with our house Smoked Rosemary Old Fashioned to elevate your dining experience!",
            "additional_revenue": 15.00,
            "demo": True
        })

    try:
        sys_prompt = (
            "You are a top Restaurant Revenue Management AI.\n"
            "Analyze the customer's active order and suggest ONE high-margin drink, starter, or dessert from the menu to boost Average Order Value (AOV).\n"
            "Return ONLY valid JSON with keys:\n"
            '- "upsell_item": name of suggested menu dish/drink\n'
            '- "pitch": 1 irresistible sentence pitching the upsell to the customer in English\n'
            '- "added_value": numeric price of upsell\n\n'
            f"ACTIVE MENU:\n{json.dumps(MENU, indent=2)}"
        )
        user_prompt = f"Active Customer Cart:\n{json.dumps(cart_items, indent=2)}"
        raw = chat(sys_prompt, user_prompt, temperature=0.5)

        if raw.startswith("```json"): raw = raw[7:]
        elif raw.startswith("```"): raw = raw[3:]
        if raw.endswith("```"): raw = raw[:-3]

        return jsonify({"success": True, "upsell": json.loads(raw.strip())})
    except Exception as e:
        return jsonify({"error": f"Revenue upsell failed: {str(e)}"}), 500

# ============================================================
# CLIENT AI FEATURE 2: INSTANT SOCIAL MEDIA & MARKETING AD GENERATOR
# ============================================================

@app.route("/api/ai/marketing-generator", methods=["POST"])
def marketing_generator():
    data = request.get_json(silent=True) or {}
    dish_name = data.get("dish_name", "").strip()

    if not dish_name:
        return jsonify({"error": "Dish name is required."}), 400

    dish_info = next((d for d in MENU if d["name"].lower() == dish_name.lower()), {"name": dish_name, "description": "Signature dish."})

    if not AI_ENABLED:
        return jsonify({
            "instagram_caption": "🔥 Craving perfection? Try our Prime Wagyu Ribeye Steak tonight! Grilled over oak charcoal with bone marrow butter. #GourmetDining #Wagyu #Foodie",
            "tiktok_script": "Hook: 'You won't believe how tender this Wagyu ribeye is...' [Show sizzle shot, pour garlic butter]",
            "google_post": "Join us this weekend for our Chef Special Wagyu Ribeye paired with vintage Cabernet. Reserve your table now!",
            "demo": True
        })

    try:
        sys_prompt = (
            "You are a World-Class Restaurant Social Media Marketing Agency.\n"
            "Create high-converting social media marketing posts for the given dish in clear, catchy English.\n"
            "Return ONLY valid JSON with keys:\n"
            '- "instagram_caption": (engaging caption with trending hashtags)\n'
            '- "tiktok_script": (short 15-second viral video script concept)\n'
            '- "google_post": (professional promotional update for Google Maps/Business)\n'
        )
        user_prompt = f"Generate marketing campaign for dish: {json.dumps(dish_info)}"
        raw = chat(sys_prompt, user_prompt, temperature=0.7)

        if raw.startswith("```json"): raw = raw[7:]
        elif raw.startswith("```"): raw = raw[3:]
        if raw.endswith("```"): raw = raw[:-3]

        return jsonify({"success": True, "marketing": json.loads(raw.strip())})
    except Exception as e:
        return jsonify({"error": f"Marketing generation failed: {str(e)}"}), 500

# ============================================================
# CLIENT AI FEATURE 3: MENU PRICING & PROFIT OPTIMIZER
# ============================================================

@app.route("/api/ai/pricing-optimizer", methods=["POST"])
def pricing_optimizer():
    if not AI_ENABLED:
        return jsonify({
            "recommendations": [
                {"dish": "Smoked Chocolate Lava Sphere", "current_price": 12.50, "suggested_price": 14.50, "reason": "High demand dessert with strong perceived luxury value."},
                {"dish": "Charred Fiery Paneer Tikka", "current_price": 14.00, "suggested_price": 15.50, "reason": "Popular vegetarian starter with high margin potential."}
            ],
            "demo": True
        })

    try:
        sys_prompt = (
            "You are an expert Restaurant Revenue & Profit Optimization Consultant.\n"
            "Analyze the active menu items and return JSON recommendations to optimize pricing and maximize restaurant profitability.\n"
            "Return ONLY a JSON object with key 'recommendations': array of objects containing 'dish', 'current_price', 'suggested_price', and 'reason' in clear English."
        )
        raw = chat(sys_prompt, f"Analyze active menu: {json.dumps(MENU, indent=2)}", temperature=0.4)

        if raw.startswith("```json"): raw = raw[7:]
        elif raw.startswith("```"): raw = raw[3:]
        if raw.endswith("```"): raw = raw[:-3]

        return jsonify({"success": True, "data": json.loads(raw.strip())})
    except Exception as e:
        return jsonify({"error": f"Pricing optimizer failed: {str(e)}"}), 500

# ============================================================
# EXISTING AI ENDPOINTS (CONCIERGE, PAIRING, EXPLAIN, SCAN, DESCRIBE)
# ============================================================

@app.route("/api/describe", methods=["POST"])
def describe():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    category = data.get("category", "Main").strip()
    tone = data.get("tone", "gourmet").strip().lower()

    if not name:
        return jsonify({"error": "Dish name is required."}), 400

    if not AI_ENABLED:
        return jsonify({
            "description": f"Exquisite {name} ({category}), masterfully crafted with fresh ingredients for an unforgettable dining experience.",
            "demo": True
        })

    tone_prompts = {
        "gourmet": "Write a sophisticated, fine-dining menu description in simple, mouthwatering English focusing on sensory notes and premium ingredients.",
        "casual": "Write a warm, friendly, simple menu description in clear English.",
        "punchy": "Write a short 1-sentence menu description in clear English.",
        "story": "Write a charming origin story description in clear English."
    }

    selected_prompt = tone_prompts.get(tone, tone_prompts["gourmet"])

    try:
        sys_msg = (
            f"You are an expert restaurant menu copywriter.\n"
            f"{selected_prompt}\n"
            f"Respond strictly in clear English. Keep under 30 words. No quotes."
        )
        text = chat(sys_msg, f"Dish Name: {name}\nCategory: {category}", temperature=0.7)
        return jsonify({"description": text, "tone": tone, "demo": False})
    except Exception as e:
        return jsonify({"error": f"Description service error: {str(e)}"}), 500

@app.route("/api/explain", methods=["POST"])
def explain_dish():
    data = request.get_json(silent=True) or {}
    dish_name = data.get("dish_name", "").strip()

    if not dish_name:
        return jsonify({"error": "Dish name is required."}), 400

    if not AI_ENABLED:
        return jsonify({
            "explanation": f"{dish_name} is a delicious restaurant dish prepared with fresh seasonal ingredients.",
            "demo": True
        })

    try:
        system_prompt = (
            "You are a friendly dining guide.\n"
            "Explain what the given dish or culinary term is in plain, simple, easy-to-understand English.\n"
            "Keep response under 50 words. Strict English only."
        )
        text = chat(system_prompt, f"Explain this dish/term in simple English: {dish_name}", temperature=0.5)
        return jsonify({"explanation": text, "demo": False})
    except Exception as e:
        return jsonify({"error": f"Explanation failed: {str(e)}"}), 500

@app.route("/api/scan", methods=["POST"])
def scan_menu():
    if "file" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected."}), 400

    if not AI_ENABLED:
        return jsonify({"error": "Azure OpenAI Vision connection is required."}), 503

    try:
        image_bytes = file.read()
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime = file.mimetype or "image/jpeg"

        prompt = """
You are an expert AI OCR Restaurant Data Parser. Extract all food and drink items visible in this menu image.
Convert and write all dish names, categories, and descriptions strictly into clear English.

Return ONLY a valid JSON array of objects.
Each object MUST have:
- name: string (name of dish in clear English)
- category: string ("Starters", "Mains", "Desserts", or "Beverages")
- price: number (numeric price e.g. 18.5)
- calories: number (estimated calories e.g. 450)
- dietary: array of strings (e.g. ["Vegetarian"], ["Gluten-Free"], ["Spicy"], or [])
- description: string (simple English description)
- pairing: string (suggested beverage pairing in English)
"""

        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"}
                        }
                    ]
                }
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```json"): raw = raw[7:]
        elif raw.startswith("```"): raw = raw[3:]
        if raw.endswith("```"): raw = raw[:-3]
        raw = raw.strip()

        parsed_items = json.loads(raw)
        if not isinstance(parsed_items, list):
            return jsonify({"error": "Vision model did not return a valid list.", "raw": raw}), 422

        newly_added = []
        for item in parsed_items:
            if not isinstance(item, dict) or not item.get("name"):
                continue

            menu_entry = {
                "id": get_next_id(),
                "name": str(item.get("name", "Scanned Dish")),
                "category": str(item.get("category", "Mains")),
                "price": float(item.get("price", 14.0)),
                "calories": int(item.get("calories", 450)),
                "dietary": item.get("dietary", []) if isinstance(item.get("dietary"), list) else [],
                "description": str(item.get("description", "Freshly extracted from physical menu scan.")),
                "pairing": str(item.get("pairing", "House Sommelier Selection")),
                "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"
            }
            MENU.append(menu_entry)
            newly_added.append(menu_entry)

        return jsonify({
            "success": True,
            "extracted_count": len(newly_added),
            "items": newly_added
        })

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse JSON from Vision model.", "raw": raw}), 422
    except Exception as e:
        return jsonify({"error": f"Menu scan failed: {str(e)}"}), 500

@app.route("/api/ask", methods=["POST"])
def ask_concierge():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required."}), 400

    if not AI_ENABLED:
        return jsonify({
            "answer": "Welcome! I recommend starting with our Truffle Burrata & Heirloom Tomatoes, followed by the Prime Wagyu Ribeye Steak paired with Cabernet Sauvignon.",
            "demo": True
        })

    try:
        menu_summary = json.dumps(MENU, indent=2)
        system_prompt = (
            "You are an expert restaurant Head Concierge & Sommelier.\n"
            "Help guests choose dishes, answer dietary questions, recommend pairings, and suggest multi-course meals.\n"
            "Reference exact items, prices, and dietary tags from the active menu provided below.\n"
            "Always respond strictly in clear, natural, mouthwatering English.\n"
            "Be polite, appetizing, helpful, and concise (under 100 words).\n\n"
            f"ACTIVE RESTAURANT MENU:\n{menu_summary}"
        )

        answer = chat(system_prompt, question, temperature=0.7)
        return jsonify({"answer": answer, "demo": False})
    except Exception as e:
        return jsonify({"error": f"Concierge service error: {str(e)}"}), 500

@app.route("/api/pairing", methods=["POST"])
def recommend_pairing():
    data = request.get_json(silent=True) or {}
    dish_name = data.get("name", "").strip()

    if not dish_name:
        return jsonify({"error": "Dish name is required."}), 400

    if not AI_ENABLED:
        return jsonify({
            "pairing": f"For {dish_name}, we recommend a crisp Pinot Grigio or an artisanal Craft Amber Ale.",
            "demo": True
        })

    try:
        system_prompt = (
            "You are a Master Sommelier and Mixologist.\n"
            "Provide 1 ideal wine pairing, 1 craft beer pairing, and 1 non-alcoholic/mocktail pairing for the given dish.\n"
            "Always respond strictly in clear English with emojis under 40 words total."
        )
        pairing_text = chat(system_prompt, f"Dish: {dish_name}", temperature=0.7)
        return jsonify({"pairing": pairing_text, "demo": False})
    except Exception as e:
        return jsonify({"error": f"Pairing service error: {str(e)}"}), 500

@app.route("/api/allergen-check", methods=["POST"])
def allergen_check():
    data = request.get_json(silent=True) or {}
    allergy = data.get("allergy", "").strip()
    dish_name = data.get("dish_name", "").strip()

    if not allergy or not dish_name:
        return jsonify({"error": "Allergy and dish name are required."}), 400

    if not AI_ENABLED:
        return jsonify({
            "safe": True,
            "analysis": f"Based on our recipe index for {dish_name}, it does not typically contain {allergy}. Always inform your server.",
            "demo": True
        })

    try:
        dish_info = next((d for d in MENU if d["name"].lower() == dish_name.lower()), {"name": dish_name})
        system_prompt = (
            "You are a clinical culinary allergen expert.\n"
            "Analyze if the given dish is safe for someone with the specified allergy or restriction.\n"
            "Always respond strictly in clear English under 50 words."
        )
        user_prompt = f"Dish: {json.dumps(dish_info)}\nCustomer Restriction/Allergy: {allergy}"
        result = chat(system_prompt, user_prompt, temperature=0.3)
        return jsonify({"analysis": result, "demo": False})
    except Exception as e:
        return jsonify({"error": f"Allergen check error: {str(e)}"}), 500

# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    print("Starting Intelligent Restaurant Menu Backend (Full Power AI)...")
    print(f"Azure OpenAI Connected: {AI_ENABLED}")
    app.run(debug=True, host="127.0.0.1", port=5000)