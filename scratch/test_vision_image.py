import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
TEXT_MODEL = os.getenv("TEXT_MODEL_DEPLOYMENT", "gpt-4.1-mini").strip()
VISION_MODEL = os.getenv("VISION_MODEL_DEPLOYMENT", "gpt-4.1-mini").strip()
IMAGE_MODEL = os.getenv("IMAGE_MODEL_DEPLOYMENT", "FLUX-1.1-pro").strip()

client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    default_headers={"api-key": AZURE_OPENAI_API_KEY}
)

print("Testing Vision Model...")
try:
    res_v = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": "Describe a gourmet pizza in 5 words."}]
    )
    print("Vision Model output:", res_v.choices[0].message.content)
except Exception as e:
    print("Vision Model test error:", e)

print("\nTesting Image Model...")
try:
    res_i = client.images.generate(
        model=IMAGE_MODEL,
        prompt="Gourmet woodfired truffle pizza on dark marble background",
        n=1
    )
    print("Image Model response:", res_i)
except Exception as e:
    print("Image Model test error:", e)
