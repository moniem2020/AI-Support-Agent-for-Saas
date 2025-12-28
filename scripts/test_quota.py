"""Test different models to find one with available quota."""
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models_to_try = [
    "gemini-2.5-flash",
    "gemini-2.5-pro", 
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-exp-1206",
]

print("Testing available models for quota...")
print("=" * 50)

for model_name in models_to_try:
    print(f"\nTrying: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hi")
        print(f"  [SUCCESS] Response: {response.text[:50]}...")
        print(f"\n  >>> WORKING MODEL FOUND: {model_name}")
        break
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            print(f"  [QUOTA EXCEEDED]")
        elif "not found" in error_msg.lower():
            print(f"  [MODEL NOT FOUND]")
        else:
            print(f"  [ERROR] {type(e).__name__}: {error_msg[:80]}")
