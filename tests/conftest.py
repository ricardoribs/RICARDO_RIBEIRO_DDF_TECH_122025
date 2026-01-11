# tests/conftest.py
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """
    Cria uma Sessão Spark exclusiva para testes.
    Configurada para ser leve (local) e não consumir muita memória.
    """
    spark = (
        SparkSession.builder.master("local[1]")
        .appName("Olist_Unit_Tests")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    yield spark

    # Encerra a sessão após todos os testes
    spark.stop()
