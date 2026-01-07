import pytest
import os
import shutil
from pyspark.sql import SparkSession

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_SCRIPT = os.path.join(BASE_DIR, '..', '08_pipelines', 'pipeline_pyspark_lakehouse.py')
LAKE_DIR = os.path.join(BASE_DIR, '..', '08_pipelines', 'data_lake')

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .appName("IntegrationTest") \
        .master("local[1]") \
        .getOrCreate()

def test_pipeline_pyspark_end_to_end(spark):
    """
    Executa o script do pipeline PySpark como um subprocesso e verifica
    se os arquivos Parquet foram gerados nas camadas Bronze, Silver e Gold.
    """
    print("\n🔄 Executando Pipeline PySpark via Sistema...")
    
    # 1. Executa o script real
    exit_code = os.system(f"python {PIPELINE_SCRIPT}")
    assert exit_code == 0, "O script do pipeline falhou na execução."

    # 2. Verifica Camada Bronze (Raw Parquet)
    bronze_items = os.path.join(LAKE_DIR, "bronze", "items")
    assert os.path.exists(bronze_items), "Pasta Bronze/Items não criada"
    assert len(os.listdir(bronze_items)) > 0, "Nenhum arquivo Parquet na Bronze"

    # 3. Verifica Camada Silver (Clean Parquet)
    silver_fact = os.path.join(LAKE_DIR, "silver", "fact_items")
    df_silver = spark.read.parquet(silver_fact)
    assert df_silver.count() > 0, "Tabela Fato Silver está vazia"
    assert "ingestion_date" in df_silver.columns, "Metadado de ingestão perdido"

    # 4. Verifica Camada Gold (Aggregated)
    gold_vendas = os.path.join(LAKE_DIR, "gold", "vendas_mensais")
    df_gold = spark.read.parquet(gold_vendas)
    
    assert df_gold.count() > 0, "Tabela Gold vazia"
    assert "receita_total" in df_gold.columns, "Coluna de receita não encontrada na Gold"
    
    print("✅ Teste de Integração Spark: SUCESSO (Bronze -> Silver -> Gold)")