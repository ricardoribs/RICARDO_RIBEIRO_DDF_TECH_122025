import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType

class BronzeIngestor:
    """
    Gerencia a ingestão de dados brutos (CSV) para a camada Bronze (Parquet).
    """
    def __init__(self, spark: SparkSession, lakehouse_dir: str):
        self.spark = spark
        self.lakehouse_dir = str(lakehouse_dir)

    def ingest_orders(self, csv_path: str):
        print(f"🔄 Ingesting from {csv_path}...")
        
        # Schema explícito para performance e segurança
        schema = StructType([
            StructField("order_id", StringType(), False),
            StructField("order_item_id", IntegerType(), True),
            StructField("product_id", StringType(), True),
            StructField("seller_id", StringType(), True),
            StructField("shipping_limit_date", TimestampType(), True),
            StructField("price", FloatType(), True),
            StructField("freight_value", FloatType(), True)
        ])

        # Lê CSV com schema definido
        df = self.spark.read.csv(csv_path, header=True, schema=schema)
        
        # Salva em Parquet (Bronze)
        output_path = os.path.join(self.lakehouse_dir, "bronze", "order_items")
        df.write.mode("overwrite").parquet(output_path)
        print(f"✅ Bronze Saved: {output_path}")