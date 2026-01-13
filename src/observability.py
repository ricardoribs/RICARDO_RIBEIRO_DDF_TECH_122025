import logging
from pythonjsonlogger import jsonlogger
from prefect.artifacts import create_markdown_artifact

# --- 1. CONFIGURAÇÃO DE LOGS JSON ---
def setup_structured_logging():
    """Transforma o logger padrão em JSON Estruturado."""
    logger = logging.getLogger()
    
    # Evita duplicação se já estiver configurado
    if not any(isinstance(h.formatter, jsonlogger.JsonFormatter) for h in logger.handlers):
        handler = logging.StreamHandler()
        # Define o formato JSON: Timestamp, Nível, Nome, Mensagem, Arquivo
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s %(filename)s'
        )
        handler.setFormatter(formatter)
        logger.handlers = [handler]
        logger.setLevel(logging.INFO)

# --- 2. DECORADOR DE MÉTRICAS ---
class TaskMetrics:
    """Classe auxiliar para acumular métricas durante o fluxo."""
    def __init__(self):
        self.metrics = []

    def log(self, stage: str, rows: int, duration_sec: float, status: str = "SUCCESS"):
        entry = {
            "stage": stage,
            "rows": rows,
            "duration": f"{duration_sec:.2f}s",
            "throughput": f"{int(rows/duration_sec)} rows/s" if duration_sec > 0 else "N/A",
            "status": "✅" if status == "SUCCESS" else "❌"
        }
        self.metrics.append(entry)

    def generate_report(self):
        """Cria um relatório Markdown bonito na UI do Prefect."""
        md_table = """
### 📊 Relatório de Execução do Pipeline

| Estágio | Status | Linhas Processadas | Duração | Throughput |
| :--- | :---: | :---: | :---: | :---: |
"""
        for m in self.metrics:
            md_table += f"| {m['stage']} | {m['status']} | {m['rows']:,} | {m['duration']} | {m['throughput']} |\n"

        # Cria o artefato na UI
        create_markdown_artifact(
            key="pipeline-performance-report",
            markdown=md_table,
            description="Métricas detalhadas de ingestão e processamento."
        )

# Instância global para ser usada no Flow
monitor = TaskMetrics()