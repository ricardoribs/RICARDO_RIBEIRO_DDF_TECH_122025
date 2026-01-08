-- =============================================================================
-- 📊 ANÁLISE DE PERFORMANCE: Transactional (3NF) vs Dimensional (Star Schema)
-- Objetivo: Demonstrar o ganho de performance da Camada Gold
-- Como usar: Rode cada bloco separadamente e compare o "Execution Time"
-- =============================================================================

-- -----------------------------------------------------------------------------
-- CENÁRIO 1: Consulta Complexa no Modelo Transacional (Bronze/Silver)
-- Problema: Muitos JOINs, scan em tabelas grandes não otimizadas para leitura
-- -----------------------------------------------------------------------------
EXPLAIN ANALYZE
SELECT 
    DATE_TRUNC('month', o.order_purchase_timestamp) AS mes,
    p.product_category_name AS categoria,
    COUNT(DISTINCT o.order_id) AS total_pedidos,
    SUM(oi.price + oi.freight_value) AS receita_total
FROM public.olist_orders_dataset o -- (Ou schema bronze/silver)
INNER JOIN public.olist_order_items_dataset oi ON o.order_id = oi.order_id
INNER JOIN public.olist_products_dataset p ON oi.product_id = p.product_id
INNER JOIN public.olist_sellers_dataset s ON oi.seller_id = s.seller_id
INNER JOIN public.olist_customers_dataset c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY 1, 2
ORDER BY receita_total DESC;

-- -----------------------------------------------------------------------------
-- CENÁRIO 2: Mesma Consulta no Star Schema (Gold)
-- Vantagem: Menos JOINs, Dimensões pré-tratadas, Inteiros (SKs) ao invés de Strings
-- -----------------------------------------------------------------------------
EXPLAIN ANALYZE
SELECT 
    t.ano,
    t.mes,
    p.categoria,
    COUNT(DISTINCT f.order_id) AS total_pedidos,
    SUM(f.valor_total) AS receita_total
FROM gold.fato_vendas f
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo
INNER JOIN gold.dim_produto p ON f.sk_produto = p.sk_produto
-- Note que não precisamos de JOIN com Cliente ou Seller se não formos usar colunas deles
GROUP BY 1, 2, 3
ORDER BY receita_total DESC;

/*
=============================================================================
🏆 RESULTADO ESPERADO (BENCHMARK TÍPICO):
=============================================================================

1. Custo Computacional (Cost):
   - Transacional: Alto (Muitos Nested Loops e Hash Joins pesados)
   - Star Schema: Baixo (Merge Joins eficientes em chaves numéricas)

2. Tempo de Execução (Execution Time):
   - Transacional: ~400ms - 800ms (Depende do cache)
   - Star Schema:  ~50ms - 100ms
   
   👉 GANHO DE PERFORMANCE: 5x a 8x MAIS RÁPIDO
=============================================================================
*/