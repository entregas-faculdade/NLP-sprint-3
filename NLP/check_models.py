import os
import requests
from dotenv import load_dotenv

load_dotenv()

groq_key = os.getenv("GROQ-API-KEY") or os.getenv("GROQ_API_KEY")
openrouter_key = os.getenv("OPEN-ROUTER-API-KEY") or os.getenv("OPENROUTER_API_KEY")

print("Checking Groq models...")
if groq_key:
    headers = {"Authorization": f"Bearer {groq_key}"}
    resp = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
    if resp.status_code == 200:
        models = resp.json().get("data", [])
        print("Groq available models:")
        for m in models:
            print(f" - {m['id']}")
    else:
        print(f"Groq API Error: {resp.status_code} - {resp.text}")
else:
    print("GROQ API KEY not found in .env")

print("\nChecking OpenRouter free models...")
if openrouter_key:
    headers = {"Authorization": f"Bearer {openrouter_key}"}
    resp = requests.get("https://openrouter.ai/api/v1/models")
    if resp.status_code == 200:
        models = resp.json().get("data", [])
        free_models = []
        for m in models:
            pricing = m.get("pricing", {})
            # Check if pricing is 0 or completely free
            if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
                free_models.append(m["id"])
        
        print(f"OpenRouter available FREE models ({len(free_models)} found):")
        for m in free_models[:15]: # print first 15
            print(f" - {m}")
        if len(free_models) > 15:
            print(" - ... (and more)")
    else:
        print(f"OpenRouter API Error: {resp.status_code} - {resp.text}")
else:
    print("OPEN ROUTER API KEY not found in .env")
