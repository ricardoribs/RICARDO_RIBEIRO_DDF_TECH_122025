-- =====================================================
-- VIEWS ANALÍTICAS - Star Schema Olist
-- Propósito: Facilitar consultas comuns de BI
-- =====================================================

-- =====================================================
-- VIEW 1: Vendas por Tempo e Categoria
-- Uso: Análise temporal de categorias de produtos
-- =====================================================

CREATE OR REPLACE VIEW gold.vw_vendas_tempo_categoria AS
SELECT 
    -- Dimensão Tempo
    t.ano,
    t.trimestre,
    t.mes,
    t.nome_mes,
    t.semana_ano,
    t.eh_fim_semana,
    
    -- Dimensão Produto
    p.categoria,
    p.categoria_principal,
    p.faixa_peso,
    
    -- Métricas Agregadas
    COUNT(DISTINCT f.order_id) AS total_pedidos,
    COUNT(*) AS total_itens,
    SUM(f.valor_item) AS receita_produto,
    SUM(f.valor_frete) AS receita_frete,
    SUM(f.valor_total) AS receita_total,
    AVG(f.valor_total) AS ticket_medio,
    SUM(f.quantidade) AS quantidade_vendida,
    
    -- Métricas Calculadas
    ROUND(SUM(f.valor_frete) / NULLIF(SUM(f.valor_item), 0) * 100, 2) AS percentual_frete,
    ROUND(SUM(f.valor_total) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS ticket_medio_pedido
    
FROM gold.fato_vendas f
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo
INNER JOIN gold.dim_produto p ON f.sk_produto = p.sk_produto

WHERE p.product_id != 'UNKNOWN'

GROUP BY 
    t.ano,
    t.trimestre,
    t.mes,
    t.nome_mes,
    t.semana_ano,
    t.eh_fim_semana,
    p.categoria,
    p.categoria_principal,
    p.faixa_peso
    
ORDER BY 
    t.ano,
    t.mes,
    receita_total DESC;

-- Exemplo de uso:
-- SELECT * FROM gold.vw_vendas_tempo_categoria
-- WHERE ano = 2018 AND mes = 11
-- ORDER BY receita_total DESC
-- LIMIT 10;

-- =====================================================
-- VIEW 2: Performance de Sellers por Região
-- Uso: Análise geográfica e ranking de vendedores
-- =====================================================

CREATE OR REPLACE VIEW gold.vw_performance_sellers AS
SELECT 
    -- Dimensão Seller
    s.seller_id,
    s.cidade,
    s.estado,
    s.regiao,
    s.segmento_seller,
    s.faixa_receita,
    
    -- Dimensão Tempo
    t.ano,
    t.trimestre,
    t.mes,
    
    -- Métricas de Vendas
    COUNT(DISTINCT f.order_id) AS total_pedidos,
    COUNT(DISTINCT f.sk_cliente) AS clientes_unicos,
    COUNT(*) AS total_itens,
    SUM(f.valor_total) AS receita_total,
    AVG(f.valor_total) AS ticket_medio,
    SUM(f.valor_item) AS receita_produtos,
    SUM(f.valor_frete) AS receita_frete,
    
    -- Métricas Calculadas
    ROUND(SUM(f.valor_frete) / NULLIF(SUM(f.valor_item), 0) * 100, 2) AS perc_frete,
    ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS itens_por_pedido,
    
    -- Datas
    MIN(t.data_completa) AS primeira_venda,
    MAX(t.data_completa) AS ultima_venda,
    MAX(t.data_completa) - MIN(t.data_completa) AS dias_ativo
    
FROM gold.fato_vendas f
INNER JOIN gold.dim_seller s ON f.sk_seller = s.sk_seller
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo

WHERE s.seller_id != 'UNKNOWN'

GROUP BY 
    s.seller_id,
    s.cidade,
    s.estado,
    s.regiao,
    s.segmento_seller,
    s.faixa_receita,
    t.ano,
    t.trimestre,
    t.mes
    
ORDER BY 
    receita_total DESC;

-- Exemplo de uso:
-- SELECT 
--     regiao,
--     COUNT(DISTINCT seller_id) AS num_sellers,
--     SUM(receita_total) AS receita_regiao,
--     AVG(ticket_medio) AS ticket_medio_regiao
-- FROM gold.vw_performance_sellers
-- WHERE ano = 2018
-- GROUP BY regiao
-- ORDER BY receita_regiao DESC;

-- =====================================================
-- VIEW 3: Análise de Clientes (RFM Simplificado)
-- Uso: Segmentação e análise de comportamento
-- =====================================================

CREATE OR REPLACE VIEW gold.vw_analise_clientes AS
SELECT 
    -- Dimensão Cliente
    c.sk_cliente,
    c.customer_id,
    c.customer_unique_id,
    c.cidade,
    c.estado,
    c.regiao,
    c.segmento_cliente,
    c.faixa_ltv,
    
    -- Métricas RFM (Recency, Frequency, Monetary)
    MAX(t.data_completa) AS data_ultima_compra,
    CURRENT_DATE - MAX(t.data_completa) AS dias_desde_ultima_compra,  -- Recency
    COUNT(DISTINCT f.order_id) AS total_compras,                      -- Frequency
    SUM(f.valor_total) AS valor_total_gasto,                          -- Monetary
    AVG(f.valor_total) AS ticket_medio,
    
    -- Métricas de Produto
    COUNT(DISTINCT f.sk_produto) AS produtos_distintos_comprados,
    
    -- Datas
    MIN(t.data_completa) AS data_primeira_compra,
    MAX(t.data_completa) - MIN(t.data_completa) AS dias_como_cliente
    
FROM gold.fato_vendas f
INNER JOIN gold.dim_cliente c ON f.sk_cliente = c.sk_cliente
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo

WHERE c.registro_atual = TRUE 
  AND c.customer_id != 'UNKNOWN'

GROUP BY 
    c.sk_cliente,
    c.customer_id,
    c.customer_unique_id,
    c.cidade,
    c.estado,
    c.regiao,
    c.segmento_cliente,
    c.faixa_ltv
    
ORDER BY 
    valor_total_gasto DESC;

-- Exemplo de uso:
-- SELECT * FROM gold.vw_analise_clientes
-- WHERE dias_desde_ultima_compra <= 90  -- Clientes ativos (últimos 3 meses)
-- ORDER BY valor_total_gasto DESC
-- LIMIT 100;

-- =====================================================
-- VIEW 4: Análise de Produtos Detalhada
-- Uso: Performance de produtos e categorias
-- =====================================================

CREATE OR REPLACE VIEW gold.vw_analise_produtos AS
SELECT 
    -- Dimensão Produto
    p.sk_produto,
    p.product_id,
    p.categoria,
    p.categoria_principal,
    p.peso_gramas,
    p.faixa_peso,
    p.volume_cm3,
    p.fotos,
    
    -- Métricas de Vendas
    COUNT(DISTINCT f.order_id) AS total_pedidos,
    COUNT(*) AS total_itens_vendidos,
    SUM(f.valor_item) AS receita_produto,
    SUM(f.valor_frete) AS custo_frete,
    SUM(f.valor_total) AS receita_total,
    AVG(f.valor_item) AS preco_medio,
    AVG(f.valor_frete) AS frete_medio,
    
    -- Métricas Calculadas
    ROUND(AVG(f.valor_frete) / NULLIF(AVG(f.valor_item), 0) * 100, 2) AS perc_frete_medio,
    
    -- Distribuição Temporal
    MIN(t.data_completa) AS primeira_venda,
    MAX(t.data_completa) AS ultima_venda,
    MAX(t.data_completa) - MIN(t.data_completa) AS dias_no_catalogo,
    
    -- Sellers e Clientes
    COUNT(DISTINCT f.sk_seller) AS sellers_que_vendem,
    COUNT(DISTINCT f.sk_cliente) AS clientes_unicos
    
FROM gold.fato_vendas f
INNER JOIN gold.dim_produto p ON f.sk_produto = p.sk_produto
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo

WHERE p.product_id != 'UNKNOWN'

GROUP BY 
    p.sk_produto,
    p.product_id,
    p.categoria,
    p.categoria_principal,
    p.peso_gramas,
    p.faixa_peso,
    p.volume_cm3,
    p.fotos
    
ORDER BY 
    receita_total DESC;

-- Exemplo de uso:
-- SELECT * FROM gold.vw_analise_produtos
-- WHERE categoria_principal = 'Eletrônicos'
-- ORDER BY total_itens_vendidos DESC
-- LIMIT 20;

-- =====================================================
-- VIEW 5: Análise de Sazonalidade
-- Uso: Identificar padrões temporais
-- =====================================================

CREATE OR REPLACE VIEW gold.vw_sazonalidade AS
SELECT 
    -- Dimensões Temporais
    t.ano,
    t.mes,
    t.nome_mes,
    t.dia_semana,
    t.nome_dia_semana,
    t.eh_fim_semana,
    t.eh_feriado,
    t.nome_feriado,
    t.semana_ano,
    
    -- Métricas
    COUNT(DISTINCT f.order_id) AS total_pedidos,
    COUNT(*) AS total_itens,
    SUM(f.valor_total) AS receita_total,
    AVG(f.valor_total) AS ticket_medio,
    
    -- Métricas por Pedido
    ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS itens_por_pedido,
    ROUND(SUM(f.valor_total) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS valor_medio_pedido
    
FROM gold.fato_vendas f
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo

GROUP BY 
    t.ano,
    t.mes,
    t.nome_mes,
    t.dia_semana,
    t.nome_dia_semana,
    t.eh_fim_semana,
    t.eh_feriado,
    t.nome_feriado,
    t.semana_ano
    
ORDER BY 
    t.ano,
    t.mes,
    t.dia_semana;

-- Exemplo de uso:
-- Comparar vendas em feriados vs não-feriados
-- SELECT 
--     eh_feriado,
--     COUNT(*) AS dias,
--     ROUND(AVG(total_pedidos), 0) AS media_pedidos_dia,
--     ROUND(AVG(receita_total), 2) AS media_receita_dia
-- FROM gold.vw_sazonalidade
-- WHERE ano = 2018
-- GROUP BY eh_feriado;

-- =====================================================
-- VIEW 6: Dashboard Executivo (KPIs Principais)
-- Uso: Visão geral para executivos
-- =====================================================

CREATE OR REPLACE VIEW gold.vw_dashboard_executivo AS
SELECT 
    -- Período
    t.ano,
    t.trimestre,
    t.mes,
    t.nome_mes,
    
    -- KPIs de Vendas
    COUNT(DISTINCT f.order_id) AS total_pedidos,
    COUNT(*) AS total_itens,
    SUM(f.valor_total) AS receita_total,
    SUM(f.valor_item) AS receita_produtos,
    SUM(f.valor_frete) AS receita_frete,
    
    -- KPIs de Clientes
    COUNT(DISTINCT f.sk_cliente) AS clientes_ativos,
    
    -- KPIs de Produtos
    COUNT(DISTINCT f.sk_produto) AS produtos_vendidos,
    
    -- KPIs de Sellers
    COUNT(DISTINCT f.sk_seller) AS sellers_ativos,
    
    -- Métricas Calculadas
    ROUND(SUM(f.valor_total) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS ticket_medio,
    ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS itens_por_pedido,
    ROUND(SUM(f.valor_frete) / NULLIF(SUM(f.valor_item), 0) * 100, 2) AS percentual_frete,
    
    -- Comparativo MoM (Month over Month) - placeholder
    LAG(SUM(f.valor_total)) OVER (ORDER BY t.ano, t.mes) AS receita_mes_anterior,
    ROUND(
        (SUM(f.valor_total) - LAG(SUM(f.valor_total)) OVER (ORDER BY t.ano, t.mes)) / 
        NULLIF(LAG(SUM(f.valor_total)) OVER (ORDER BY t.ano, t.mes), 0) * 100,
        2
    ) AS crescimento_mom_percentual
    
FROM gold.fato_vendas f
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo

GROUP BY 
    t.ano,
    t.trimestre,
    t.mes,
    t.nome_mes
    
ORDER BY 
    t.ano,
    t.mes;

-- Exemplo de uso:
-- SELECT * FROM gold.vw_dashboard_executivo
-- WHERE ano = 2018
-- ORDER BY mes;

-- =====================================================
-- VALIDAÇÃO DAS VIEWS
-- =====================================================

-- Teste rápido de cada view
SELECT 'vw_vendas_tempo_categoria' AS view_name, COUNT(*) AS registros FROM gold.vw_vendas_tempo_categoria
UNION ALL
SELECT 'vw_performance_sellers', COUNT(*) FROM gold.vw_performance_sellers
UNION ALL
SELECT 'vw_analise_clientes', COUNT(*) FROM gold.vw_analise_clientes
UNION ALL
SELECT 'vw_analise_produtos', COUNT(*) FROM gold.vw_analise_produtos
UNION ALL
SELECT 'vw_sazonalidade', COUNT(*) FROM gold.vw_sazonalidade
UNION ALL
SELECT 'vw_dashboard_executivo', COUNT(*) FROM gold.vw_dashboard_executivo;

-- =====================================================
-- FIM DO SCRIPT
-- 6 Views analíticas criadas com sucesso!
-- =====================================================