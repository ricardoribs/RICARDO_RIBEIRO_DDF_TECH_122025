import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType

@pytest.fixture(scope="session")
def spark():
    """Sessão Spark local para testes"""
    return SparkSession.builder \
        .master("local[1]") \
        .appName("Test") \
        .getOrCreate()

def test_calculo_receita_gold(spark):
    """Testa se o Spark soma corretamente a receita"""
    data = [("beleza", 100.0), ("beleza", 50.0), ("tech", 200.0)]
    df = spark.createDataFrame(data, ["categoria", "price"])
    
    df_agg = df.groupBy("categoria").sum("price")
    row = df_agg.filter("categoria='beleza'").collect()[0]
    
    assert row[1] == 150.0 # 100 + 50