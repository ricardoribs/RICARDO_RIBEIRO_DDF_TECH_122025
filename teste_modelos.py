import google.generativeai as genai
import os

# COLE SUA CHAVE AQUI PARA TESTAR
GOOGLE_API_KEY = "AIzaSyCb6SgI85CZXs2z5PzS2_mtxVeXJWRvajY" 

genai.configure(api_key=GOOGLE_API_KEY)

print("🔍 Listando modelos disponíveis para sua chave...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Disponível: {m.name}")
except Exception as e:
    print(f"❌ Erro ao listar: {e}")
