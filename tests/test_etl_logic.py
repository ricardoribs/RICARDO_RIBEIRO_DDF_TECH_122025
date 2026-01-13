# tests/test_etl_logic.py
from pyspark.sql.types import StructType, StructField, StringType, FloatType


def test_schema_enforcement(spark):
    """
    Testa se conseguimos criar um DataFrame com o Schema definido.
    Simula a entrada de dados brutos.
    """
    # 1. Define dados simulados (Mock)
    data = [("order_1", "prod_A", 100.50), ("order_2", "prod_B", 50.00)]

    # 2. Define o schema esperado (igual ao do flow_main.py)
    schema = StructType(
        [
            StructField("order_id", StringType(), True),
            StructField("product_id", StringType(), True),
            StructField("price", FloatType(), True),
        ]
    )

    # 3. Cria o DataFrame
    df = spark.createDataFrame(data, schema)

    # 4. Asserções (Validações)
    assert df.count() == 2
    assert "price" in df.columns
    # Verifica se o tipo do preço é Float mesmo
    assert df.schema["price"].dataType == FloatType()


def test_negative_price_logic(spark):
    """
    Testa a lógica que usaremos no Quality Gate.
    Verifica se conseguimos identificar preços negativos.
    """
    data = [("valid", 10.0), ("invalid", -5.0)]
    schema = StructType(
        [StructField("id", StringType(), True), StructField("price", FloatType(), True)]
    )

    df = spark.createDataFrame(data, schema)

    # Lógica de filtro
    negatives = df.filter("price < 0").count()

    assert negatives == 1
