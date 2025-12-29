# Planejamento do Projeto - Case Dadosfera

**Metodologia:** Híbrida (Checklist Sequencial + Boas Práticas do PMBOK)
**Gerente de Projeto:** Ricardo
**Data de Início:** 29/12/2025

---

## Visão Arquitetural

O projeto foi estruturado seguindo uma abordagem em **camadas de dados (Bronze, Silver e Gold)**, visando escalabilidade, governança e qualidade desde a ingestão até o consumo analítico.

* **Bronze:** Dados brutos ingeridos
* **Silver:** Dados tratados, validados e enriquecidos (incluindo GenAI)
* **Gold:** Dados modelados para analytics, dashboards e Data Apps

---

## 1. Cronograma e Estimativas (Gantt Simplificado)

| ID     | Atividade                                             | Estimativa | Status       | Dependência |
| ------ | ----------------------------------------------------- | ---------- | ------------ | ----------- |
| **00** | Planejamento e Estruturação do Repositório            | 1h         | Concluído    | -           |
| **01** | Seleção e Aquisição de Dados (>100k rows)             | 2h         | Em andamento | 00          |
| **02** | Ingestão na Dadosfera (Carga + Microtransformação)    | 3h         | Pendente     | 01          |
| **03** | Catalogação e Criação do Dicionário de Dados          | 2h         | Pendente     | 02          |
| **04** | Análise de Qualidade de Dados (Data Quality)          | 4h         | Pendente     | 03          |
| **05** | Processamento com GenAI (Criação de Features via LLM) | 5h         | Pendente     | 01, 02      |
| **06** | Modelagem de Dados Analítica (Star Schema)            | 4h         | Pendente     | 04, 05      |
| **07** | Análise de Dados e Construção de Dashboard (Metabase) | 5h         | Pendente     | 06          |
| **08** | Construção de Pipelines de Dados (Automação)          | 4h         | Pendente     | 06          |
| **09** | Desenvolvimento de Data Apps (Streamlit)              | 6h         | Pendente     | 07          |
| **10** | Gravação e Preparação da Apresentação Final           | 4h         | Pendente     | 0009        |

---

## 2. Análise de Riscos (PMBOK)

| Risco                                             | Probabilidade | Impacto | Plano de Mitigação                                                                                            |
| ------------------------------------------------- | ------------- | ------- | ------------------------------------------------------------------------------------------------------------- |
| **Rate Limit da API OpenAI**                      | Alta          | Médio   | Implementar backoff exponencial, processamento em batch e fallback com redução de contexto ou execução local. |
| **Inconsistência na Ingestão de Dados**           | Média         | Alto    | Validação de schema, constraints e tipagem antes da persistência utilizando Pandas e Great Expectations.      |
| **Falha na Integração com a Dadosfera**           | Baixa         | Alto    | Consulta à documentação oficial, fóruns técnicos e acionamento de suporte, se disponível.                     |
| **Dados de Baixa Qualidade Impactarem o Consumo** | Média         | Médio   | Implementação de camada Silver com dados tratados antes do consumo pelo Metabase e Streamlit.                 |
| **Estouro do Tempo de Apresentação**              | Alta          | Baixo   | Roteiro objetivo focado nos diferenciais técnicos, arquitetura e decisões de engenharia.                      |

> Os riscos foram tratados com foco em **mitigação preventiva**, priorizando qualidade e confiabilidade do pipeline de dados.

---

## 3. Custos Estimados

* **Infraestrutura Cloud (Dadosfera):** Utilização do trial gratuito.
* **API OpenAI (GPT-3.5 / GPT-4):** Estimativa de até **US$ 2.00** para geração de features e processamento textual.
* **Google Colab:** Versão gratuita (uso eventual de GPU T4, se necessário).
* **Esforço estimado:** Aproximadamente **40 horas**, distribuídas entre ingestão, qualidade, modelagem, automação e analytics.

---

## 4. Indicadores de Sucesso (KPIs)

* Percentual de registros válidos após validações de Data Quality
* Tempo de execução dos pipelines de ingestão e transformação
* Latência de atualização dos dashboards
* Aderência do modelo analítico ao Star Schema
* Reprodutibilidade e automação do fluxo de dados

---

Este planejamento visa demonstrar capacidade técnica, organização de projeto e maturidade em engenharia e análise de dados em um ambiente próximo ao corporativo.
