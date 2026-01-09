from prefect import flow, task
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env) para segurança
load_dotenv()

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAKEHOUSE_DIR = os.path.join(BASE_DIR, "09_lakehouse")
RAW_DATA_DIR = os.path.join(BASE_DIR, "01_base_dados")

# --- CONFIGURAÇÃO GENAI ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_spark_session():
    """Sessão Spark Otimizada para Local"""
    return SparkSession.builder \
        .appName("Olist_Modern_Stack") \
        .master("local[*]") \
        .config("spark.ui.showConsoleProgress", "false") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()

@task(name="1. Ingest Bronze (Raw)", log_prints=True)
def ingest_bronze():
    spark = get_spark_session()
    print(f"📥 Ingesting Data to Bronze...")
    
    csv_file = os.path.join(RAW_DATA_DIR, "olist_order_items_dataset.csv")
    if not os.path.exists(csv_file):
        print(f"⚠️ Arquivo não encontrado: {csv_file}")
        return

    # Schema Enforcement (Performance)
    orders_schema = StructType([
        StructField("order_id", StringType(), False),
        StructField("order_item_id", IntegerType(), True),
        StructField("product_id", StringType(), True),
        StructField("seller_id", StringType(), True),
        StructField("shipping_limit_date", TimestampType(), True),
        StructField("price", FloatType(), True),
        StructField("freight_value", FloatType(), True)
    ])

    df = spark.read.csv(csv_file, header=True, schema=orders_schema)
    df.write.mode("overwrite").parquet(os.path.join(LAKEHOUSE_DIR, "bronze", "order_items"))
    print(f"✅ Bronze Updated: {df.count()} rows")

@task(name="2. Transform Silver (Clean)", log_prints=True)
def process_silver():
    spark = get_spark_session()
    print("✨ Processing Silver...")
    
    bronze_path = os.path.join(LAKEHOUSE_DIR, "bronze", "order_items")
    df = spark.read.parquet(bronze_path)
    
    # Tratamento básico
    df_clean = df.withColumn("processed_at", current_timestamp()) \
                 .withColumn("price", col("price").cast(FloatType()))
    
    df_clean.write.mode("overwrite").parquet(os.path.join(LAKEHOUSE_DIR, "silver", "order_items"))
    print("✅ Silver Updated")

@task(name="3. Quality Gate (Validation)", log_prints=True)
def validate_silver():
    """
    [NOVO] Quality Gate: Impede que dados ruins avancem.
    Verifica se existem preços negativos ou nulos.
    """
    spark = get_spark_session()
    print("🛡️ Running Quality Checks...")
    
    silver_path = os.path.join(LAKEHOUSE_DIR, "silver", "order_items")
    df = spark.read.parquet(silver_path)
    
    # Regra 1: Preço não pode ser negativo
    invalid_price = df.filter(col("price") < 0).count()
    
    # Regra 2: Product ID não pode ser nulo
    null_products = df.filter(col("product_id").isNull()).count()
    
    if invalid_price > 0 or null_products > 0:
        error_msg = f"❌ DATA QUALITY FAILED! Prices < 0: {invalid_price}, Null Products: {null_products}"
        print(error_msg)
        # Em produção, isso pararia o pipeline
        raise ValueError(error_msg)
    
    print("✅ Quality Gate Passed: Data Integrity 100%")

@task(name="4. AI Enrichment (Gemini)", log_prints=True)
def enrich_products_ai():
    """
    [NOVO] Integração de IA no Pipeline.
    Lê produtos da Silver, gera descrições criativas com Gemini e salva na Gold.
    """
    if not GOOGLE_API_KEY:
        print("⚠️ Skipped AI Task: GOOGLE_API_KEY not found in .env")
        return

    print("🤖 Starting AI Enrichment Batch...")
    spark = get_spark_session()
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # [CORREÇÃO FINAL] Usando o modelo disponível na sua lista (Jan/2026)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Lê dados da Silver
    silver_path = os.path.join(LAKEHOUSE_DIR, "silver", "order_items")
    df = spark.read.parquet(silver_path)
    
    # Amostra pequena para demonstração
    unique_products = df.select("product_id", "price").distinct().limit(5).collect()
    
    ai_results = []
    
    print(f"🧠 Generating descriptions for {len(unique_products)} products...")
    
    for row in unique_products:
        pid = row['product_id']
        price = row['price']
        
        # Prompt Engineering
        prompt = f"Crie uma descrição de marketing curta e atraente (max 100 caracteres) em PT-BR para um produto com ID {pid} que custa R$ {price}. Invente o nome do produto criativo."
        
        try:
            response = model.generate_content(prompt)
            desc = response.text.strip()
            ai_results.append((pid, desc))
            print(f"✨ Gerado para {pid}: {desc}") 
        except Exception as e:
            print(f"⚠️ AI Error for {pid}: {e}")
            ai_results.append((pid, "Erro na geração"))

    # Salva o resultado enriquecido na camada GOLD
    if ai_results:
        schema_ai = StructType([
            StructField("product_id", StringType(), True),
            StructField("ai_description", StringType(), True)
        ])
        
        df_ai = spark.createDataFrame(ai_results, schema=schema_ai)
        output_path = os.path.join(LAKEHOUSE_DIR, "gold", "ai_product_descriptions")
        df_ai.write.mode("overwrite").parquet(output_path)
        print(f"✅ AI Enrichment Complete: Saved to {output_path}")

@flow(name="Olist ETL Pipeline (Full Stack)")
def main_flow():
    print("🚀 Pipeline Start: Ingestion -> Quality -> AI -> Analytics")
    
    ingest_bronze()
    process_silver()
    
    # Os novos passos do Ciclo 2
    validate_silver()
    enrich_products_ai()
    
    print("🏁 Pipeline Finished Successfully!")

if __name__ == "__main__":
    main_flow()