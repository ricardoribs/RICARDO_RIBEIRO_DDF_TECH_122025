# Item 8 - Pipeline de Dados (ETL Automatizado)

Este módulo contém a orquestração do pipeline de processamento de dados, simulando a funcionalidade do módulo "Intelligence" da Dadosfera.

## Arquitetura do Pipeline

O pipeline foi desenvolvido em Python seguindo o padrão ETL (Extract, Transform, Load) com checkpoints de qualidade.

```mermaid
graph LR

    A[Ingestao Bronze - CSV Olist] --> B[PostgreSQL Neon - Dadosfera]

    B --> C[Validacao Data Quality]
    C -->|OK| D[Transformacoes SQL]
    C -->|Falha| E[Alerta ou Log de Erro]

    D --> F[Star Schema - Camada Gold]
    F --> G[Snowflake - Analytics]

    G --> H[Metabase Dashboard]
    G --> I[Streamlit Data App]

```
---
## Etapas do Processo
1. Ingestão: Leitura do Data Lake (CSV local olist_order_items).

2. Qualidade (Data Quality): Validação de integridade referencial e valores numéricos (check de nulos e negativos).

3. Transformação: Agregação de dados para criar a visão Seller Performance (Soma de receita, contagem de pedidos).

4. Carga (Load): Persistência dos dados processados na pasta saida_gold.

## Como Executar

Execute o pipeline ETL localmente com o comando abaixo:

```bash
python etl_pipeline.py


## Logs de Execução
O pipeline gera um arquivo de log (pipeline_log.txt) para auditoria de cada execução.
Exemplo de Log:
[2025-01-05 10:00:01] === INICIO DO PIPELINE DE DADOS ===
[2025-01-05 10:00:01] Iniciando Step 1: Ingestao de Dados
[2025-01-05 10:00:02] Ingestao concluida. Linhas carregadas: 112650
[2025-01-05 10:00:02] Iniciando Step 2: Validacao de Qualidade
[2025-01-05 10:00:02] Validacao concluida com sucesso
[2025-01-05 10:00:02] Iniciando Step 3: Transformacao e Modelagem
[2025-01-05 10:00:03] Iniciando Step 4: Carga (Save)
[2025-01-05 10:00:03] PIPELINE FINALIZADO COM SUCESSO
---
## Diferencial: Observabilidade Avançada

Implementação de um **Logger Estruturado** (`pipeline_avancado_observabilidade.py`) que vai além de logs de texto simples.

### Recursos Implementados:
1.  **JSON Logging:** Logs estruturados legíveis por máquina (prontos para Datadog/Splunk).
2.  **Métricas de Negócio:** Coleta automática de:
    * Throughput (registros/segundo).
    * Quality Score (baseado em regras de validação).
    * Latência por etapa.
3.  **Fail-Fast:** Interrupção automática se o *Quality Score* cair abaixo de 95%.
4.  **Relatório Automático:** Geração de HTML pós-execução com resumo do job.

### Exemplo de Log JSON Gerado:
```json
{
  "timestamp": "2025-01-07T10:00:01",
  "execution_id": "20250107_1000",
  "pipeline": "olist_etl_production",
  "step": "pipeline",
  "status": "SUCCESS",
  "metrics": {
    "records_ingested": 112650,
    "quality_score": 100.0,
    "throughput_records_per_sec": 45320.5
  }
}
---
