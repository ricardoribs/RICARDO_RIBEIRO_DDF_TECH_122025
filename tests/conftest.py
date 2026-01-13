import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    """Cria uma sessão Spark local otimizada para testes."""
    spark = (
        SparkSession.builder
        .master("local[1]")  # Roda em 1 núcleo para ser rápido
        .appName("OlistUnitTests")
        .config("spark.sql.shuffle.partitions", "1") # Evita overhead em dados pequenos
        .config("spark.ui.enabled", "false") # Desativa UI para ganhar tempo
        .getOrCreate()
    )
    yield spark
    spark.stop()