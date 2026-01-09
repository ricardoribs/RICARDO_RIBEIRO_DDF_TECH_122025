# ⚙️ Source Code: ETL & Orchestration

Este diretório contém o código fonte responsável pela ingestão, processamento e orquestração dos dados.

## 🛠️ Stack Tecnológica
* **Orquestração:** Prefect
* **Processamento:** Apache Spark (PySpark)
* **Infraestrutura:** Local (WSL 2)

## 📂 Estrutura
* `orchestration/`: Contém os fluxos (`flows`) e tarefas (`tasks`) do Prefect.
* `etl/`: (Opcional) Scripts auxiliares de transformação Spark.

## 🚀 Como Executar o Pipeline

Certifique-se de que o servidor do Prefect esteja rodando (`prefect server start`).

```bash
# A partir da raiz do projeto
python3 src/orchestration/flow_main.py
```

---

## O que este pipeline faz?
* Ingest Bronze: Lê arquivos CSV brutos (01_base_dados) e converte para Parquet (09_lakehouse/bronze).

* Process Silver: Lê a Bronze, aplica Schema Enforcement (tipagem forte) e salva particionado na Silver.