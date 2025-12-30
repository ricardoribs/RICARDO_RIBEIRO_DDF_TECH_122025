import great_expectations as gx
import pandas as pd
import os
import webbrowser  # <--- Importante para abrir o navegador
from great_expectations.expectations import (
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeBetween
)

print("🚀 Iniciando Validação de Qualidade (Versão com Relatório)...")

# 1. Configurar contexto
context = gx.get_context()

# 2. Carregar dados
caminho_csv = "../01_base_dados/olist_order_items_dataset.csv"

# Resolve caminho absoluto para evitar erros
caminho_abs = os.path.abspath(caminho_csv)
if not os.path.exists(caminho_abs):
    print(f"❌ Erro: Arquivo não encontrado em {caminho_abs}")
    exit()

print(f"📂 Lendo arquivo: {caminho_abs}...")
df = pd.read_csv(caminho_abs)

# 3. Criar Fonte de Dados
data_source = context.data_sources.add_pandas("meus_dados_olist")
data_asset = data_source.add_dataframe_asset(name="itens_pedidos")
batch_definition = data_asset.add_batch_definition_whole_dataframe("batch_def_olist")

# 4. Criar Suite de Testes
suite_name = "suite_qualidade_bronze"
try:
    context.suites.delete(suite_name)
except:
    pass

suite = context.suites.add(gx.ExpectationSuite(name=suite_name))

print("🧪 Definindo regras...")
# Regras
suite.add_expectation(ExpectColumnValuesToNotBeNull(column="order_id"))
suite.add_expectation(ExpectColumnValuesToNotBeNull(column="product_id"))
suite.add_expectation(ExpectColumnValuesToBeBetween(column="price", min_value=0.01))
suite.add_expectation(ExpectColumnValuesToBeBetween(column="freight_value", min_value=0))

# 5. Validação
validation_definition = context.validation_definitions.add(
    gx.ValidationDefinition(
        name="validacao_def",
        data=batch_definition,
        suite=suite
    )
)

# 6. Checkpoint + Action de Update Data Docs (Importante!)
checkpoint = context.checkpoints.add(
    gx.Checkpoint(
        name="checkpoint_validacao",
        validation_definitions=[validation_definition],
        actions=[
            gx.checkpoint.actions.UpdateDataDocsAction(name="update_data_docs")
        ]
    )
)

print("🏃 Rodando verificação...")
result = checkpoint.run(batch_parameters={"dataframe": df})

print(f"✅ Resultado: {result.success}")

# --- PARTE NOVA: FORÇAR ABERTURA DO RELATÓRIO ---
print("📄 Tentando abrir relatório...")

# Tenta o método nativo primeiro
try:
    urls = context.open_data_docs()
except:
    pass

# Se não abriu, vamos caçar o arquivo HTML manualmente
# O GX cria uma pasta 'gx' onde o script roda
caminho_relatorio = os.path.join(os.getcwd(), "gx", "uncommitted", "data_docs", "local_site", "index.html")

if os.path.exists(caminho_relatorio):
    print(f"🔗 Abrindo: {caminho_relatorio}")
    webbrowser.open(f"file:///{caminho_relatorio}")
else:
    print("⚠️ Não achei o index.html padrão. Procurando nas subpastas...")
    # Tenta achar qualquer index.html dentro da pasta gx
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), "gx")):
        if "index.html" in files:
            full_path = os.path.join(root, "index.html")
            print(f"🔗 Encontrado e abrindo: {full_path}")
            webbrowser.open(f"file:///{full_path}")
            break