import google.generativeai as genai
import os

# Quando for testar
GOOGLE_API_KEY = "teste aqui sua chave, não esqueça de apagar e não commitar"

genai.configure(api_key=GOOGLE_API_KEY)

print("🔍 Listando modelos disponíveis para sua chave...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Disponível: {m.name}")
except Exception as e:
    print(f"❌ Erro ao listar: {e}")
