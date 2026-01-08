import sys
import os
import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, FloatType

# --- Configuração ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', '01_base_dados', 'olist_order_items_dataset.csv')
REPORT_FILE = os.path.join(BASE_DIR, 'relatorio_qualidade_spark.json')

def init_spark():
    return SparkSession.builder \
        .appName("DataQuality_Check") \
        .master("local[*]") \
        .getOrCreate()

def run_spark_quality():
    print("🚀 Iniciando Data Quality Nativo com PySpark...")
    spark = init_spark()
    
    # 1. Ingestão
    try:
        df = spark.read.csv(DATA_PATH, header=True, inferSchema=True)
        print(f"📊 Dataset carregado. Total de linhas: {df.count()}")
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return

    # 2. Definição de Regras e Verificações
    validations = []
    
    # Regra 1: Não pode haver IDs nulos
    null_ids = df.filter(F.col("order_id").isNull() | F.col("product_id").isNull()).count()
    validations.append({
        "rule": "Integridade de Chaves",
        "description": "order_id e product_id não podem ser nulos",
        "status": "PASS" if null_ids == 0 else "FAIL",
        "failed_count": null_ids
    })

    # Regra 2: Preço deve ser maior que 0 (Casting para garantir numérico)
    df = df.withColumn("price", F.col("price").cast(FloatType()))
    invalid_prices = df.filter(F.col("price") <= 0).count()
    validations.append({
        "rule": "Regra de Negócio - Preço",
        "description": "O preço deve ser estritamente maior que 0",
        "status": "PASS" if invalid_prices == 0 else "FAIL",
        "failed_count": invalid_prices
    })

    # Regra 3: Frete não pode ser negativo
    df = df.withColumn("freight_value", F.col("freight_value").cast(FloatType()))
    negative_freight = df.filter(F.col("freight_value") < 0).count()
    validations.append({
        "rule": "Regra de Negócio - Frete",
        "description": "O valor do frete não pode ser negativo",
        "status": "PASS" if negative_freight == 0 else "FAIL",
        "failed_count": negative_freight
    })

    # Regra 4: Validação Estatística (Média de Preço)
    avg_price = df.select(F.avg("price")).first()[0]
    validations.append({
        "rule": "Consistência Estatística",
        "description": "Média de preço deve estar entre 50 e 250",
        "status": "PASS" if 50 <= avg_price <= 250 else "WARNING",
        "observed_value": round(avg_price, 2)
    })

    # 3. Gerar Relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "framework": "PySpark Native",
        "total_records": df.count(),
        "results": validations
    }

    # Exibir no Console
    print("\n" + "="*50)
    print("🏆 RESULTADO DO DATA QUALITY (SPARK)")
    print("="*50)
    for v in validations:
        icon = "✅" if v["status"] == "PASS" else ("⚠️" if v["status"] == "WARNING" else "❌")
        print(f"{icon} {v['rule']}: {v['status']}")
        if v["status"] != "PASS":
            print(f"   Detalhe: {v.get('failed_count', v.get('observed_value'))} falhas/valor")
    print("="*50)

    # Salvar JSON
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Relatório salvo em: {REPORT_FILE}")
    
    spark.stop()

if __name__ == "__main__":
    run_spark_quality()