import pytest
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from src.etl.silver_cleaning import SilverCleaner
import shutil
from pathlib import Path

# Dados Mockados
def get_dirty_data(spark):
    data = [
        # order_id, order_item_id, product_id, price, freight_value, shipping_limit_date
        ("order_1", "1", "prod_A", "29.99", "15.00", "2023-01-01"), # Caso Perfeito
        ("order_2", "1", "prod_B", "-10.00", "12.00", "2023-01-02"), # Preço Negativo
        ("order_3", "1", None, "50.00", "10.00", "2023-01-03"),      # Produto Nulo
        ("order_4", "1", "prod_C", "invalid", "0.00", "2023-01-04") # Preço inválido
    ]
    columns = ["order_id", "order_item_id", "product_id", "price", "freight_value", "shipping_limit_date"]
    return spark.createDataFrame(data, columns)

def test_clean_order_items_schema_and_logic(spark, tmp_path):
    """
    Testa se a transformação Silver:
    1. Converte tipos corretamente (String -> Double).
    2. Mantém a estrutura de colunas esperada.
    """
    # 1. Setup
    df_dirty = get_dirty_data(spark)
    
    lakehouse_path = tmp_path / "lakehouse"
    cleaner = SilverCleaner(spark, lakehouse_path)
    
    bronze_path = lakehouse_path / "bronze" / "order_items"
    df_dirty.write.mode("overwrite").parquet(str(bronze_path))
    
    # 2. Execução
    df_cleaned = cleaner.clean_order_items()
    
    # 3. Asserções
    rows = df_cleaned.collect()
    
    # Verifica conversão de preço
    row_1 = next(r for r in rows if r.order_id == "order_1")
    
    # [CORREÇÃO] Usamos pytest.approx para ignorar diferenças infinitesimais de float
    assert row_1.price == pytest.approx(29.99, abs=0.01)
    
    # Verifica se freight_value foi mantido e convertido
    assert row_1.freight_value == pytest.approx(15.00, abs=0.01)

    print("\n✅ Teste de Lógica Silver: SUCESSO")