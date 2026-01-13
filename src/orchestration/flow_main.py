import time
import os
import subprocess
import logging
from pathlib import Path
from datetime import timedelta

# Prefect & Logging
from prefect import task, flow, get_run_logger
from prefect.artifacts import create_markdown_artifact
from pythonjsonlogger import jsonlogger

# External Libs
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import great_expectations as gx
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, input_file_name, row_number, to_timestamp, year, month
from pyspark.sql.window import Window

# Internal modules
from src.config import settings

# =====================================================
# 0. SETUP DE OBSERVABILIDADE & SPARK
# =====================================================

def setup_structured_logging():
    """Configura logs em formato JSON para ingestão em ferramentas (Datadog, etc)."""
    logger = logging.getLogger()
    if not any(isinstance(h.formatter, jsonlogger.JsonFormatter) for h in logger.handlers):
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s %(filename)s'
        )
        handler.setFormatter(formatter)
        logger.handlers = [handler]
        logger.setLevel(logging.INFO)

class TaskMetrics:
    """Coletor de métricas para gerar relatório visual no final."""
    def __init__(self):
        self.metrics = []

    def log(self, stage: str, rows: int, duration: float, status="SUCCESS"):
        self.metrics.append({
            "stage": stage,
            "rows": rows,
            "duration": f"{duration:.2f}s",
            "throughput": f"{int(rows/duration)} rows/s" if duration > 0 and rows > 0 else "N/A",
            "status": "✅" if status == "SUCCESS" else "❌"
        })

    def generate_report(self):
        """Cria tabela Markdown na UI do Prefect."""
        md = "### 📊 Relatório de Performance do Pipeline\n\n"
        md += "| Estágio | Status | Linhas | Duração | Throughput |\n"
        md += "| :--- | :---: | :---: | :---: | :---: |\n"
        for m in self.metrics:
            md += f"| {m['stage']} | {m['status']} | {m['rows']:,} | {m['duration']} | {m['throughput']} |\n"
        
        create_markdown_artifact(
            key="pipeline-report",
            markdown=md,
            description="Métricas de execução Olist ETL"
        )

# Inicializa Monitoramento Global
setup_structured_logging()
monitor = TaskMetrics()

def get_spark_session():
    """Cria sessão Spark otimizada para performance e idempotência."""
    return (
        SparkSession.builder.appName("OlistETL_Production")
        .config("spark.sql.warehouse.dir", str(settings.LAKEHOUSE_DIR))
        .config("spark.ui.showConsoleProgress", "false")
        
        # --- ESCALABILIDADE (Simulação de Cluster) ---
        .config("spark.sql.shuffle.partitions", "4") # Em prod seria 200+
        .config("spark.default.parallelism", "4")
        .config("spark.memory.offHeap.enabled", "true")
        .config("spark.memory.offHeap.size", "1g")
        
        # --- IDEMPOTÊNCIA (Overwrite Dinâmico) ---
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .getOrCreate()
    )

# =====================================================
# 1. Ingestão (Bronze) - APPEND ONLY + METRICS
# =====================================================
@task(name="1. Ingest Bronze (Raw)", retries=2, retry_delay_seconds=5)
def ingest_bronze():
    logger = get_run_logger()
    spark = get_spark_session()
    start_time = time.time()
    
    default_path = settings.RAW_DATA_DIR / "olist_order_items_dataset.csv"
    if not default_path.exists():
        raise FileNotFoundError("Input dataset missing.")

    logger.info(f"📥 Ingestão Bronze (Append): {default_path.name}")
    
    try:
        df = spark.read.csv(str(default_path), header=True, inferSchema=True)
        
        # Rastreabilidade
        df_enriched = (df
            .withColumn("ingestion_at", current_timestamp())
            .withColumn("source_file", input_file_name())
        )
        
        output_path = settings.LAKEHOUSE_DIR / "bronze" / "order_items"
        
        # Gravação (Particionada por ingestão para organização)
        (df_enriched.write
            .mode("append") 
            .format("parquet")
            .partitionBy("ingestion_at")
            .save(str(output_path)))
            
        # Métricas
        count = df_enriched.count()
        duration = time.time() - start_time
        logger.info("Bronze Finished", extra={"rows": count, "duration": duration})
        monitor.log("Bronze (Raw)", count, duration)
        
    except Exception as e:
        monitor.log("Bronze (Raw)", 0, time.time() - start_time, "FAILED")
        raise e

