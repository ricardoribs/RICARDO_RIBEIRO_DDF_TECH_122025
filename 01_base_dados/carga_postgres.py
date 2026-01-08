import pandas as pd
from sqlalchemy import create_engine

# 1. Cole sua URL do Neon aqui (MANTENHA as aspas)
DATABASE_URL = "postgresql://neondb_owner:npg_1QsZTI5WHJEf@ep-fragrant-wildflower-acyrg3bh-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Cria a conexão
engine = create_engine(DATABASE_URL)

# Lista dos arquivos para subir
arquivos = {
    "olist_order_items": "olist_order_items_dataset.csv",
    "olist_products": "olist_products_dataset.csv",
    "olist_customers": "olist_customers_dataset.csv",
    "olist_orders": "olist_orders_dataset.csv"
}

print("🚀 Iniciando carga para o PostgreSQL...")

for tabela, arquivo in arquivos.items():
    print(f"Lendo {arquivo}...")
    # Lê o CSV
    df = pd.read_csv(arquivo)
    
    # Sobe para o banco
    print(f"Enviando {tabela} ({len(df)} linhas)...")
    df.to_sql(tabela, engine, if_exists='replace', index=False)
    print(f"✅ {tabela} carregada com sucesso!")

print("🎉 Tudo pronto! Agora vá para a Dadosfera.")