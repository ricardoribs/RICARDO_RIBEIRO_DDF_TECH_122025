-- =====================================================
-- FATO_VENDAS: Tabela Fato Principal
-- Grão: Um item vendido em um pedido
-- Registros esperados: ~112.650
-- =====================================================

CREATE TABLE gold.fato_vendas (
    -- Chaves Surrogate (FKs para dimensões)
    sk_tempo INT NOT NULL,
    sk_produto INT NOT NULL,
    sk_seller INT NOT NULL,
    sk_cliente INT NOT NULL,
    
    -- Chaves de Negócio (Degenerate Dimensions)
    order_id VARCHAR(50) NOT NULL,
    order_item_id INT NOT NULL,
    
    -- Métricas (Medidas Aditivas)
    valor_item DECIMAL(10,2) NOT NULL,          -- price
    valor_frete DECIMAL(10,2) NOT NULL,         -- freight_value
    valor_total DECIMAL(10,2) NOT NULL,         -- price + freight_value
    quantidade INT DEFAULT 1,                    -- Sempre 1 neste dataset
    
    -- Metadados de Controle
    data_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    origem_carga VARCHAR(50) DEFAULT 'OLIST_BRONZE',
    
    -- Chave Primária Composta
    PRIMARY KEY (order_id, order_item_id),
    
    -- Chaves Estrangeiras (FKs)
    FOREIGN KEY (sk_tempo) REFERENCES gold.dim_tempo(sk_tempo),
    FOREIGN KEY (sk_produto) REFERENCES gold.dim_produto(sk_produto),
    FOREIGN KEY (sk_seller) REFERENCES gold.dim_seller(sk_seller),
    FOREIGN KEY (sk_cliente) REFERENCES gold.dim_cliente(sk_cliente),
    
    -- Índices para Performance em Queries Analíticas
    INDEX idx_fato_sk_tempo (sk_tempo),
    INDEX idx_fato_sk_produto (sk_produto),
    INDEX idx_fato_sk_seller (sk_seller),
    INDEX idx_fato_sk_cliente (sk_cliente),
    INDEX idx_fato_order_id (order_id),
    INDEX idx_fato_data_carga (data_carga),
    
    -- Índice Composto para queries temporais com produto
    INDEX idx_tempo_produto (sk_tempo, sk_produto),
    
    -- Índice Composto para queries de seller
    INDEX idx_tempo_seller (sk_tempo, sk_seller)
);

-- =====================================================
-- POPULAR FATO VENDAS
-- =====================================================

INSERT INTO gold.fato_vendas (
    sk_tempo,
    sk_produto,
    sk_seller,
    sk_cliente,
    order_id,
    order_item_id,
    valor_item,
    valor_frete,
    valor_total,
    quantidade
)
SELECT 
    -- Lookup de Chaves Surrogate (SKs)
    
    -- SK Tempo: converter data para YYYYMMDD
    TO_NUMBER(TO_CHAR(DATE(oi.shipping_limit_date), 'YYYYMMDD')) AS sk_tempo,
    
    -- SK Produto: lookup na dim_produto (ou -1 se não encontrar)
    COALESCE(dp.sk_produto, -1) AS sk_produto,
    
    -- SK Seller: lookup na dim_seller (ou -1 se não encontrar)
    COALESCE(ds.sk_seller, -1) AS sk_seller,
    
    -- SK Cliente: lookup na dim_cliente (apenas registros atuais)
    COALESCE(dc.sk_cliente, -1) AS sk_cliente,
    
    -- Chaves de Negócio (mantidas para rastreabilidade)
    oi.order_id,
    oi.order_item_id,
    
    -- Métricas (valores monetários)
    oi.price AS valor_item,
    oi.freight_value AS valor_frete,
    (oi.price + oi.freight_value) AS valor_total,
    
    -- Quantidade (sempre 1 neste dataset)
    1 AS quantidade
    
FROM bronze.olist_order_items oi

-- JOIN com dim_produto
LEFT JOIN gold.dim_produto dp 
    ON oi.product_id = dp.product_id

