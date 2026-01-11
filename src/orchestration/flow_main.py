from prefect import task, flow, get_run_logger
from src.etl.bronze_ingestion import BronzeIngestor
from src.etl.silver_cleaning import SilverCleaner
from src.config import settings
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import google.generativeai as genai
import great_expectations as gx
import os

def get_spark_session():
    return SparkSession.builder \
        .appName("OlistETL") \
        .config("spark.sql.warehouse.dir", "/app/09_lakehouse") \
        .getOrCreate()

@task(name="1. Ingest Bronze (Raw)", log_prints=True)
def ingest_bronze():
    logger = get_run_logger()
    spark = get_spark_session()
    
    csv_path = "/app/01_base_dados/olist_order_items_dataset.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    logger.info(f"📥 Iniciando ingestão Bronze. Origem: {os.path.dirname(csv_path)}")
    
    ingestor = BronzeIngestor(spark, settings.LAKEHOUSE_DIR)
    ingestor.ingest_orders(csv_path)
    
    logger.info("✅ Bronze atualizada.")

@task(name="2. Transform Silver (Clean)", log_prints=True)
def process_silver():
    logger = get_run_logger()
    spark = get_spark_session()
    
    logger.info("✨ Iniciando processamento Silver...")
    
    cleaner = SilverCleaner(spark, settings.LAKEHOUSE_DIR)
    df_clean = cleaner.clean_order_items()
    
    output_path = settings.LAKEHOUSE_DIR / "silver" / "order_items"
    df_clean.write.mode("overwrite").parquet(str(output_path))
    logger.info("✅ Silver atualizada com sucesso.")

@task(name="3. Quality Gate (GX)", log_prints=True)
def validate_silver():
    logger = get_run_logger()
    spark = get_spark_session()
    
    silver_path = settings.LAKEHOUSE_DIR / "silver" / "order_items"
    logger.info(f"🛡️ Iniciando Great Expectations na camada: {silver_path}")
    
    # 1. Carregar dados
    df_spark = spark.read.parquet(str(silver_path))
    df_pandas = df_spark.toPandas()
    
    # 2. Configurar Contexto
    context = gx.get_context()
    datasource_name = "spark_silver_data"
    data_asset_name = "order_items"
    
    datasource = context.sources.add_pandas(datasource_name)
    asset = datasource.add_dataframe_asset(name=data_asset_name, dataframe=df_pandas)
    
    # 3. Validar
    batch_request = asset.build_batch_request()
    validator = context.get_validator(
        batch_request=batch_request,
        create_expectation_suite_with_name="silver_quality_gate"
    )

    logger.info("📐 Aplicando regras de validação...")
    
    # Regra 1: Preço > 0
    validator.expect_column_values_to_be_between(column="price", min_value=0.01)
    # Regra 2: IDs não nulos
    validator.expect_column_values_to_not_be_null(column="order_id")
    validator.expect_column_values_to_not_be_null(column="product_id")

    # Executar
    checkpoint_result = validator.validate()
    
    if not checkpoint_result.success:
        logger.error("❌ FALHA CRÍTICA: Dados inválidos encontrados!")
        raise ValueError("Data Quality Check Failed!")
    
    logger.info("✅ Quality Gate Aprovado! Integridade Enterprise Garantida.")

@task(name="4. AI Enrichment (Gemini)", log_prints=True)
def enrich_products_ai():
    logger = get_run_logger()
    spark = get_spark_session()
    
    logger.info("🤖 Iniciando Batch de Enriquecimento com IA...")

    if not settings.GOOGLE_API_KEY:
        logger.warning("⚠️ Pulando IA: Chave de API não configurada.")
        return

    # [FIX] Limpeza da chave para evitar erro de Header do gRPC
    clean_key = settings.GOOGLE_API_KEY.strip()
    genai.configure(api_key=clean_key)
    
    model = genai.GenerativeModel('gemini-pro')

    silver_path = settings.LAKEHOUSE_DIR / "silver" / "order_items"
    df = spark.read.parquet(str(silver_path))
    
    # Amostra para demonstração (evita custo/tempo excessivo)
    unique_products = df.select("product_id", "price").distinct().limit(5).collect()
    
    logger.info(f"🧠 Gerando descrições para {len(unique_products)} produtos (Amostra)...")
    
    ai_results = []
    
    for row in unique_products:
        pid = row['product_id']
        price = row['price']
        
        prompt = f"""
        Atue como um Especialista em Marketing de E-commerce.
        Crie para o produto ID '{pid}' que custa R$ {price}:
        1. Um nome comercial criativo e curto.
        2. Uma descrição de venda persuasiva (máx 100 caracteres).
        Responda no formato: Nome | Descrição
        """
        
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            if "|" in text:
                name, desc = text.split("|", 1)
                ai_results.append((pid, name.strip(), desc.strip()))
                logger.info(f"✨ Gerado: {name.strip()}")
        except Exception as e:
            logger.error(f"Erro no Gemini para {pid}: {e}")

    # Salva Gold (Simulação)
    if ai_results:
        schema = "product_id STRING, marketing_name STRING, marketing_description STRING"
        df_ai = spark.createDataFrame(ai_results, schema=schema)
        
        gold_path = settings.LAKEHOUSE_DIR / "gold" / "ai_product_descriptions"
        df_ai.write.mode("overwrite").parquet(str(gold_path))
        logger.info(f"✅ Enriquecimento concluído. Salvo em: {gold_path}")

@flow(name="Olist ETL Pipeline (Full Stack)")
def main_flow():
    ingest_bronze()
    process_silver()
    validate_silver()
    enrich_products_ai()

if __name__ == "__main__":
    main_flow()