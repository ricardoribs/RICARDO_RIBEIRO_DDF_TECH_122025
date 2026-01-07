# Case Técnico Dadosfera – Engenharia de Dados

![CI/CD Pipeline](https://github.com/ricardoribs/RICARDO_RIBEIRO_DDF_TECH_122025/actions/workflows/ci_cd.yml/badge.svg)
![Stack](https://img.shields.io/badge/Stack-PySpark%20|%20WSL2%20|%20Streamlit-blue)
![Architecture](https://img.shields.io/badge/Architecture-Medallion%20Lakehouse-orange)

**Autor:** Ricardo Ribeiro  
**Data:** Dezembro/2025 (Atualizado em Jan/2026)  
**Contexto:** Implementação de Plataforma de Dados End-to-End para E-commerce

---

## Visão Geral e Evolução da Arquitetura

Este projeto adota uma abordagem híbrida (**Modern Data Stack**). Inicialmente concebido com scripts Pandas e bancos relacionais, o projeto foi **migrado para uma Arquitetura Big Data** utilizando **Apache Spark (PySpark)** rodando em ambiente **Linux (WSL 2)**. 

O objetivo atual é simular um ambiente produtivo escalável, transformando dados brutos em um **Lakehouse (Medallion Architecture)**, cobrindo ingestão, schema enforcement, particionamento e analytics com IA.

---

## Fase 0 – Planejamento

**Objetivo:** Definir escopo, estrutura do repositório, metodologia ágil e riscos do projeto.

| ID | Atividade | Status | Entrega |
| :-- | :--- | :--- | :--- |
| 00 | [Planejamento e Kanban](./00_planejamento/) | Concluído | Metodologia Ágil e Estrutura do Repositório |

---

## Fase 1 – Bronze (Ingestão Big Data)

**Objetivo:** Garantir aquisição, persistência e rastreabilidade dos dados brutos em formato otimizado.

**Fonte:** Brazilian E-Commerce Public Dataset by Olist (>100k pedidos)

| ID | Atividade | Status | Dependência |
| :-- | :--- | :--- | :--- |
| 01 | [Seleção e Aquisição da Base Olist](./01_base_dados/) | Concluído | 00 |
| 02 | [Ingestão via PySpark (Lakehouse Local)](./08_pipelines/) | **Atualizado** | 01 |

---

## Fase 2 – Silver (Refinamento e Schema)

**Objetivo:** Garantir consistência, tipagem forte e particionamento dos dados para performance.

| ID | Atividade | Status | Dependência |
| :-- | :--- | :--- | :--- |
| 03 | [Catalogação e Dicionário de Dados](./01_base_dados/dicionario_dados.md) | Concluído | 02 |
| 04 | [Schema Enforcement & Limpeza (Spark)](./08_pipelines/) | **Atualizado** | 03 |
| 05 | [GenAI – Enriquecimento via App](./09_data_app/) | Concluído | 01, 02 |

---

## Fase 3 – Gold (Agregação e Consumo)

**Objetivo:** Disponibilizar dados analíticos (KPIs) prontos para visualização e produtos de IA.

| ID | Atividade | Status | Dependência |
| :-- | :--- | :--- | :--- |
| 06 | [Modelagem Dimensional e Agregação Spark](./08_pipelines/) | **Atualizado** | 04 |
| 07 | [Dashboard Analítico Integrado (Streamlit)](./09_data_app/) | **Atualizado** | 06 |
| 09 | [Data App – GenAI + Analytics](./09_data_app/) | Concluído | 07 |

---

## Fase 4 – Automação e Infraestrutura

**Objetivo:** Garantir execução em ambiente Linux (WSL) e orquestração de jobs Spark.

| ID | Atividade | Status | Dependência |
| :-- | :--- | :--- | :--- |
| 08 | [Pipeline PySpark (Medallion Architecture)](./08_pipelines/) | **Atualizado** | 06 |

---

## Testes Automatizados

O projeto conta com uma suíte robusta de testes utilizando **pytest**, adaptada para validar sessões Spark e lógica de transformação:

* **Unit Tests:** Verificam a lógica de agregação do PySpark.
* **Ambiente:** Testes rodam em CI/CD instalando Java e Spark automaticamente.

### Como executar

```bash
pytest tests/ -v
```

---

## Diagrama de Arquitetura (Lakehouse)
O fluxo de dados segue uma arquitetura Medallion, com processamento distribuído via Spark no WSL, persistência em Parquet e consumo via Streamlit com integração de IA.


```mermaid
graph TD
    classDef plan fill:#40e0d0,stroke:#333,stroke-width:2px,color:white;
    classDef bronze fill:#cd7f32,stroke:#333,stroke-width:2px,color:white;
    classDef silver fill:#c0c0c0,stroke:#333,stroke-width:2px,color:black;
    classDef gold fill:#ffd700,stroke:#333,stroke-width:2px,color:black;

    subgraph Planejamento["Fase 0 - Planejamento"]
        P0["Item 0: Planejamento & PMBOK - Definição de escopo, cronograma e riscos"]:::plan
    end

    subgraph Ingestao["Fase 1 - Processamento Spark (WSL)"]
        B1["Fonte Olist (CSV) - Dados brutos"]:::bronze
        B2["PySpark Ingestion (Bronze Layer)"]:::bronze
        B1 -->|Extração e Load| B2
    end

    subgraph Refinamento["Fase 2 - Tratamento (Silver)"]
        S1["Schema Enforcement - Validação de colunas e tipos"]:::silver
        S2["Particionamento (Ano/Mês) - Organização para análise"]:::silver
        B2 -->|Transformação| S1 -->|Preparação| S2
    end

    subgraph Consumo["Fase 3 - Agregação (Gold) & App"]
        G1["KPIs Agregados (Parquet) - Dados prontos para análise"]:::gold
        G2["Streamlit (Dashboard) - Visualização interativa"]:::gold
        G3["GenAI (Gemini + Stable Diffusion) - Geração de insights visuais"]:::gold
        S2 -->|Agregação| G1
        G1 -->|Visualização| G2
        G2 --> G3
```

---

* Observação: A infraestrutura foi migrada para Linux (WSL) para eliminar dependências de winutils e simular um cluster Spark real.

---

## Tech Stack & Estrutura do Repositório
* 00_planejamento/ – Metodologia ágil, Kanban e planejamento

* 01_base_dados/ – Datasets brutos (CSV)

* 08_pipelines/ – CORE: Scripts PySpark (Bronze/Silver/Gold)

* 09_data_app/ – Aplicação Streamlit com Dashboard e IA Generativa

* 09_lakehouse/ – (Local) Estrutura de pastas do Data Lake

* tests/ – Testes unitários para Spark

---

## Análise de Riscos Mitigados

* Escalabilidade: Migração de Pandas para Spark permite processar terabytes de dados.

* Rate Limit de API (GenAI): Implementado sistema de Fallback (Gemini -> Prompt Manual -> Hugging Face) para garantir resiliência.

* Segurança: Uso de .gitignore rigoroso para evitar vazamento de dados do Lakehouse

---

<div align="center"> <h3>Desenvolvido por Ricardo Ribeiro</h3> <p>Case Técnico Dadosfera • Dezembro/2025 • Atualizado Jan/2026</p> </div>

---