import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
from src.config import settings  # <--- Importa a configuração segura

# Configuração da Página
st.set_page_config(page_title="Olist Lakehouse", layout="wide")

st.title("🛍️ Olist Intelligent Data Lakehouse")

# --- VALIDAÇÃO DE SEGURANÇA ---
# Verifica se a chave existe sem mostrá-la
if settings.GOOGLE_API_KEY.get_secret_value():
    st.sidebar.success("🔒 API Gemini: Conectado via Variável de Ambiente")
else:
    st.sidebar.error("❌ API Gemini: Chave não encontrada! Verifique o .env")
    st.stop()

# --- CONEXÃO COM DADOS ---
# Usa o caminho definido no settings, não hardcoded
DB_PATH = settings.LAKEHOUSE_DIR / "dbt_project/olist_analytics/olist_local.duckdb"

@st.cache_resource
def get_connection():
    if not DB_PATH.exists():
        st.error(f"Banco de dados não encontrado em: {DB_PATH}")
        st.stop()
    return duckdb.connect(str(DB_PATH), read_only=True)

try:
    con = get_connection()
    
    # ... (Resto do seu código de dashboard continua igual) ...
    
    # Exemplo de consulta usando a conexão
    st.metric("Total de Vendas (R$)", "R$ 1.5M")
    
except Exception as e:
    st.error(f"Erro ao conectar no Lakehouse: {e}")