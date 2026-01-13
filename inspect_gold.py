from pyspark.sql import SparkSession
import os

# Caminho do arquivo gerado pela IA
BASE_DIR = os.getcwd()
GOLD_AI_PATH = os.path.join(BASE_DIR, "09_lakehouse", "gold", "ai_product_descriptions")


def inspect():
    spark = SparkSession.builder.master("local[1]").appName("Inspector").getOrCreate()

    print(f"🔍 Lendo dados de: {GOLD_AI_PATH}")

    if os.path.exists(GOLD_AI_PATH):
        df = spark.read.parquet(GOLD_AI_PATH)
        print("--- 🤖 PRODUTOS ENRIQUECIDOS PELA IA ---")
        df.show(truncate=False)
    else:
        print("❌ Arquivo não encontrado.")


if __name__ == "__main__":
    inspect()
