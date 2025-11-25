import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: No API Key found in .env")
else:
    genai.configure(api_key=api_key)  # type: ignore
    print(f"🔑 Checking models for key starting with: {api_key[:5]}...")
    print("\n✅ AVAILABLE MODELS:")
    
    try:
        # Ask Google what models we can use
        for m in genai.list_models():  # type: ignore
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")