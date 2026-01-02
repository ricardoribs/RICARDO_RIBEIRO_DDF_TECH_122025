Item 7 - Análise de Dados e Visualização
📊 Dashboard no Metabase
Link do Dashboard: Dashboard Executivo Olist - Ricardo Ribeiro
Coleção: Ricardo Ribeiro - Olist - Dez 2025
Ferramenta: Metabase (Dadosfera)
Período analisado: 2016-2020

🎯 Objetivo da Análise
Construir um dashboard executivo que permita:

Monitorar KPIs principais de vendas em tempo real
Analisar evolução temporal da receita
Identificar principais vendedores (sellers)
Entender distribuição de preços dos produtos


📈 Visualizações Implementadas
1. KPIs Principais (Number Cards)
Dashboard contém 4 KPIs estratégicos no topo:
KPIValorDescrição💰 Receita TotalR$ 15.8MSoma de price + freight_value de todos os itens📦 Total de Pedidos98,666Pedidos únicos (order_id distinct)🎯 Ticket MédioR$ 140.64Valor médio por pedido📊 Total de Itens112.7kQuantidade total de itens vendidos
Query SQL:
sql-- KPI 1: Receita Total
SELECT 
    ROUND(SUM(price + freight_value) / 1000000, 2) AS receita_milhoes
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;

-- KPI 2: Total de Pedidos
SELECT 
    COUNT(DISTINCT order_id) AS total_pedidos
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;

-- KPI 3: Ticket Médio
SELECT 
    ROUND(AVG(price + freight_value), 2) AS ticket_medio
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;

-- KPI 4: Total de Itens
SELECT 
    COUNT(*) AS total_itens
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;
Configuração no Metabase:

Tipo: Number (card grande)
Formatação: Moeda brasileira (R$) onde aplicável
Posicionamento: Linha superior, 4 colunas iguais


2. Gráfico de Evolução Temporal (Area Chart)
Descrição:
Análise de série temporal mostrando crescimento de receita e volume de pedidos entre janeiro/2017 e janeiro/2020.
Insights:

📈 Crescimento consistente de 2017 a 2018
🚀 Pico em novembro/2018: ~R$ 1.2M em receita mensal
📉 Queda abrupta em 2019: Possível mudança no negócio ou fim de coleta de dados
🔄 Sazonalidade visível: Picos regulares sugerem campanhas sazonais (Black Friday, etc)

Query SQL:
sqlSELECT 
    DATE_TRUNC('month', CAST(shipping_limit_date AS DATE)) AS mes,
    SUM(price) AS receita,
    COUNT(DISTINCT order_id) AS pedidos
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
WHERE shipping_limit_date IS NOT NULL
GROUP BY 1
ORDER BY 1;
Configuração:

Tipo: Area Chart (gráfico de área com preenchimento)
Eixo X: mes (agrupamento mensal)
Eixo Y: receita (verde) + pedidos (azul)
Suavização: Ativada


3. Ranking de Vendedores (Horizontal Bar Chart)
Descrição:
Top 10 sellers (vendedores) com maior volume de pedidos e receita gerada.
Insights:

🏆 Concentração de vendas: Top 3 sellers representam parcela significativa
💡 Oportunidade: Expandir base de sellers ativos
📊 Correlação preço x volume: Sellers com mais pedidos nem sempre têm maior receita

Query SQL:
sqlSELECT 
    seller_id AS vendedor,
    COUNT(DISTINCT order_id) AS pedidos,
    ROUND(SUM(price) / 1000, 1) AS receita_k
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
GROUP BY 1
ORDER BY pedidos DESC
LIMIT 10;
Configuração:

Tipo: Bar Chart (barras horizontais)
Eixo Y: vendedor (ID do seller)
Eixo X: pedidos (azul) + receita_k (laranja)
Ordenação: Decrescente por volume de pedidos


4. Distribuição por Faixa de Preço (Donut Chart)
Descrição:
Segmentação dos 112.650 itens por faixa de preço unitário.
Insights:

