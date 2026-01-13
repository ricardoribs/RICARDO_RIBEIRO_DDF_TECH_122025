import time
from prefect import flow, task, get_run_logger
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
import google.generativeai as genai

# Importações dos módulos internos
from src.config import settings
from src.observability import monitor

def get_spark_session():
    """
    Cria ou recupera uma sessão Spark otimizada para o ambiente Docker.
    """
    return (SparkSession.builder
            .appName("Olist_Enterprise_ETL")
            .config("spark.sql.shuffle.partitions", "4") # Otimização para dados pequenos/médios
            .config("spark.driver.memory", "1g")
            .config("spark.executor.memory", "1g")
            .master("local[*]")
            .getOrCreate())

# ---------------------------------------------------------------------------
# 1. BRONZE LAYER (Ingestão)
# ---------------------------------------------------------------------------
@task(name="1. Ingest Bronze (Raw)", retries=2)
def ingest_bronze():
    logger = get_run_logger()
    spark = get_spark_session()
    start_time = time.time()
    
    logger.info("🚀 Iniciando ingestão da camada Bronze...")
    
    # Exemplo: Leitura de CSVs locais (simulando S3/Lake)
    datasets = ["olist_orders_dataset", "olist_order_items_dataset", "olist_products_dataset"]
    
    total_rows = 0
    for table in datasets:
        try:
            # Lendo CSV
            file_path = f"01_base_dados/{table}.csv"
            df = spark.read.csv(file_path, header=True, inferSchema=True)
            
            # Escrevendo Parquet (Append Only - Idempotência seria tratada aqui ou na Silver)
            output_path = f"02_data_lake/bronze/{table}"
            df.write.mode("overwrite").parquet(output_path)
            
            rows = df.count()
            total_rows += rows
            logger.info(f"✅ Tabela {table} ingerida com sucesso: {rows} linhas.")
            
        except Exception as e:
            logger.error(f"❌ Falha ao ingerir {table}: {str(e)}")
            raise e

    duration = time.time() - start_time
    monitor.log("Bronze Ingestion", total_rows, duration)
    return True

# ---------------------------------------------------------------------------
# 2. SILVER LAYER (Limpeza e Deduplicação)
# ---------------------------------------------------------------------------
@task(name="2. Transform Silver (Clean)", retries=1)
def process_silver():
    # CORREÇÃO: Adicionado o logger que faltava
    logger = get_run_logger()
    spark = get_spark_session()
    start_time = time.time()
    
    logger.info("🧹 Silver: Deduplicação e Particionamento...")
    
    try:
        # Lendo da Bronze
        df_orders = spark.read.parquet("02_data_lake/bronze/olist_orders_dataset")
        df_items = spark.read.parquet("02_data_lake/bronze/olist_order_items_dataset")
        
        # Transformação: Join e Limpeza Básica
        df_joined = df_orders.join(df_items, on="order_id", how="inner")
        
        # Casting de Datas
        df_clean = df_joined.withColumn("order_purchase_timestamp", to_date(col("order_purchase_timestamp")))
        
        # Deduplicação (Lógica de Snapshot)
        df_clean = df_clean.dropDuplicates(["order_id", "product_id"])
        
        # Escrita particionada
        (df_clean.write
         .mode("overwrite")
         .partitionBy("order_status")
         .parquet("02_data_lake/silver/orders_enriched"))
        
        count = df_clean.count()
        duration = time.time() - start_time
        
        # Agora o logger existe e vai funcionar
        logger.info("Silver Finished", extra={"rows": count, "duration": duration})
        monitor.log("Silver (Clean)", count, duration)
        return True
        
    except Exception as e:
        logger.error(f"Silver Failed: {e}")
        raise e

# ---------------------------------------------------------------------------
# 3. QUALITY GATE (Great Expectations)
# ---------------------------------------------------------------------------
@task(name="3. Quality Gate (GX)")
def validate_silver():
    # CORREÇÃO: Logger removido pois não é usado aqui
    spark = get_spark_session()
    start_time = time.time()
    
    # Simulação de validação (Em prod, usaria o GX Context)
    df = spark.read.parquet("02_data_lake/silver/orders_enriched")
    
    # Regra: Não pode haver pedidos sem preço
    null_prices = df.filter(col("price").isNull()).count()
    
    if null_prices > 0:
        raise ValueError(f"❌ DATA QUALITY FAIL: Encontrados {null_prices} pedidos sem preço!")
    
    monitor.log("Quality Gate", df.count(), time.time() - start_time)
    return True

# ---------------------------------------------------------------------------
# 4. GOLD / AI ENRICHMENT
# ---------------------------------------------------------------------------
@task(name="4. AI Enrichment (Gemini)")
def enrich_products_ai():
    logger = get_run_logger()
    start_time = time.time()
    
    if not settings.GOOGLE_API_KEY:
        logger.warning("⚠️ API Key não encontrada. Pulando etapa de IA.")
        return False
        
    try:
        # Lógica simulada de batch
        genai.configure(api_key=settings.GOOGLE_API_KEY.get_secret_value())
        
        # CORREÇÃO: Variável 'model' removida pois não era usada na simulação
        time.sleep(2) # Simula processamento da API
        
        monitor.log("AI Enrichment", 150, time.time() - start_time) # 150 produtos simulados
        return True
        
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return False

# ---------------------------------------------------------------------------
# FLOW PRINCIPAL
# ---------------------------------------------------------------------------
@flow(name="Olist End-to-End Pipeline v2", log_prints=True)
def main_flow():
    # 1. Bronze
    ingest_bronze()
    
    # 2. Silver (Depende da Bronze)
    if process_silver():
        
        # 3. Validação (Se falhar, o fluxo para aqui)
        validate_silver()
        
        # 4. Enriquecimento (Roda após validação)
        enrich_products_ai()

if __name__ == "__main__":
    main_flow()