import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# SEMPRE usar variável de ambiente, nunca hardcoded
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY não encontrada no arquivo .env ou variáveis de ambiente.")

print("✅ Chave de API encontrada. Configurando cliente...")
genai.configure(api_key=GOOGLE_API_KEY)

# Teste simples (opcional)
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, Data Engineering!")
    print(f"🤖 Resposta do Gemini: {response.text}")
except Exception as e:
    print(f"⚠️ Erro ao conectar com a API: {e}")