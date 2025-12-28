"""Simple test of API key quota."""
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key (last 8 chars): ...{api_key[-8:]}")

genai.configure(api_key=api_key)

print("\nTesting simple generation...")
try:
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    response = model.generate_content("Say hello!")
    print(f"Response: {response.text}")
    print("\n[SUCCESS] API is working!")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
