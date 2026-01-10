import pandas as pd
import streamlit as st
from pathlib import Path

# =====================================================
# Page config
# =====================================================
st.set_page_config(
    page_title="Olist Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# Resolve project root
# =====================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_PATH = PROJECT_ROOT / "09_lakehouse" / "silver"

ORDERS_DIR = SILVER_PATH / "orders"
ITEMS_DIR = SILVER_PATH / "order_items"

# =====================================================
# Dataset validation
# =====================================================
missing = []
if not ORDERS_DIR.exists():
    missing.append(str(ORDERS_DIR))
if not ITEMS_DIR.exists():
    missing.append(str(ITEMS_DIR))

if missing:
    st.error("Required datasets not found")
    st.code("\n".join(missing))
    st.stop()

# =====================================================
# Load data
# =====================================================
@st.cache_data(show_spinner=True)
def load_data():
    orders = pd.read_parquet(ORDERS_DIR)
    items = pd.read_parquet(ITEMS_DIR)

    # Garantia de datetime
    if "order_purchase_timestamp" not in orders.columns:
        raise ValueError("Column 'order_purchase_timestamp' not found in orders dataset")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce"
    )

    df = items.merge(
        orders[["order_id", "order_purchase_timestamp"]],
        on="order_id",
        how="left"
    )

    return df

df = load_data()

# =====================================================
# Sidebar filters
# =====================================================
with st.sidebar:
    st.markdown("## Filters")

    # ---------- YEAR ----------
    years = (
        df["order_purchase_timestamp"]
        .dropna()
        .dt.year
        .astype(int)
        .unique()
    )

    if len(years) > 1:
        selected_year = st.selectbox(
            "Year",
            sorted(years),
            index=len(years) - 1
        )
    else:
        selected_year = years[0]
        st.caption(f"Year: {selected_year}")

    # ---------- PRODUCTS ----------
    top_products = (
        df.groupby("product_id")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(20)
        .index
        .tolist()
    )

    selected_products = st.multiselect(
        "Products (Top revenue)",
        options=top_products,
        default=top_products[:5]
    )


# =====================================================
# Apply filters
# =====================================================
df_filtered = df[
    (df["order_purchase_timestamp"].dt.year == selected_year)
    & (df["product_id"].isin(selected_products))
]

# =====================================================
# Header
# =====================================================
st.markdown("## Olist Analytics")
st.caption(
    f"Year: {selected_year} • "
    f"Orders: {df_filtered['order_id'].nunique():,}"
)

# =====================================================
# KPIs
# =====================================================
c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Revenue",
    f"${df_filtered['price'].sum():,.2f}"
)

c2.metric(
    "Average Item Price",
    f"${df_filtered['price'].mean():,.2f}"
)

c3.metric(
    "Items Sold",
    f"{len(df_filtered):,}"
)

# =====================================================
# Charts
# =====================================================
st.markdown("### Revenue by Product")

revenue = (
    df_filtered
    .groupby("product_id", as_index=False)["price"]
    .sum()
    .sort_values("price", ascending=False)
)

st.bar_chart(
    revenue,
    x="product_id",
    y="price",
    use_container_width=True
)

# =====================================================
# Data preview
# =====================================================
with st.expander("Data preview"):
    st.dataframe(df_filtered, use_container_width=True)