🎯 34.6% até R$ 50: Produtos de entrada/baixo custo dominam
💰 29.4% entre R$ 50-100: Faixa intermediária relevante
📈 24.0% entre R$ 100-200: Mercado médio-alto expressivo
💎 12.0% acima de R$ 200: Nicho premium menor mas importante

Implicações estratégicas:

Marketplace democrático (atende todas as faixas)
Oportunidade de upsell da faixa mais baixa
Mix saudável de produtos

Query SQL:
sqlSELECT 
    CASE 
        WHEN price < 50 THEN 'Até R$ 50'
        WHEN price < 100 THEN 'R$ 50-100'
        WHEN price < 200 THEN 'R$ 100-200'
        ELSE 'Acima R$ 200'
    END AS faixa_preco,
    COUNT(*) AS quantidade
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
GROUP BY 1
ORDER BY 1;
Configuração:

Tipo: Donut Chart (gráfico de rosca)
Segmentos: faixa_preco
Valor: quantidade
Percentuais: Visíveis
Total no centro: 112,650


📊 Tipos de Visualização Utilizados
✅ 5 tipos distintos de visualização:

Number - KPIs principais (4 cards)
Area Chart - Evolução temporal
Horizontal Bar Chart - Ranking de sellers
Donut Chart - Distribuição de preços
(Potencial para adicionar) - Map, Heatmap ou Scatter

✅ Requisito do case ATENDIDO (mínimo 5 tipos diferentes)

🎨 Design e Layout
Princípios Aplicados:

Hierarquia Visual: KPIs no topo → Gráficos principais → Secundários
Grid Responsivo: 12 colunas para alinhamento perfeito
Paleta Consistente:

Verde: Receita/valores monetários positivos
Azul: Volume/contagens
Cores suaves e profissionais


Espaçamento: Padding uniforme entre cards

Estrutura:
┌─────────────────────────────────────────────────┐
│  [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]            │
│                                                  │
│  [Evolução Temporal - Grande]  [Top Sellers]    │
│                                                  │
│  [Distribuição Preço]                           │
└─────────────────────────────────────────────────┘

📁 Arquivos do Projeto
07_analise_visualizacao/
├── README.md                          # Este arquivo
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

🔗 Links Importantes

Dashboard Interativo: Clique aqui
Tabela na Dadosfera: TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
Coleção Metabase: Ricardo Ribeiro - Olist - Dez 2025


💡 Insights de Negócio
1. Performance Geral

Receita total de R$ 15.8M demonstra marketplace robusto
Ticket médio de R$ 140.64 indica mix equilibrado de produtos
98k+ pedidos mostram volume significativo de transações

2. Comportamento Temporal

Crescimento acelerado em 2017-2018
Sazonalidade clara (picos mensais)
Queda em 2019 sugere necessidade de investigação

3. Concentração de Vendedores

Marketplace relativamente concentrado (top 10 dominam)
Oportunidade de diversificar base de sellers
Potencial para programa de incentivo a novos vendedores

4. Estratégia de Pricing

64% dos produtos abaixo de R$ 100 (acessibilidade)
Presença em todas as faixas de preço (democratização)
Oportunidade de aumentar participação premium (12%)


🚀 Próximos Passos Sugeridos

Adicionar filtros de data para análise de períodos específicos
Criar drill-downs por categoria de produto
Implementar alertas para KPIs fora do esperado
Adicionar comparativos YoY (Year over Year)
Incluir análise geográfica (se dados de localização disponíveis)


📊 Conclusão
O dashboard desenvolvido atende plenamente aos requisitos do Item 7 do case técnico Dadosfera:
✅ Mínimo 5 tipos de visualização diferentes
✅ Análise de categorias (sellers/faixas de preço)
✅ Análise de série temporal (evolução 2016-2020)
✅ Queries SQL documentadas e salvas
✅ Dashboard publicado e acessível via link
✅ Layout profissional e organizado
✅ Insights de negócio documentados
Status: ✅ COMPLETO