-- JOIN com dim_seller
LEFT JOIN gold.dim_seller ds 
    ON oi.seller_id = ds.seller_id

-- JOIN com orders para pegar customer_id
LEFT JOIN bronze.olist_orders o 
    ON oi.order_id = o.order_id

-- JOIN com dim_cliente (apenas versão atual)
LEFT JOIN gold.dim_cliente dc 
    ON o.customer_id = dc.customer_id 
    AND dc.registro_atual = TRUE

-- Filtros de Qualidade
WHERE oi.shipping_limit_date IS NOT NULL
  AND oi.price IS NOT NULL
  AND oi.freight_value IS NOT NULL;

-- =====================================================
-- VALIDAÇÃO CRÍTICA
-- =====================================================

-- 1. Verificar contagem total
SELECT COUNT(*) AS total_registros_fato 
FROM gold.fato_vendas;

-- 2. Comparar com Bronze (deve ser igual ou próximo)
SELECT 
    'Bronze' AS camada,
    COUNT(*) AS registros,
    ROUND(SUM(price + freight_value), 2) AS receita_total
FROM bronze.olist_order_items
WHERE shipping_limit_date IS NOT NULL
UNION ALL
SELECT 
    'Gold' AS camada,
    COUNT(*) AS registros,
    ROUND(SUM(valor_total), 2) AS receita_total
FROM gold.fato_vendas;

-- 3. Verificar integridade referencial
SELECT 
    COUNT(*) AS total_fato,
    COUNT(DISTINCT sk_tempo) AS tempos_distintos,
    COUNT(DISTINCT sk_produto) AS produtos_distintos,
    COUNT(DISTINCT sk_seller) AS sellers_distintos,
    COUNT(DISTINCT sk_cliente) AS clientes_distintos,
    COUNT(DISTINCT order_id) AS pedidos_distintos
FROM gold.fato_vendas;

-- 4. Verificar presença de NULLs (NÃO deve ter!)
SELECT 
    SUM(CASE WHEN sk_tempo IS NULL THEN 1 ELSE 0 END) AS nulls_tempo,
    SUM(CASE WHEN sk_produto IS NULL THEN 1 ELSE 0 END) AS nulls_produto,
    SUM(CASE WHEN sk_seller IS NULL THEN 1 ELSE 0 END) AS nulls_seller,
    SUM(CASE WHEN sk_cliente IS NULL THEN 1 ELSE 0 END) AS nulls_cliente,
    SUM(CASE WHEN valor_item IS NULL THEN 1 ELSE 0 END) AS nulls_valor_item,
    SUM(CASE WHEN valor_frete IS NULL THEN 1 ELSE 0 END) AS nulls_valor_frete
FROM gold.fato_vendas;

-- 5. Verificar uso de chaves "UNKNOWN" (-1)
SELECT 
    SUM(CASE WHEN sk_produto = -1 THEN 1 ELSE 0 END) AS produtos_unknown,
    SUM(CASE WHEN sk_seller = -1 THEN 1 ELSE 0 END) AS sellers_unknown,
    SUM(CASE WHEN sk_cliente = -1 THEN 1 ELSE 0 END) AS clientes_unknown
FROM gold.fato_vendas;

-- 6. Verificar valores negativos ou zeros (pode ser problema)
SELECT 
    SUM(CASE WHEN valor_item <= 0 THEN 1 ELSE 0 END) AS valores_item_invalidos,
    SUM(CASE WHEN valor_frete < 0 THEN 1 ELSE 0 END) AS valores_frete_negativos,
    SUM(CASE WHEN valor_total <= 0 THEN 1 ELSE 0 END) AS valores_total_invalidos
FROM gold.fato_vendas;

-- 7. Estatísticas descritivas das métricas
SELECT 
    ROUND(MIN(valor_item), 2) AS min_item,
    ROUND(AVG(valor_item), 2) AS avg_item,
    ROUND(MAX(valor_item), 2) AS max_item,
    ROUND(MIN(valor_frete), 2) AS min_frete,
    ROUND(AVG(valor_frete), 2) AS avg_frete,
    ROUND(MAX(valor_frete), 2) AS max_frete,
    ROUND(MIN(valor_total), 2) AS min_total,
    ROUND(AVG(valor_total), 2) AS avg_total,
    ROUND(MAX(valor_total), 2) AS max_total
