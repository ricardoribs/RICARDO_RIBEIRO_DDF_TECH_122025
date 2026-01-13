import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Erro: Chave não encontrada no .env")
else:
    genai.configure(api_key=api_key)
    print("🔍 Listando modelos disponíveis para sua chave:")
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"❌ Erro ao listar: {e}")
