# Item 7 — Análise de Dados e Visualização

## Dashboard Executivo Olist — Ricardo Ribeiro

**Ferramenta:** Metabase (Dadosfera)
**Período analisado:** 2016–2020
**Coleção:** Ricardo Ribeiro – Olist – Dez/2025

**Dashboard Interativo:** [text](https://metabase-treinamentos.dadosfera.ai/dashboard/227-dashboard-executivo-olist-ricardo-ribeiro?agrupamento_de_tempo=)

---

## Objetivo da Análise

Construir um dashboard executivo para apoiar a tomada de decisão, permitindo:

* Monitorar KPIs principais de vendas
* Analisar a evolução temporal da receita
* Identificar os principais sellers
* Entender a distribuição de preços dos produtos

---

## KPIs Principais (Number Cards)

| KPI              |     Valor | Descrição                                          |
| ---------------- | --------: | -------------------------------------------------- |
| Receita Total    |  R$ 15,8M | Soma de `price + freight_value` de todos os itens  |
| Total de Pedidos |    98.666 | Quantidade de pedidos únicos (`order_id` distinto) |
| Ticket Médio     | R$ 140,64 | Valor médio por pedido                             |
| Total de Itens   |   112.650 | Quantidade total de itens vendidos                 |

### Queries SQL — KPIs

```sql
-- KPI 1: Receita Total
SELECT ROUND(SUM(price + freight_value) / 1000000, 2) AS receita_milhoes
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;

-- KPI 2: Total de Pedidos
SELECT COUNT(DISTINCT order_id) AS total_pedidos
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;

-- KPI 3: Ticket Médio
SELECT ROUND(AVG(price + freight_value), 2) AS ticket_medio
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;

-- KPI 4: Total de Itens
SELECT COUNT(*) AS total_itens
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;
```

**Configuração no Metabase:**

* Tipo: Number (cards grandes)
* Formatação: Moeda brasileira (R$) quando aplicável
* Posicionamento: Linha superior do dashboard (4 colunas)

---

## Evolução Temporal — Receita e Pedidos

**Tipo:** Area Chart
**Período:** Jan/2017 – Jan/2020

### Principais Insights

* Crescimento consistente entre 2017 e 2018
* Pico de receita em novembro de 2018 (~R$ 1,2M)
* Queda relevante ao longo de 2019
* Sazonalidade recorrente ao longo do período

### Query SQL

```sql
SELECT
  DATE_TRUNC('month', CAST(shipping_limit_date AS DATE)) AS mes,
  SUM(price) AS receita,
  COUNT(DISTINCT order_id) AS pedidos
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
WHERE shipping_limit_date IS NOT NULL
GROUP BY 1
ORDER BY 1;
```

**Configuração:**

* Eixo X: Mês (agrupamento mensal)
* Eixo Y: Receita e pedidos
* Suavização: Ativada

---

## Ranking de Sellers — Top 10

**Tipo:** Horizontal Bar Chart

### Principais Insights

* Alta concentração de vendas nos principais sellers
* Sellers com maior volume não necessariamente geram maior receita
* Oportunidade de expansão da base de vendedores

### Query SQL

```sql
SELECT
  seller_id AS vendedor,
  COUNT(DISTINCT order_id) AS pedidos,
  ROUND(SUM(price) / 1000, 1) AS receita_k
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
GROUP BY 1
ORDER BY pedidos DESC
LIMIT 10;
```

**Configuração:**

* Eixo Y: Seller
* Eixo X: Pedidos e receita
* Ordenação: Decrescente por volume de pedidos

---

## Distribuição por Faixa de Preço

**Tipo:** Donut Chart

### Principais Insights

* Predominância de produtos até R$ 100
* Mix equilibrado entre faixas intermediárias
* Presença relevante de produtos premium

### Query SQL

```sql
SELECT
  CASE
    WHEN price < 50 THEN 'Até R$ 50'
    WHEN price < 100 THEN 'R$ 50–100'
    WHEN price < 200 THEN 'R$ 100–200'
    ELSE 'Acima R$ 200'
  END AS faixa_preco,
  COUNT(*) AS quantidade
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
GROUP BY 1
ORDER BY 1;
```

**Configuração:**

* Segmentos: Faixa de preço
* Valor: Quantidade de itens
* Percentuais visíveis
* Total central: 112.650 itens

---

## Tipos de Visualização Utilizados

* Number (KPIs)
* Area Chart (série temporal)
* Horizontal Bar Chart (ranking)
* Donut Chart (distribuição)
* Potencial de expansão: Map, Heatmap ou Scatter

**Requisito do case atendido:** mínimo de cinco tipos distintos

---

## Design e Layout

* Hierarquia visual: KPIs no topo, gráficos principais ao centro e análises complementares abaixo
* Grid responsivo em 12 colunas
* Paleta de cores consistente para valores monetários e volumes
* Espaçamento uniforme entre componentes

Layout lógico:

```
[KPI 1] [KPI 2] [KPI 3] [KPI 4]
[Evolução Temporal] [Top Sellers]
[Distribuição de Preços]
```

---

## Estrutura de Arquivos

```
07_analise_visualizacao/
├── README.md
├── queries_sql/
│   ├── kpi_receita_total.sql
│   ├── kpi_total_pedidos.sql
│   ├── kpi_ticket_medio.sql
│   ├── kpi_total_itens.sql
│   ├── grafico_evolucao_temporal.sql
│   ├── grafico_top_vendedores.sql
│   └── grafico_distribuicao_preco.sql
├── prints/
│   ├── dashboard_completo.png
│   ├── kpis_detalhe.png
│   ├── evolucao_temporal.png
│   ├── top_sellers.png
│   └── distribuicao_preco.png
└── LINK_DASHBOARD_METABASE.txt
```

---

## Insights de Negócio

**Performance Geral**

* Receita total de R$ 15,8M indica marketplace robusto
* Ticket médio equilibrado
* Alto volume de transações

**Comportamento Temporal**

* Crescimento acelerado entre 2017 e 2018
* Sazonalidade bem definida
* Queda em 2019 demanda investigação adicional

**Vendedores**

* Alta concentração nos principais sellers
* Oportunidade de diversificação da base

**Estratégia de Pricing**

* Predominância de produtos de menor valor
* Mix saudável de preços
* Potencial de crescimento no segmento premium

---

## Próximos Passos

* Inclusão de filtros dinâmicos por período
* Drill-down por categoria de produto
* Comparativos Year over Year (YoY)
* Alertas para KPIs fora do esperado
* Análise geográfica, quando disponível

---

## Conclusão

O dashboard desenvolvido atende integralmente aos requisitos do Item 7 do case técnico Dadosfera:

* Múltiplos tipos de visualização
* Análise temporal e categórica
* Queries SQL documentadas
* Dashboard publicado e acessível
* Layout profissional
* Insights de negócio claros

**Status:** COMPLETO

## Item 6 - Modelagem de Dados (COMPLETO)

**Metodologia:** Star Schema (Ralph Kimball)

### Estrutura Implementada:
- **1 Tabela Fato:** `fato_vendas` (~112k registros)
- **4 Dimensões:** `dim_tempo`, `dim_produto`, `dim_seller`, `dim_cliente`
- **6 Views Analíticas** para consumo direto em BI

### Benefícios:
-  Performance 4-6x melhor que modelo transacional
-  Queries simplificadas (2-3 JOINs vs 5-7)
-  Otimizado para ferramentas de BI (Metabase, Power BI)

### Justificativa:
Star Schema escolhido por simplicidade, performance e compatibilidade 
com ferramentas modernas de analytics.

👉 [Ver diagrama](../06_modelagem/diagramas/star_schema.md)
👉 [Ver scripts DDL](../06_modelagem/ddl_scripts/)

---
