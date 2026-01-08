from prefect import flow, task
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
import os

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAKEHOUSE_DIR = os.path.join(BASE_DIR, "09_lakehouse")
RAW_DATA_DIR = os.path.join(BASE_DIR, "01_base_dados")

# --- FUNÇÃO AUXILIAR (Não é Task) ---
def get_spark_session():
    """
    Retorna a sessão Spark ativa ou cria uma nova.
    Removemos o Delta Lake para simplificar a execução no WSL sem JARs externos.
    """
    return SparkSession.builder \
        .appName("Olist_Modern_Stack") \
        .master("local[*]") \
        .config("spark.ui.showConsoleProgress", "false") \
        .getOrCreate()

@task(name="Ingest Bronze (Raw)", log_prints=True)
def ingest_bronze():
    # Instanciamos o Spark AQUI DENTRO para evitar erro de serialização do Prefect
    spark = get_spark_session()
    
    print(f"📥 Ingesting Data to Bronze Layer at {LAKEHOUSE_DIR}/bronze")
    
    csv_file = os.path.join(RAW_DATA_DIR, "olist_order_items_dataset.csv")
    
    if not os.path.exists(csv_file):
        print(f"⚠️ Aviso: Arquivo não encontrado: {csv_file}")
        return

    # Leitura
    df_items = spark.read.csv(csv_file, header=True, inferSchema=True)
    
    # Escrita (Parquet Puro)
    output_path = os.path.join(LAKEHOUSE_DIR, "bronze", "order_items")
    df_items.write.mode("overwrite").parquet(output_path)
    print(f"✅ Bronze Layer Updated: {df_items.count()} rows")

@task(name="Transform Silver (Clean)", log_prints=True)
def process_silver():
    spark = get_spark_session()
    print("✨ Processing Silver Layer...")
    
    bronze_path = os.path.join(LAKEHOUSE_DIR, "bronze", "order_items")
    
    try:
        # Leitura da Bronze
        df = spark.read.parquet(bronze_path)
        
        # Transformação
        df_clean = df.withColumn("processed_at", current_timestamp()) \
                     .withColumn("price", df["price"].cast(FloatType())) \
                     .withColumn("freight_value", df["freight_value"].cast(FloatType()))
        
        # Escrita na Silver
        output_path = os.path.join(LAKEHOUSE_DIR, "silver", "order_items")
        df_clean.write.mode("overwrite").parquet(output_path)
        print("✅ Silver Layer Updated")
        
    except Exception as e:
        print(f"❌ Erro na Silver: {e}")

@flow(name="Olist ETL Pipeline")
def main_flow():
    print("🚀 Iniciando Pipeline Olist (Prefect + Spark)...")
    
    # Chamamos as tasks sem passar argumentos complexos
    ingest_bronze()
    process_silver()
    
    print("🏁 Pipeline Finalizado!")

if __name__ == "__main__":
    main_flow()