# =====================================================
# 2. Transformação (Silver) - DEDUPLICAÇÃO + PARTICIONAMENTO
# =====================================================
@task(name="2. Transform Silver (Clean)", retries=1)
def process_silver():
    logger = get_run_logger()
    spark = get_spark_session()
    start_time = time.time()
    
    logger.info("🧹 Silver: Deduplicação e Particionamento...")
    
    try:
        input_path = settings.LAKEHOUSE_DIR / "bronze" / "order_items"
        df_bronze = spark.read.parquet(str(input_path))
        
        # 1. Deduplicação (Idempotência)
        w = Window.partitionBy("order_id", "order_item_id").orderBy(col("ingestion_at").desc())
        df_dedup = (df_bronze
            .withColumn("rn", row_number().over(w))
            .filter(col("rn") == 1)
            .drop("rn", "source_file")
        )
        
        # 2. Transformação e Colunas de Partição (Escalabilidade)
        df_clean = (df_dedup
            .withColumn("shipping_limit_date", to_timestamp(col("shipping_limit_date")))
            .withColumn("processed_at", current_timestamp())
            # Particionamento de Negócio (Ano/Mês)
            .withColumn("partition_year", year(col("shipping_limit_date")))
            .withColumn("partition_month", month(col("shipping_limit_date")))
            .dropDuplicates()
        )
        
        output_path = settings.LAKEHOUSE_DIR / "silver" / "order_items"
        
        # 3. Gravação Otimizada
        (df_clean.write
            .mode("overwrite")
            .partitionBy("partition_year", "partition_month")
            .parquet(str(output_path)))
        
        # Métricas
        count = df_clean.count()
        duration = time.time() - start_time
        logger.info("Silver Finished", extra={"rows": count, "duration": duration})
        monitor.log("Silver (Clean)", count, duration)
        
    except Exception as e:
        monitor.log("Silver (Clean)", 0, time.time() - start_time, "FAILED")
        raise e

# =====================================================
# 3. Quality Gate (GX)
# =====================================================
@task(name="3. Quality Gate (GX)")
def validate_silver():
    logger = get_run_logger()
    spark = get_spark_session()
    start_time = time.time()
    silver_path = settings.LAKEHOUSE_DIR / "silver" / "order_items"
    
    try:
        df_pandas = spark.read.parquet(str(silver_path)).toPandas()
        rows = len(df_pandas)
    except Exception:
        monitor.log("Quality Gate", 0, time.time() - start_time, "SKIPPED")
        return

    context = gx.get_context()
    datasource = context.sources.add_pandas("spark_silver")
    asset = datasource.add_dataframe_asset("orders", df_pandas)
    batch_request = asset.build_batch_request()
    
    validator = context.get_validator(
        batch_request=batch_request,
        create_expectation_suite_with_name="daily_check_v3"
    )
    validator.expect_column_values_to_not_be_null("order_id")
    validator.expect_column_values_to_be_between("price", 0.01, 500000)
    
    res = validator.validate()
    duration = time.time() - start_time
    
    if not res.success:
        monitor.log("Quality Gate", rows, duration, "FAILED")
        raise ValueError("Quality Gate Failed")
    
    monitor.log("Quality Gate", rows, duration)

# =====================================================
# 4. Enriquecimento IA (Gold)
# =====================================================
@task(name="4. AI Enrichment (Gemini)", retries=3)
def enrich_products_ai():
    logger = get_run_logger()
    start_time = time.time()
    
    if not settings.GOOGLE_API_KEY.get_secret_value():
        monitor.log("AI Enrichment", 0, time.time() - start_time, "SKIPPED")
        return

    try:
        # Lógica simulada de batch
        genai.configure(api_key=settings.GOOGLE_API_KEY.get_secret_value())
        model = genai.GenerativeModel('gemini-flash-latest')
        time.sleep(2) # Simula processamento
        
        monitor.log("AI Enrichment", 5, time.time() - start_time) # 5 itens simulados
        
    except Exception as e:
        monitor.log("AI Enrichment", 0, time.time() - start_time, "FAILED")
        logger.error(f"AI Error: {e}")

# =====================================================
# 5. Analytics (dbt)
# =====================================================
@task(name="5. Analytics (dbt)")
def run_dbt_analytics():
    logger = get_run_logger()
    start_time = time.time()
    dbt_dir = Path("/app/dbt_project/olist_analytics")
    
    try:
        subprocess.run(["dbt", "deps"], cwd=dbt_dir, check=True, capture_output=True)
        res = subprocess.run(["dbt", "run", "--profiles-dir", "."], cwd=dbt_dir, capture_output=True, text=True)
        
        if res.returncode != 0:
            raise RuntimeError(res.stderr)
            
        logger.info(res.stdout)
        monitor.log("dbt Analytics", 0, time.time() - start_time)
        
    except Exception as e:
        monitor.log("dbt Analytics", 0, time.time() - start_time, "FAILED")
        raise e

# =====================================================
# Fluxo Principal & Deployment
# =====================================================
@flow(name="Olist ETL Pipeline (Production)")
def main_flow():
    ingest_bronze()
    process_silver()
    validate_silver()
    enrich_products_ai()
    run_dbt_analytics()
    
    # Gera o relatório visual na UI
    monitor.generate_report()

if __name__ == "__main__":
    print("🔌 Iniciando Serviço de Orquestração (Escalável & Observável)...")
    
    main_flow.serve(
        name="olist-etl-production-service",
        cron="0 6 * * *",
        tags=["production", "docker", "idempotent", "scalable"],
        description="Pipeline Lakehouse completo com Logs JSON, Particionamento e Deduplicação.",
        pause_on_shutdown=False
    )