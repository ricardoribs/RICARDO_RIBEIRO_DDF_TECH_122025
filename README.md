# Case Técnico Dadosfera – Engenharia de Dados

**Autor:** Ricardo Ribeiro
**Data:** Dezembro/2025
**Contexto:** Implementação de Plataforma de Dados End-to-End para E-commerce.

---

## Visão Geral

Este projeto adota uma abordagem híbrida (Modern Data Stack), combinando planejamento estruturado com entregas incrementais. O objetivo foi transformar dados brutos de e-commerce em dados analíticos confiáveis, governados e prontos para consumo, cobrindo ingestão, qualidade, modelagem, analytics e automação.

---

## 🎥 Apresentação do Case (Item 10)

> 🔗 *Link para apresentação executiva (5–7 minutos)*

---

## Fase 0 – Planejamento

**Objetivo:** Definir escopo, estrutura do repositório, metodologia ágil e riscos do projeto.

| ID | Atividade                                   | Status    | Entrega                                     |
| -- | ------------------------------------------- | --------- | ------------------------------------------- |
| 00 | [Planejamento e Kanban](./00_planejamento/) | Concluído | Metodologia Ágil e Estrutura do Repositório |

---

## Fase 1 – Bronze (Ingestão)

**Objetivo:** Garantir aquisição, persistência e rastreabilidade dos dados brutos.

**Fonte:** Brazilian E-Commerce Public Dataset by Olist (>100k pedidos).

| ID | Atividade                                                      | Status    | Dependência |
| -- | -------------------------------------------------------------- | --------- | ----------- |
| 01 | [Seleção e Aquisição da Base Olist](./01_base_dados/)          | Concluído | 00          |
| 02 | [Ingestão via PostgreSQL (Neon) na Dadosfera](./08_pipelines/) | Concluído | 01          |

---

## Fase 2 – Silver (Qualidade e Enriquecimento)

**Objetivo:** Garantir consistência, qualidade dos dados e enriquecimento semântico.

| ID | Atividade                                                                | Status    | Dependência |
| -- | ------------------------------------------------------------------------ | --------- | ----------- |
| 03 | [Catalogação e Dicionário de Dados](./01_base_dados/dicionario_dados.md) | Concluído | 02          |
| 04 | [Data Quality com Great Expectations](./04_data_quality/)                | Concluído | 03          |
| 05 | [GenAI – Enriquecimento com Google Gemini](./05_genai_llm/)              | Concluído | 01, 02      |

---

## Fase 3 – Gold (Modelagem e Consumo)

**Objetivo:** Disponibilizar dados analíticos prontos para BI e produtos de dados.

| ID | Atividade                                                                | Status    | Dependência |
| -- | ------------------------------------------------------------------------ | --------- | ----------- |
| 06 | [Modelagem Dimensional – Star Schema (Kimball)](./06_modelagem/)         | Concluído | 04, 05      |
| 07 | [Dashboard Analítico (Metabase + Snowflake)](./07_analise_visualizacao/) | Concluído | 06          |
| 09 | [Data App – Streamlit Interativo](./09_data_app/)                        | Concluído | 07          |

---

## Fase 4 – Automação

**Objetivo:** Garantir reprodutibilidade, orquestração e confiabilidade dos pipelines.

| ID | Atividade                                              | Status    | Dependência |
| -- | ------------------------------------------------------ | --------- | ----------- |
| 08 | [Pipelines Automatizados com Prefect](./08_pipelines/) | Concluído | 06          |

---

## 🏗️ Diagrama de Arquitetura

O fluxo de dados segue uma arquitetura Lakehouse, com ingestão transacional via PostgreSQL (Neon) na plataforma Dadosfera, processamento e modelagem analítica, consumo em Snowflake e visualização no Metabase.

```mermaid
graph TD
    classDef bronze fill:#cd7f32,stroke:#333,stroke-width:2px,color:white;
    classDef silver fill:#c0c0c0,stroke:#333,stroke-width:2px,color:black;
    classDef gold fill:#ffd700,stroke:#333,stroke-width:2px,color:black;
    classDef plan fill:#40e0d0,stroke:#333,stroke-width:2px;

    subgraph Planejamento [Fase 0 – Planejamento]
        I0[Item 0: Planejamento & Kanban]:::plan
    end

    subgraph Bronze [Fase 1 – Bronze | Ingestão]
        I1[Item 1: Base Olist]:::bronze
        I2[Item 2: PostgreSQL (Neon) – Dadosfera]:::bronze
        I1 --> I2
    end

    subgraph Silver [Fase 2 – Silver | Qualidade & Enriquecimento]
        I3[Item 3: Catalogação]:::silver
        I4[Item 4: Data Quality]:::silver
        I5[Item 5: GenAI / NLP]:::silver
        I2 --> I3 --> I4 --> I5
    end

    subgraph Gold [Fase 3 – Gold | Modelagem & Consumo]
        I6[Item 6: Star Schema]:::gold
        I7[Item 7: BI – Metabase / Snowflake]:::gold
        I9[Item 9: Data App – Streamlit]:::gold
        I5 --> I6
        I6 --> I7
        I6 --> I9
    end

    subgraph Automacao [Fase 4 – Automação & Entrega]
        I8[Item 8: Pipelines Prefect]
        I10[Item 10: Apresentação Final]
        I8 -.-> I6
        I7 --> I10
        I9 --> I10
    end
```

**Observação:**
A ingestão ocorre via PostgreSQL (Neon) na plataforma Dadosfera. A camada Gold é consumida no Snowflake, que atua como engine analítica para construção dos dashboards no Metabase.

---

## Tech Stack & Estrutura do Repositório

* **00_planejamento/** – Metodologia ágil, Kanban e planejamento.
* **01_base_dados/** – Datasets brutos e dicionário de dados.
* **04_data_quality/** – Validação com Great Expectations.
* **05_genai_llm/** – Notebooks de NLP e LLM (Google Gemini).
* **06_modelagem/** – Modelagem dimensional, DDLs e diagramas.
* **07_analise_visualizacao/** – Dashboards, KPIs e queries analíticas.
* **08_pipelines/** – Orquestração e automação (Prefect / Dadosfera).
* **09_data_app/** – Aplicação interativa em Streamlit.

---

## Análise de Riscos Mitigados

1. **Rate Limit de API (GenAI):** mitigado com backoff exponencial e uso do modelo Gemini Flash.
2. **Qualidade dos Dados:** bloqueio de pipelines com Great Expectations (fail-fast).
3. **Segurança:** credenciais gerenciadas via variáveis de ambiente (não versionadas).

---

<div align="center">
  <h3>Desenvolvido por Ricardo Ribeiro</h3>
  <p>Case Técnico Dadosfera • Dezembro/2025</p>
</div>
