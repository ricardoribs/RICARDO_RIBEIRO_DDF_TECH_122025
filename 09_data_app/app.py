import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Olist | Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# ESTILO GLOBAL (DESIGN SYSTEM)
# =====================================================
st.markdown("""
<style>
:root {
    --primary: #111827;
    --secondary: #6b7280;
    --accent: #2563eb;
    --border: #e5e7eb;
    --bg: #f9fafb;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 2rem;
    background-color: var(--bg);
}

.section-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 0.5rem;
}

.section-subtitle {
    font-size: 0.9rem;
    color: var(--secondary);
    margin-bottom: 1.5rem;
}

.kpi-card {
    background-color: white;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid var(--border);
}

.kpi-title {
    font-size: 0.8rem;
    color: var(--secondary);
}

.kpi-value {
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--primary);
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================
def kpi(title, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def apply_plot_theme(fig):
    fig.update_layout(
        template="simple_white",
        font=dict(size=12),
        title_font_size=16,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )
    return fig


@st.cache_data(ttl=3600)
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        base_dir, "..", "01_base_dados", "olist_order_items_dataset.csv"
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    df = pd.read_csv(file_path)
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"])
    df["data"] = df["shipping_limit_date"].dt.date
    return df


# =====================================================
# HEADER
# =====================================================
st.markdown("## Olist • Visão Executiva")
st.markdown(
    "<div class='section-subtitle'>Análise consolidada de vendas, logística e performance operacional</div>",
    unsafe_allow_html=True
)

# =====================================================
# LOAD DATA
# =====================================================
try:
    data = load_data()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# =====================================================
# SIDEBAR — FILTROS
# =====================================================
with st.sidebar:
    st.markdown("### Filtros")
    st.caption("Aplicados globalmente no dashboard")

    preset = st.selectbox(
        "Período",
        ["Tudo", "7 dias", "30 dias", "12 meses", "Personalizado"]
    )

    min_date = data["data"].min()
    max_date = data["data"].max()

    if preset == "7 dias":
        start_date = max_date - timedelta(days=7)
        end_date = max_date
    elif preset == "30 dias":
        start_date = max_date - timedelta(days=30)
        end_date = max_date
    elif preset == "12 meses":
        start_date = max_date - timedelta(days=365)
        end_date = max_date
    elif preset == "Personalizado":
        date_range = st.date_input(
            "Intervalo",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    st.caption(f"{start_date} → {end_date}")

    if st.button("Resetar filtros"):
        st.cache_data.clear()
        st.rerun()

# =====================================================
# APLICA FILTROS
# =====================================================
df = data[
    (data["data"] >= start_date) &
    (data["data"] <= end_date)
]

# =====================================================
# KPIs
# =====================================================
receita = df["price"].sum()
pedidos = df["order_id"].nunique()
ticket = receita / pedidos if pedidos > 0 else 0
frete = df["freight_value"].mean()

k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi("Receita Total", f"R$ {receita:,.2f}")
with k2:
    kpi("Pedidos", f"{pedidos:,}")
with k3:
    kpi("Ticket Médio", f"R$ {ticket:,.2f}")
with k4:
    kpi("Frete Médio", f"R$ {frete:,.2f}")

st.markdown("---")

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3 = st.tabs([
    "Evolução",
    "Rankings",
    "Distribuição"
])

# =====================================================
# TAB 1 — EVOLUÇÃO
# =====================================================
with tab1:
    st.markdown("<div class='section-title'>Evolução da Receita</div>", unsafe_allow_html=True)

    gran = st.radio("Granularidade", ["Dia", "Mês"], horizontal=True)

    chart_df = df.copy()
    if gran == "Mês":
        chart_df["periodo"] = pd.to_datetime(chart_df["data"]).dt.to_period("M").dt.to_timestamp()
    else:
        chart_df["periodo"] = pd.to_datetime(chart_df["data"])

    chart_df = chart_df.groupby("periodo")["price"].sum().reset_index()

    fig = px.area(
        chart_df,
        x="periodo",
        y="price",
        labels={"price": "Receita (R$)", "periodo": "Data"}
    )

    st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

# =====================================================
# TAB 2 — RANKINGS
# =====================================================
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-title'>Top Sellers</div>", unsafe_allow_html=True)
        sellers = df.groupby("seller_id")["price"].sum().nlargest(10).reset_index()
        fig = px.bar(
            sellers,
            x="price",
            y="seller_id",
            orientation="h",
            labels={"price": "Receita (R$)", "seller_id": "Seller"}
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>Top Produtos</div>", unsafe_allow_html=True)
        products = df.groupby("product_id")["order_item_id"].count().nlargest(10).reset_index()
        fig = px.bar(
            products,
            x="order_item_id",
            y="product_id",
            orientation="h",
            labels={"order_item_id": "Quantidade", "product_id": "Produto"}
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

# =====================================================
# TAB 3 — DISTRIBUIÇÃO
# =====================================================
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-title'>Distribuição de Preços</div>", unsafe_allow_html=True)
        limit = df["price"].quantile(0.95)
        fig = px.histogram(
            df[df["price"] <= limit],
            x="price",
            nbins=30
        )
        st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>Preço vs Frete</div>", unsafe_allow_html=True)
        sample = df.sample(min(2000, len(df)))
        fig = px.scatter(
            sample,
            x="price",
            y="freight_value",
            opacity=0.5,
            labels={"price": "Preço", "freight_value": "Frete"}
        )
        st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} • Cache ativo")
