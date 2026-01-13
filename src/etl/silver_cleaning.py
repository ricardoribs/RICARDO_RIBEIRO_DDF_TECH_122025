import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, col
from pyspark.sql.types import FloatType

class SilverCleaner:
    """
    Aplica limpeza e padronização da camada Bronze para Silver.
    """
    def __init__(self, spark: SparkSession, lakehouse_dir: str):
        self.spark = spark
        self.lakehouse_dir = str(lakehouse_dir)

    def clean_order_items(self):
        input_path = os.path.join(self.lakehouse_dir, "bronze", "order_items")
        print(f"🧹 Cleaning data from {input_path}...")
        
        df = self.spark.read.parquet(input_path)
        
        # Transformações: Casting explícito, metadados e remoção de duplicatas
        df_clean = df.withColumn("processed_at", current_timestamp()) \
                     .withColumn("price", col("price").cast(FloatType())) \
                     .withColumn("freight_value", col("freight_value").cast(FloatType())) \
                     .dropDuplicates(["order_id", "order_item_id"])
        
        return df_clean