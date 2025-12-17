"""List available Gemini models."""
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key: {'Set' if api_key else 'MISSING!'}")

genai.configure(api_key=api_key)

print("\nAvailable Models:")
print("=" * 50)
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  {model.name}")
