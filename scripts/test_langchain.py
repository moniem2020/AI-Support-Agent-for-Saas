"""Debug the responder's model invocation."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import GOOGLE_API_KEY, MODEL_ROUTING

print("Testing LangChain ChatGoogleGenerativeAI...")
print(f"API Key: ...{GOOGLE_API_KEY[-8:]}")
print(f"MODEL_ROUTING: {MODEL_ROUTING}")

model_name = MODEL_ROUTING["moderate"]
print(f"\nTrying model: {model_name}")

try:
    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3
    )
    
    print("Model created, invoking...")
    response = model.invoke("Say hello!")
    print(f"Response: {response.content}")
    print("\n[SUCCESS] LangChain model works!")
except Exception as e:
    import traceback
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    traceback.print_exc()
