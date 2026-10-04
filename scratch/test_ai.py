import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
TEXT_MODEL = os.getenv("TEXT_MODEL_DEPLOYMENT", "gpt-4.1-mini").strip()

print("Endpoint:", AZURE_OPENAI_ENDPOINT)
print("Text Model:", TEXT_MODEL)

try:
    client = OpenAI(
        base_url=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        default_headers={"api-key": AZURE_OPENAI_API_KEY}
    )
    res = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": "Hello! Say test passed."}]
    )
    print("Response:", res.choices[0].message.content)
except Exception as e:
    print("Standard client failed:", e)
    # Let's try direct REST API or AzureOpenAI if needed
    try:
        from openai import AzureOpenAI
        # Azure OpenAI resource endpoint format: https://<resource>.openai.azure.com/
        base_endpoint = AZURE_OPENAI_ENDPOINT.replace("/openai/v1", "").replace("/v1", "")
        az_client = AzureOpenAI(
            azure_endpoint=base_endpoint,
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-08-01-preview"
        )
        res2 = az_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": "Hello from AzureOpenAI!"}]
        )
        print("AzureOpenAI Response:", res2.choices[0].message.content)
    except Exception as e2:
        print("AzureOpenAI failed:", e2)
