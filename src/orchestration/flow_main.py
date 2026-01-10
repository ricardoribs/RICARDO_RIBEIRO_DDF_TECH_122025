from prefect import flow, task, get_run_logger
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, col, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
import google.generativeai as genai
import great_expectations as gx
import os

# [IMPORTANTE] Importando as configurações centralizadas
from src.config import settings

def get_spark_session():
    """
    Sessão Spark Otimizada.
    Configurações de memória e UI ajustadas para rodar liso no Docker/WSL.
    """
    return SparkSession.builder \
        .appName(settings.SPARK_APP_NAME) \
        .master(settings.SPARK_MASTER) \
        .config("spark.ui.showConsoleProgress", "false") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

@task(name="1. Ingest Bronze (Raw)", log_prints=True)
def ingest_bronze():
    """
    Ingestão Raw -> Bronze com Schema Enforcement.
    """
    logger = get_run_logger()
    spark = get_spark_session()
    
    logger.info(f"📥 Iniciando ingestão Bronze. Origem: {settings.RAW_DATA_DIR}")
    
    csv_path = settings.RAW_DATA_DIR / "olist_order_items_dataset.csv"
    
    # Verifica se arquivo existe (compatível com Pathlib)
    if not csv_path.exists():
        logger.error(f"❌ Arquivo não encontrado: {csv_path}")
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    # [PERFORMANCE] Definição Explícita de Schema (Evita leitura dupla do Spark)
    orders_schema = StructType([
        StructField("order_id", StringType(), False),
        StructField("order_item_id", IntegerType(), True),
        StructField("product_id", StringType(), True),
        StructField("seller_id", StringType(), True),
        StructField("shipping_limit_date", TimestampType(), True),
        StructField("price", FloatType(), True),
        StructField("freight_value", FloatType(), True)
    ])

    df = spark.read.csv(str(csv_path), header=True, schema=orders_schema)
    
    output_path = settings.LAKEHOUSE_DIR / "bronze" / "order_items"
    df.write.mode("overwrite").parquet(str(output_path))
    
    logger.info(f"✅ Bronze atualizada: {df.count()} linhas processadas.")

@task(name="2. Transform Silver (Clean)", log_prints=True)
def process_silver():
    """
    Refinamento Bronze -> Silver. Limpeza e Tipagem.
    """
    logger = get_run_logger()
    spark = get_spark_session()
    logger.info("✨ Iniciando processamento Silver...")
    
    bronze_path = settings.LAKEHOUSE_DIR / "bronze" / "order_items"
    df = spark.read.parquet(str(bronze_path))
    
    # Tratamento e Enriquecimento Técnico
    df_clean = df.withColumn("processed_at", current_timestamp()) \
                 .withColumn("price", col("price").cast(FloatType())) \
                 .withColumn("freight_value", col("freight_value").cast(FloatType()))
    
    output_path = settings.LAKEHOUSE_DIR / "silver" / "order_items"
    df_clean.write.mode("overwrite").parquet(str(output_path))
    logger.info("✅ Silver atualizada com sucesso.")

@task(name="3. Quality Gate (GX)", log_prints=True)
def validate_silver():
    """
    [Enterprise] Validação de Dados com Great Expectations.
    Define regras de negócio e bloqueia o pipeline se os dados estiverem ruins.
    """
    logger = get_run_logger()
    spark = get_spark_session()
    
    silver_path = settings.LAKEHOUSE_DIR / "silver" / "order_items"
    logger.info(f"🛡️ Iniciando Great Expectations na camada: {silver_path}")
    
    # 1. Carregar dados (Spark -> Pandas para validação ágil no GX)
    df_spark = spark.read.parquet(str(silver_path))
    df_pandas = df_spark.toPandas()
    
    # 2. Inicializar Contexto do GX (Em memória)
    context = gx.get_context()
    
    # 3. Criar Datasource e Asset
    datasource_name = "spark_silver_data"
    data_asset_name = "order_items"
    
    datasource = context.sources.add_pandas(datasource_name)
    asset = datasource.add_dataframe_asset(name=data_asset_name, dataframe=df_pandas)
    
    # 4. Definir Expectativas (Regras de Qualidade)
    suite_name = "silver_quality_gate"
    context.add_or_update_expectation_suite(expectation_suite_name=suite_name)
    
    batch_request = asset.build_batch_request()
    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name
    )
    
    logger.info("📐 Aplicando regras de validação...")
    
    # Regra 1: Preço deve ser positivo e razoável
    validator.expect_column_values_to_be_between(
        column="price", min_value=0.01, max_value=1000000
    )
    
    # Regra 2: Order ID e Product ID não podem ser nulos
    validator.expect_column_values_to_not_be_null(column="order_id")
    validator.expect_column_values_to_not_be_null(column="product_id")
    
    # Regra 3: Frete não pode ser negativo
    validator.expect_column_values_to_be_between(
        column="freight_value", min_value=0
    )

    # 5. Executar Validação
    checkpoint = context.add_or_update_checkpoint(
        name="silver_checkpoint",
        validator=validator,
    )
    
    checkpoint_result = checkpoint.run()
    
    # 6. Avaliar Sucesso/Frasso
    if not checkpoint_result.success:
        logger.error("❌ FALHA CRÍTICA: Great Expectations encontrou erros nos dados!")
        # Dica: O relatório HTML fica salvo na pasta 'gx/' dentro do container/volume
        raise ValueError("Data Quality Check Failed! Pipeline interrompido.")
    
    logger.info("✅ Quality Gate Aprovado! Integridade Enterprise Garantida.")

