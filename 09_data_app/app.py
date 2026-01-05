import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="Olist Executive Dashboard",
    page_icon="🛒",
    layout="wide"
)

# --- Título e Cabeçalho ---
st.title("🛒 Dashboard Executivo - Olist E-commerce")
st.markdown("---")

# --- Função de Carregamento de Dados (com Cache) ---
@st.cache_data
def load_data():
    # Caminho relativo buscando na pasta anterior (01_base_dados)
    # Tenta caminhos diferentes para evitar erro de "Arquivo não encontrado"
    possible_paths = [
        "../01_base_dados/olist_order_items_dataset.csv",
        "01_base_dados/olist_order_items_dataset.csv",
        "olist_order_items_dataset.csv"
    ]
    
    df = None
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            break
            
    if df is None:
        st.error("❌ Erro: Arquivo CSV não encontrado. Verifique se a pasta '01_base_dados' existe.")
        return None

    # Tratamento de dados básico
    if 'shipping_limit_date' in df.columns:
        df['data'] = pd.to_datetime(df['shipping_limit_date']).dt.date
    
    return df

# Carregar dados
data = load_data()

if data is not None:
    # --- Sidebar (Filtros) ---
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Data
    min_date = data['data'].min()
    max_date = data['data'].max()
    
    start_date, end_date = st.sidebar.date_input(
        "Selecione o Período",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # Aplicar Filtro
    df_filtered = data[
        (data['data'] >= start_date) & 
        (data['data'] <= end_date)
    ]

    # --- KPIs (Indicadores Principais) ---
    col1, col2, col3, col4 = st.columns(4)

    receita_total = df_filtered['price'].sum()
    frete_total = df_filtered['freight_value'].sum()
    total_pedidos = df_filtered['order_id'].nunique()
    ticket_medio = receita_total / total_pedidos if total_pedidos > 0 else 0

    col1.metric("💰 Receita Total", f"R$ {receita_total:,.2f}")
    col2.metric("📦 Total de Pedidos", f"{total_pedidos:,}")
    col3.metric("🚚 Custo de Frete", f"R$ {frete_total:,.2f}")
    col4.metric("🎫 Ticket Médio", f"R$ {ticket_medio:,.2f}")

    st.markdown("---")

    # --- Gráficos (Layout em Colunas) ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Evolução de Vendas (Diária)")
        vendas_diarias = df_filtered.groupby('data')['price'].sum().reset_index()
        fig_line = px.area(vendas_diarias, x='data', y='price', template="plotly_white")
        st.plotly_chart(fig_line, use_container_width=True)

    with col_right:
        st.subheader("🏆 Top 10 Vendedores (Receita)")
        top_sellers = df_filtered.groupby('seller_id')['price'].sum().reset_index().sort_values(by='price', ascending=False).head(10)
        fig_bar = px.bar(top_sellers, x='price', y='seller_id', orientation='h', template="plotly_white")
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}) # Ordenar barras
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Análise de Distribuição ---
    st.subheader("📊 Distribuição de Preço vs Frete")
    st.caption("Analise a correlação entre o valor do produto e o custo de envio.")
    
    # Amostra de 5000 pontos para não pesar o gráfico
    fig_scatter = px.scatter(
        df_filtered.sample(min(5000, len(df_filtered))), 
        x='price', 
        y='freight_value', 
        opacity=0.5,
        title="Scatter Plot (Amostra 5k registros)",
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Rodapé ---
    st.markdown("---")
    st.markdown("**Desenvolvido por Ricardo Ribeiro** | Case Técnico Dadosfera 2025")