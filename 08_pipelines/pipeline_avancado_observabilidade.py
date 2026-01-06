import logging
import json
import pandas as pd
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any

# --- Configuração de Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', '01_base_dados', 'olist_order_items_dataset.csv')

# ============================================
# 1. LOGGER ESTRUTURADO (JSON)
# ============================================
class StructuredLogger:
    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        self.execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f'pipeline_metrics_{self.execution_id}.json'
        
        # Configurar logging para arquivo
        # Limpar handlers anteriores para evitar duplicação
        root_logger = logging.getLogger()
        if root_logger.handlers:
            root_logger.handlers = []
            
        logging.basicConfig(
            filename=self.log_filename,
            level=logging.INFO,
            format='%(message)s'
        )
        print(f"📡 Iniciando Pipeline '{pipeline_name}' (ID: {self.execution_id})...")

    def log_event(self, step: str, status: str, metrics: Dict[str, Any]):
        """Registra evento em formato JSON e imprime no console"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "execution_id": self.execution_id,
            "pipeline": self.pipeline_name,
            "step": step,
            "status": status,
            "metrics": metrics
        }
        json_log = json.dumps(event)
        logging.info(json_log)
        print(f"[{step.upper()}] {status}: {metrics}")

# ============================================
# 2. FUNÇÕES DO PIPELINE (ETL REAL)
# ============================================
def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {DATA_PATH}")
    return pd.read_csv(DATA_PATH)

def validate_with_metrics(df):
    """Simula uma validação que retorna métricas detalhadas"""
    total = len(df)
    
    # Regra 1: Preço deve ser maior que 0
    invalid_price = df[df['price'] <= 0]
    failed_price = len(invalid_price)
    
    # Regra 2: Frete não negativo
    invalid_freight = df[df['freight_value'] < 0]
    failed_freight = len(invalid_freight)
    
    total_failures = failed_price + failed_freight
    # Se uma linha falhar em 2 regras, conta como 1 registro inválido (simplificado)
    valid_records = total - total_failures 
    
    return {
        "valid_records": valid_records,
        "checks_passed": (total * 2) - total_failures, # 2 regras por linha
        "checks_failed": total_failures
    }

def transform_data(df):
    """Agrega vendas por Vendedor (Exemplo de Transformação Gold)"""
    df_gold = df.groupby('seller_id').agg({
        'price': 'sum',
        'freight_value': 'sum',
        'order_id': 'count'
    }).reset_index()
    df_gold.rename(columns={'price': 'total_revenue', 'order_id': 'total_orders'}, inplace=True)
    return df_gold

def save_data(df):
    """Salva o resultado (mock)"""
    output_path = os.path.join(BASE_DIR, 'saida_gold', 'observabilidade_output.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path

# ============================================
# 3. RELATÓRIO HTML
# ============================================
def generate_metrics_report(execution_id: str):
    log_file = f'pipeline_metrics_{execution_id}.json'
    report_file = f'pipeline_report_{execution_id}.html'
    
    if not os.path.exists(log_file):
        print("Arquivo de log não encontrado para gerar relatório.")
        return

    with open(log_file, 'r') as f:
        events = [json.loads(line) for line in f]

    # Extração de Métricas Finais
    final_event = events[-1]
    status_icon = "✅" if final_event["status"] == "SUCCESS" else "❌"
    
    # CSS Simples
    css = """
    body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
    .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
    h1 { color: #333; }
    .metric { font-size: 1.2em; margin: 10px 0; }
    .json-box { background: #2d2d2d; color: #83c1fc; padding: 15px; border-radius: 5px; overflow-x: auto; }
    """

    html = f"""
    <html>
    <head><title>Relatório de Execução</title><style>{css}</style></head>
    <body>
        <div class="card">
            <h1>{status_icon} Pipeline Execution Report</h1>
            <p><strong>Execution ID:</strong> {execution_id}</p>
            <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="card">
            <h2>📊 Métricas Consolidadas</h2>
            <div class="metric">⏱️ Duração: <strong>{final_event['metrics'].get('duration_seconds', 0):.2f}s</strong></div>
            <div class="metric">📦 Registros Processados: <strong>{final_event['metrics'].get('records_ingested', 0)}</strong></div>
            <div class="metric">🚀 Throughput: <strong>{final_event['metrics'].get('throughput_records_per_sec', 0):.0f} rec/s</strong></div>
        </div>

        <div class="card">
            <h2>📜 Logs Detalhados (JSON Structured)</h2>
            <pre class="json-box">{json.dumps(events, indent=2)}</pre>
        </div>
    </body>
    </html>
    """
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"📄 Relatório HTML gerado: {report_file}")

# ============================================
# 4. EXECUÇÃO PRINCIPAL
# ============================================
def run_pipeline_with_observability():
    logger = StructuredLogger("olist_etl_production")
    start_time = datetime.now()
    
    metrics = {
        "records_ingested": 0,
        "records_validated": 0,
        "records_transformed": 0,
        "quality_score": 0.0
    }
    
    try:
        # Step 1: Ingestão
        logger.log_event("ingestao", "started", {})
        df = load_data()
        metrics["records_ingested"] = len(df)
        logger.log_event("ingestao", "completed", {"rows": len(df), "cols": len(df.columns)})
        
        # Step 2: Validação
        logger.log_event("validacao", "started", {})
        val_res = validate_with_metrics(df)
        metrics["records_validated"] = val_res["valid_records"]
        
        # Cálculo de Score de Qualidade
        total_checks = val_res["checks_passed"] + val_res["checks_failed"]
        quality_score = (val_res["checks_passed"] / total_checks * 100) if total_checks > 0 else 0
        metrics["quality_score"] = quality_score
        
        logger.log_event("validacao", "completed", {
            "score": quality_score, 
            "passed": val_res["checks_passed"], 
            "failed": val_res["checks_failed"]
        })

        # Fail-fast (Exemplo: Qualidade < 90% para o pipeline)
        if quality_score < 90.0:
            raise Exception(f"Qualidade dos dados insuficiente: {quality_score:.2f}%")

        # Step 3: Transformação
        logger.log_event("transformacao", "started", {})
        df_gold = transform_data(df)
        metrics["records_transformed"] = len(df_gold)
        logger.log_event("transformacao", "completed", {"rows_gold": len(df_gold)})

        # Step 4: Carga
        logger.log_event("carga", "started", {})
        path = save_data(df_gold)
        logger.log_event("carga", "completed", {"path": path})

        # Finalização
        duration = (datetime.now() - start_time).total_seconds()
        throughput = metrics["records_ingested"] / duration if duration > 0 else 0
        
        logger.log_event("pipeline", "SUCCESS", {
            **metrics,
            "duration_seconds": duration,
            "throughput_records_per_sec": throughput
        })
        
        # Gerar Relatório Visual
        generate_metrics_report(logger.execution_id)

    except Exception as e:
        logger.log_event("pipeline", "FAILED", {"error": str(e)})
        raise

if __name__ == "__main__":
    run_pipeline_with_observability()