@task(name="4. AI Enrichment (Gemini)", log_prints=True)
def enrich_products_ai():
    """
    Enriquecimento com IA Generativa (Gemini).
    Gera descrições de marketing para produtos.
    """
    logger = get_run_logger()
    
    if not settings.GOOGLE_API_KEY:
        logger.warning("⚠️ Tarefa de IA pulada: GOOGLE_API_KEY não encontrada no .env")
        return

    logger.info("🤖 Iniciando Batch de Enriquecimento com IA...")
    spark = get_spark_session()
    
    # Configuração da API
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    # [MODELO ATUALIZADO] Usando versão flash para velocidade e disponibilidade
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Lê dados da Silver
    silver_path = settings.LAKEHOUSE_DIR / "silver" / "order_items"
    df = spark.read.parquet(str(silver_path))
    
    # [DEFESA TÉCNICA - RATE LIMITING]
    # Utilizamos .collect() + Loop Python propositalmente para respeitar o 
    # limite de RPM (Requests Per Minute) da API Gratuita do Gemini.
    # Em produção (Enterprise Tier), a abordagem correta seria Spark Pandas UDF.
    unique_products = df.select("product_id", "price").distinct().limit(5).collect()
    
    ai_results = []
    logger.info(f"🧠 Gerando descrições para {len(unique_products)} produtos (Amostra)...")
    
    for row in unique_products:
        pid = row['product_id']
        price = row['price']
        
        prompt = f"Crie uma descrição de marketing curta e atraente (max 100 caracteres) em PT-BR para um produto ID {pid} valor R$ {price}. Crie um nome criativo."
        
        try:
            response = model.generate_content(prompt)
            desc = response.text.strip()
            ai_results.append((pid, desc))
            logger.info(f"✨ Gerado: {desc}")
        except Exception as e:
            logger.error(f"⚠️ Erro na IA para {pid}: {e}")
            ai_results.append((pid, "Erro na geração"))

    # Persistência na Gold
    if ai_results:
        schema_ai = StructType([
            StructField("product_id", StringType(), True),
            StructField("ai_description", StringType(), True)
        ])
        
        df_ai = spark.createDataFrame(ai_results, schema=schema_ai)
        
        output_path = settings.LAKEHOUSE_DIR / "gold" / "ai_product_descriptions"
        df_ai.write.mode("overwrite").parquet(str(output_path))
        logger.info(f"✅ Enriquecimento concluído. Salvo em: {output_path}")

@flow(name="Olist ETL Pipeline (Full Stack)")
def main_flow():
    """
    Fluxo Principal Orquestrado pelo Prefect.
    """
    logger = get_run_logger()
    logger.info("🚀 Iniciando Pipeline: Ingestion -> Quality -> AI -> Analytics")
    
    # Execução Sequencial das Tarefas
    ingest_bronze()
    process_silver()
    
    # O Quality Gate agora é uma barreira real
    validate_silver()
    
    # Só roda se a qualidade passar
    enrich_products_ai()
    
    logger.info("🏁 Pipeline Finalizado com Sucesso!")

if __name__ == "__main__":
    main_flow()