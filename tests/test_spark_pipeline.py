import pytest
from pyspark.sql import SparkSession


# Fixture: Configura uma sessão Spark de teste (leve)
@pytest.fixture(scope="session")
def spark():
    spark_session = (
        SparkSession.builder.master("local[1]").appName("CI_CD_Test").getOrCreate()
    )
    yield spark_session
    spark_session.stop()


# Teste 1: Verifica se o Spark iniciou corretamente
def test_spark_session_is_active(spark):
    assert spark is not None
    assert not spark.sparkContext._jsc.sc().isStopped()


# Teste 2: Verifica se conseguimos criar um DataFrame (teste de processamento)
def test_simple_dataframe_operation(spark):
    data = [("Ricardo", "Data Engineer"), ("Dadosfera", "Company")]
    columns = ["Name", "Role"]

    df = spark.createDataFrame(data, columns)

    assert df.count() == 2
    assert "Name" in df.columns
