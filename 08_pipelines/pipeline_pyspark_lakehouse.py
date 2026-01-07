# pipeline_pyspark_lakehouse.py
# =====================================================
# Olist Lakehouse Pipeline - Production Grade
# Author: Ricardo Ribeiro
# =====================================================

import os
import sys
import logging
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, FloatType

# =====================================================
# CONFIGURAÇÕES GERAIS
# =====================================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR = os.path.join(BASE_DIR, '01_base_dados')
LAKEHOUSE_DIR = os.path.join(BASE_DIR, '09_lakehouse')
BRONZE_DIR = os.path.join(LAKEHOUSE_DIR, 'bronze')
SILVER_DIR = os.path.join(LAKEHOUSE_DIR, 'silver')
GOLD_DIR = os.path.join(LAKEHOUSE_DIR, 'gold')

DATASETS = {
    'orders': 'olist_orders_dataset.csv',
    'customers': 'olist_customers_dataset.csv',
    'order_items': 'olist_order_items_dataset.csv',
    'products': 'olist_products_dataset.csv'
}

# =====================================================
# LOGGING
# =====================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('olist_lakehouse')

# =====================================================
# SCHEMAS EXPLÍCITOS (SILVER)
# =====================================================
ORDER_SCHEMA = StructType([
    StructField('order_id', StringType(), False),
    StructField('customer_id', StringType(), True),
    StructField('order_status', StringType(), True),
    StructField('order_purchase_timestamp', TimestampType(), True),
    StructField('order_approved_at', TimestampType(), True),
    StructField('order_delivered_carrier_date', TimestampType(), True),
    StructField('order_delivered_customer_date', TimestampType(), True),
    StructField('order_estimated_delivery_date', TimestampType(), True)
])

# =====================================================
# SPARK SESSION
# =====================================================

def create_spark_session():
    logger.info('Iniciando Spark Session...')
    return (
        SparkSession.builder
        .appName('Olist_Lakehouse_Pipeline')
        .config('spark.sql.session.timeZone', 'UTC')
        .config('spark.sql.sources.partitionOverwriteMode', 'dynamic')
        .getOrCreate()
    )

# =====================================================
# UTILITÁRIOS
# =====================================================

def validate_path(path: str):
    if not os.path.exists(path):
        logger.error(f'Caminho não encontrado: {path}')
        sys.exit(1)


def write_parquet(df, path, partition_cols=None, mode='overwrite'):
    writer = df.write.mode(mode)
    if partition_cols:
        writer = writer.partitionBy(partition_cols)
    writer.parquet(path)

# =====================================================
# BRONZE - INGESTÃO RAW + DATA QUALITY BÁSICO
# =====================================================

def process_bronze(spark: SparkSession):
    logger.info('[BRONZE] Ingestão RAW + Validação básica')
    os.makedirs(BRONZE_DIR, exist_ok=True)

    for name, file in DATASETS.items():
        path = os.path.join(RAW_DIR, file)
        validate_path(path)
        logger.info(f'[BRONZE] Lendo {file}')

        df = (
            spark.read
            .option('header', True)
            .option('inferSchema', True)
            .csv(path)
        )

        if df.count() == 0:
            raise ValueError(f'Dataset vazio detectado: {file}')

        write_parquet(df, os.path.join(BRONZE_DIR, name))

# =====================================================
# SILVER - LIMPEZA, TIPAGEM E PARTICIONAMENTO
# =====================================================

def process_silver(spark: SparkSession):
    logger.info('[SILVER] Limpeza, tipagem e particionamento')
    os.makedirs(SILVER_DIR, exist_ok=True)

    orders_raw = spark.read.parquet(os.path.join(BRONZE_DIR, 'orders'))

    orders = (
        spark.createDataFrame(orders_raw.rdd, ORDER_SCHEMA)
        .dropna(subset=['order_id', 'order_purchase_timestamp'])
        .withColumn('order_year', year(col('order_purchase_timestamp')))
        .withColumn('order_month', month(col('order_purchase_timestamp')))
    )

    write_parquet(
        orders,
        os.path.join(SILVER_DIR, 'orders'),
        partition_cols=['order_year', 'order_month']
    )

# =====================================================
# GOLD - AGREGAÇÕES ANALÍTICAS
# =====================================================

def process_gold(spark: SparkSession):
    logger.info('[GOLD] Agregações analíticas')
    os.makedirs(GOLD_DIR, exist_ok=True)

    orders = spark.read.parquet(os.path.join(SILVER_DIR, 'orders'))

    pedidos_mes = (
        orders
        .groupBy('order_year', 'order_month')
        .count()
        .orderBy('order_year', 'order_month')
    )

    write_parquet(pedidos_mes, os.path.join(GOLD_DIR, 'pedidos_por_mes'))

# =====================================================
# PIPELINE ORQUESTRADOR
# =====================================================

def main():
    start_time = datetime.utcnow()
    spark = create_spark_session()

    try:
        process_bronze(spark)
        process_silver(spark)
        process_gold(spark)
        logger.info('Pipeline finalizado com sucesso 🚀')
    except Exception:
        logger.exception('Erro fatal no pipeline')
        raise
    finally:
        spark.stop()
        duration = (datetime.utcnow() - start_time).seconds
        logger.info(f'Pipeline executado em {duration}s')


if __name__ == '__main__':
    main()
