import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
import io
from PIL import Image
import google.generativeai as genai
from huggingface_hub import InferenceClient

# ============================================
# 1. CONFIGURAÇÃO E CAMINHOS
# ============================================
st.set_page_config(page_title="Olist Lakehouse & AI", layout="wide", page_icon="🛍️")

# Garante que o caminho para o Lakehouse seja encontrado independente de onde o script rode
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GOLD_PATH = os.path.join(SCRIPT_DIR, '..', '09_lakehouse', 'gold', 'pedidos_por_mes')

# ============================================
# 2. FUNÇÕES DE IA (CÉREBRO E PINTOR)
# ============================================

def get_creative_prompt(api_key, product_desc):
    """
    Usa o Google Gemini. Se der erro de cota (429), usa um prompt de fallback 
    para garantir que a imagem seja gerada na demo.
    """
    try:
        genai.configure(api_key=api_key)
        
        # Vamos tentar o 1.5 Flash que costuma ter limites mais altos que o 2.0
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt_tecnico = f"""
        Task: Create a detailed, high-quality image generation prompt for Stable Diffusion based on this product: "{product_desc}".
        Requisitos: Professional studio lighting, 8k, photorealistic, product focus.
        Output ONLY the prompt text in English.
        """
        
        response = model.generate_content(prompt_tecnico)
        return response.text

    except Exception as e:
        # --- ZONA DE SALVAMENTO DE DEMO ---
        # Se o Gemini falhar (Cota excedida), não paramos o app.
        # Criamos um prompt manual em inglês usando f-string.
        print(f"⚠️ Aviso: Gemini falhou ({e}). Usando Fallback.")
        st.warning("⚠️ Nota: Cota de IA de texto excedida. Usando modo de contingência para gerar a imagem.")
        
        # Fallback: Tradução técnica "burra" mas funcional para a imagem não falhar
        return f"Professional advertising photography of {product_desc}, cinematic lighting, 8k resolution, highly detailed, photorealistic, blurred background, product focus."

def generate_image_hf(api_token, prompt):
    """
    Usa a API da Hugging Face com o modelo v1.5 (Mais estável e rápido).
    """
    # Modelo v1.5: Menor qualidade que o XL, mas funciona quase sempre.
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        
        # Se a API pedir para esperar (modelo carregando), esperamos um pouco
        if "estimated_time" in response.json():
            st.info(f"O modelo está 'acordando'. Aguarde {response.json()['estimated_time']:.0f}s...")
            import time
            time.sleep(response.json()['estimated_time'])
            # Tenta de novo
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

        if response.status_code != 200:
            st.error(f"Erro HF ({response.status_code}): {response.text}")
            return None
            
        return Image.open(io.BytesIO(response.content))
        
    except Exception as e:
        # PLANO Z: Se tudo falhar (internet/API), retorna um Placeholder para não estragar o vídeo
        st.error(f"Erro de conexão: {e}")
        return None

# ============================================
# 3. INTERFACE DO APLICATIVO
# ============================================
st.title("🛍️ Plataforma Olist: Analytics & Creative AI")
st.markdown("Uma solução completa de Engenharia de Dados: do Lakehouse à Inteligência Artificial.")

tab1, tab2 = st.tabs(["📊 Dashboard de Vendas (Lakehouse)", "🎨 Estúdio de Marketing (GenAI)"])

# --- ABA 1: ANALYTICS ---
with tab1:
    st.header("KPIs de Vendas (Dados Processados via Spark)")
    
    if not os.path.exists(GOLD_PATH):
        st.error(f"❌ Erro Crítico: O caminho do Lakehouse não foi encontrado: {GOLD_PATH}")
        st.info("Dica: Verifique se o pipeline PySpark rodou com sucesso e gerou a pasta 'gold'.")
    else:
        try:
            # Leitura Otimizada de Parquet (Engine PyArrow)
            df = pd.read_parquet(GOLD_PATH, engine='pyarrow')
            
            # Pequeno tratamento para exibição (Pandas)
            df['ano'] = df['order_year'].astype(int)
            df['mes'] = df['order_month'].astype(int)
            # Cria data para ordenação no gráfico
            df['data_ref'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str) + '-01')
            df = df.sort_values('data_ref')

            # Métricas
            col1, col2, col3 = st.columns(3)
            total_pedidos = df['count'].sum()
            melhor_mes = df.loc[df['count'].idxmax()]
            
            col1.metric("Volume Total de Pedidos", f"{total_pedidos:,.0f}")
            col2.metric("Média Mensal", f"{df['count'].mean():,.0f}")
            col3.metric("Pico de Vendas", f"{melhor_mes['count']:,.0f} ({melhor_mes['mes']}/{melhor_mes['ano']})")

            st.divider()

            # Gráfico
            fig = px.area(df, x='data_ref', y='count', title='Evolução Temporal de Pedidos', markers=True)
            fig.update_layout(xaxis_title='Mês/Ano', yaxis_title='Qtd. Pedidos')
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro ao ler dados do Lakehouse: {e}")

# --- ABA 2: GENAI ---
with tab2:
    st.header("✨ Gerador de Anúncios com IA")
    st.markdown("""
    Este módulo utiliza uma **Arquitetura de Agentes**:
    1. **Google Gemini:** Cria o conceito artístico (Prompt Engineering).
    2. **Stable Diffusion:** Renderiza a imagem final.
    """)
    
    col_input, col_result = st.columns([1, 2])
    
    with col_input:
        st.subheader("⚙️ Configuração")
        
        # Inputs de Chaves (Para não deixar hardcoded no código)
        gemini_key = st.text_input("Gemini API Key:", type="password", help="Pegue no Google AI Studio")
        hf_token = st.text_input("Hugging Face Token:", type="password", help="Pegue nas configurações do Hugging Face")
        
        st.divider()
        
        product_input = st.text_area(
            "Descreva o produto para o anúncio:", 
            placeholder="Ex: Uma cafeteira italiana vermelha em uma cozinha rústica com fumaça saindo.",
            height=100
        )
        
        btn_generate = st.button("🎨 Criar Anúncio", type="primary", disabled=(not gemini_key or not hf_token or not product_input))

    with col_result:
        st.subheader("🖼️ Resultado")
        
        if btn_generate:
            # 1. Passo: Gemini cria o prompt
            with st.status("🤖 1. Acionando Google Gemini...", expanded=True) as status:
                st.write("Criando roteiro artístico...")
                creative_prompt = get_creative_prompt(gemini_key, product_input)
                
                if creative_prompt:
                    st.success("Prompt criado com sucesso!")
                    st.code(creative_prompt, language="text")
                    
                    # 2. Passo: Hugging Face cria a imagem
                    status.update(label="🎨 2. Acionando Stable Diffusion...", state="running")
                    image = generate_image_hf(hf_token, creative_prompt)
                    
                    if image:
                        status.update(label="✅ Processo concluído!", state="complete", expanded=False)
                        st.image(image, caption="Imagem gerada por IA", use_column_width=True)
                        
                        # Botão de Download
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button(
                            label="⬇️ Baixar Imagem",
                            data=buf.getvalue(),
                            file_name="anuncio_ia.png",
                            mime="image/png"
                        )
                    else:
                        status.update(label="❌ Falha na geração da imagem", state="error")
                else:
                    status.update(label="❌ Falha no Gemini", state="error")