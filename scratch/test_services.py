import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("--- TESTING AZURE SERVICES ---")

# 1. OpenAI Text & Vision & Image
azure_ep = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_key = os.getenv("AZURE_OPENAI_API_KEY")
text_model = os.getenv("TEXT_MODEL_DEPLOYMENT")
vision_model = os.getenv("VISION_MODEL_DEPLOYMENT")
image_model = os.getenv("IMAGE_MODEL_DEPLOYMENT")

print(f"OpenAI Endpoint: {azure_ep}")
client = OpenAI(base_url=azure_ep, api_key=azure_key)

try:
    res = client.chat.completions.create(
        model=text_model,
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("Text model OK:", res.choices[0].message.content)
except Exception as e:
    print("Text model ERR:", e)

# 2. Azure Speech TTS
speech_key = os.getenv("SPEECH_API_KEY")
speech_region = os.getenv("SPEECH_REGION")

if speech_key and speech_region:
    tts_url = f"https://{speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": speech_key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
        "User-Agent": "RestaurantMenuAI"
    }
    ssml = "<speak version='1.0' xml:lang='en-US'><voice xml:lang='en-US' name='en-US-JennyNeural'>Welcome to Palate Intelligence.</voice></speak>"
    try:
        r = requests.post(tts_url, headers=headers, data=ssml.encode("utf-8"))
        print(f"Speech TTS Status: {r.status_code}, length: {len(r.content)} bytes")
    except Exception as e:
        print("Speech TTS ERR:", e)

print("--- TEST COMPLETE ---")