FROM gold.fato_vendas;

-- =====================================================
-- QUERIES DE TESTE (Validar Star Schema)
-- =====================================================

-- Teste 1: Vendas por Ano
SELECT 
    t.ano,
    COUNT(DISTINCT f.order_id) AS total_pedidos,
    COUNT(*) AS total_itens,
    ROUND(SUM(f.valor_total), 2) AS receita_total,
    ROUND(AVG(f.valor_total), 2) AS ticket_medio
FROM gold.fato_vendas f
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano
ORDER BY t.ano;

-- Teste 2: Top 5 Produtos
SELECT 
    p.product_id,
    p.categoria,
    COUNT(*) AS qtd_vendida,
    ROUND(SUM(f.valor_total), 2) AS receita
FROM gold.fato_vendas f
INNER JOIN gold.dim_produto p ON f.sk_produto = p.sk_produto
WHERE p.product_id != 'UNKNOWN'
GROUP BY p.product_id, p.categoria
ORDER BY receita DESC
LIMIT 5;

-- Teste 3: Top 5 Sellers
SELECT 
    s.seller_id,
    s.segmento_seller,
    COUNT(DISTINCT f.order_id) AS pedidos,
    ROUND(SUM(f.valor_total), 2) AS receita
FROM gold.fato_vendas f
INNER JOIN gold.dim_seller s ON f.sk_seller = s.sk_seller
WHERE s.seller_id != 'UNKNOWN'
GROUP BY s.seller_id, s.segmento_seller
ORDER BY receita DESC
LIMIT 5;

-- Teste 4: Vendas por Região de Cliente
SELECT 
    c.regiao,
    COUNT(DISTINCT f.order_id) AS pedidos,
    ROUND(SUM(f.valor_total), 2) AS receita
FROM gold.fato_vendas f
INNER JOIN gold.dim_cliente c ON f.sk_cliente = c.sk_cliente
WHERE c.registro_atual = TRUE AND c.customer_id != 'UNKNOWN'
GROUP BY c.regiao
ORDER BY receita DESC;

-- Teste 5: Sazonalidade (Fim de Semana vs Dias Úteis)
SELECT 
    t.eh_fim_semana,
    COUNT(DISTINCT f.order_id) AS pedidos,
    ROUND(SUM(f.valor_total), 2) AS receita,
    ROUND(AVG(f.valor_total), 2) AS ticket_medio
FROM gold.fato_vendas f
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.eh_fim_semana
ORDER BY pedidos DESC;

-- =====================================================
-- CRIAR TABELA DE AUDITORIA (Opcional)
-- =====================================================

CREATE TABLE gold.fato_vendas_auditoria (
    audit_id SERIAL PRIMARY KEY,
    operacao VARCHAR(10),              -- INSERT, UPDATE, DELETE
    order_id VARCHAR(50),
    order_item_id INT,
    valor_anterior DECIMAL(10,2),
    valor_novo DECIMAL(10,2),
    usuario VARCHAR(50),
    data_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ESTATÍSTICAS FINAIS
-- =====================================================

-- Resumo Executivo
SELECT 
    'Tabela Fato' AS entidade,
    COUNT(*) AS total_registros,
    MIN(data_carga) AS primeira_carga,
    MAX(data_carga) AS ultima_carga,
    ROUND(SUM(valor_total), 2) AS receita_total_acumulada,
    ROUND(AVG(valor_total), 2) AS ticket_medio_geral
FROM gold.fato_vendas;

-- Distribuição Temporal
SELECT 
    t.ano,
    t.mes,
    COUNT(*) AS registros_mes
FROM gold.fato_vendas f
INNER JOIN gold.dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano, t.mes
ORDER BY t.ano, t.mes;

COMMIT;

-- =====================================================
-- FIM DO SCRIPT
-- Tabela Fato criada e populada com sucesso!
-- =====================================================