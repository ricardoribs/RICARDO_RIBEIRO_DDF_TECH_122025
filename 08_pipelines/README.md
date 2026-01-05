# Item 8 - Pipeline de Dados (ETL Automatizado)

Este módulo contém a orquestração do pipeline de processamento de dados, simulando a funcionalidade do módulo "Intelligence" da Dadosfera.

## Arquitetura do Pipeline

O pipeline foi desenvolvido em Python seguindo o padrão ETL (Extract, Transform, Load) com checkpoints de qualidade.

```mermaid
graph LR
    A[Ingestão (Bronze)] -->|Raw CSV| B(Validação Data Quality)
    B -->|Dados Validados| C{Transformação}
    C -->|Agregação SQL/Pandas| D[Camada Gold]
    D -->|Dataset Otimizado| E[Dashboard/Analytics]
    ```
---
## Etapas do Processo
1. Ingestão: Leitura do Data Lake (CSV local olist_order_items).

2. Qualidade (Data Quality): Validação de integridade referencial e valores numéricos (check de nulos e negativos).

3. Transformação: Agregação de dados para criar a visão Seller Performance (Soma de receita, contagem de pedidos).

4. Carga (Load): Persistência dos dados processados na pasta saida_gold.

## Como Executar
'''bash
python etl_pipeline.py

## Logs de Execução
O pipeline gera um arquivo de log (pipeline_log.txt) para auditoria de cada execução.
Exemplo de Log:
[2025-01-05 10:00:01] === INÍCIO DO PIPELINE DE DADOS ===
[2025-01-05 10:00:01] 🚀 Iniciando Step 1: Ingestão de Dados...
[2025-01-05 10:00:02] ✅ Ingestão concluída. Linhas carregadas: 112650
[2025-01-05 10:00:02] 🔍 Iniciando Step 2: Validação de Qualidade...
[2025-01-05 10:00:02] ✅ Validação concluída com sucesso.
[2025-01-05 10:00:02] ⚙️ Iniciando Step 3: Transformação e Modelagem...
[2025-01-05 10:00:03] 💾 Iniciando Step 4: Carga (Save)...
[2025-01-05 10:00:03] === PIPELINE FINALIZADO COM SUCESSO ===