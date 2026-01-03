-- =====================================================
-- DIM_SELLER: Dimensão de Vendedores (Sellers)
-- Tipo: SCD Type 1 (sobrescreve sem histórico)
-- Registros esperados: ~3.100 sellers
-- =====================================================

CREATE TABLE gold.dim_seller (
    -- Chave Surrogate (PK)
    sk_seller SERIAL PRIMARY KEY,               -- Auto-increment
    
    -- Chave de Negócio (Business Key)
    seller_id VARCHAR(50) NOT NULL UNIQUE,      -- ID original do seller
    
    -- Atributos Geográficos
    cidade VARCHAR(100),                         -- seller_city
    estado VARCHAR(2),                           -- seller_state (UF: SP, RJ, etc)
    regiao VARCHAR(20),                          -- Norte, Nordeste, Sul, Sudeste, Centro-Oeste
    cep_prefix VARCHAR(5),                       -- Primeiros 5 dígitos do CEP
    
    -- Métricas Históricas (agregadas)
    data_primeiro_pedido DATE,                   -- Data da primeira venda
    data_ultimo_pedido DATE,                     -- Data da última venda
    total_pedidos_historico INT DEFAULT 0,       -- Contador de pedidos
    receita_historica DECIMAL(10,2) DEFAULT 0,   -- Receita total acumulada
    
    -- Status
    seller_ativo BOOLEAN DEFAULT TRUE,           -- Se ainda está vendendo
    
    -- Índices para Performance
    INDEX idx_seller_id (seller_id),
    INDEX idx_estado (estado),
    INDEX idx_regiao (regiao),
    INDEX idx_seller_ativo (seller_ativo)
);

-- =====================================================
-- POPULAR DIMENSÃO SELLER
-- =====================================================

-- Inserir sellers com métricas agregadas
INSERT INTO gold.dim_seller (
    seller_id,
    cidade,
    estado,
    cep_prefix,
    data_primeiro_pedido,
    data_ultimo_pedido,
    total_pedidos_historico,
    receita_historica,
    seller_ativo
)
SELECT 
    oi.seller_id,
    
    -- Dados geográficos (não disponíveis no dataset, usar placeholder)
    'N/A' AS cidade,
    'XX' AS estado,
    NULL AS cep_prefix,
    
    -- Métricas calculadas
    MIN(DATE(oi.shipping_limit_date)) AS data_primeiro_pedido,
    MAX(DATE(oi.shipping_limit_date)) AS data_ultimo_pedido,
    COUNT(DISTINCT oi.order_id) AS total_pedidos_historico,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS receita_historica,
    
    -- Considerar ativo se vendeu nos últimos 180 dias
    CASE 
        WHEN MAX(DATE(oi.shipping_limit_date)) >= CURRENT_DATE - INTERVAL '180 days' 
        THEN TRUE 
        ELSE FALSE 
    END AS seller_ativo
    
FROM bronze.olist_order_items oi
WHERE oi.seller_id IS NOT NULL
GROUP BY oi.seller_id;

-- =====================================================
-- ADICIONAR REGIÕES BASEADO NO ESTADO
-- =====================================================

-- Atualizar região baseado no estado (se tiver dados)
UPDATE gold.dim_seller
SET regiao = CASE 
    WHEN estado IN ('SP', 'RJ', 'MG', 'ES') THEN 'Sudeste'
    WHEN estado IN ('PR', 'SC', 'RS') THEN 'Sul'
    WHEN estado IN ('BA', 'SE', 'AL', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA') THEN 'Nordeste'
    WHEN estado IN ('AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC') THEN 'Norte'
    WHEN estado IN ('MT', 'MS', 'GO', 'DF') THEN 'Centro-Oeste'
    ELSE 'Desconhecido'
END;

-- =====================================================
-- CRIAR SEGMENTAÇÃO DE SELLERS
-- =====================================================

-- Adicionar coluna de segmento
ALTER TABLE gold.dim_seller 
ADD COLUMN segmento_seller VARCHAR(30);

-- Segmentar por volume de pedidos
UPDATE gold.dim_seller
SET segmento_seller = CASE 
    WHEN total_pedidos_historico >= 100 THEN 'Top Seller (100+)'
    WHEN total_pedidos_historico >= 50 THEN 'Grande (50-99)'
    WHEN total_pedidos_historico >= 20 THEN 'Médio (20-49)'
    WHEN total_pedidos_historico >= 10 THEN 'Pequeno (10-19)'
    ELSE 'Micro (<10)'
END;

-- =====================================================
-- CRIAR FAIXAS DE RECEITA
-- =====================================================

ALTER TABLE gold.dim_seller 
ADD COLUMN faixa_receita VARCHAR(30);

UPDATE gold.dim_seller
SET faixa_receita = CASE 
    WHEN receita_historica >= 100000 THEN 'Alto Faturamento (>R$100k)'
    WHEN receita_historica >= 50000 THEN 'Médio-Alto (R$50k-100k)'
    WHEN receita_historica >= 10000 THEN 'Médio (R$10k-50k)'
    WHEN receita_historica >= 5000 THEN 'Baixo-Médio (R$5k-10k)'
    ELSE 'Baixo Faturamento (<R$5k)'
END;

-- =====================================================
-- INSERIR SELLER "DESCONHECIDO" (para NULLs)
-- =====================================================

INSERT INTO gold.dim_seller (
    sk_seller,
    seller_id,
    cidade,
    estado,
    regiao,
    data_primeiro_pedido,
    total_pedidos_historico,
    receita_historica,
    seller_ativo,
    segmento_seller,
    faixa_receita
)
VALUES (
    -1,                         -- SK negativo
    'UNKNOWN',                  -- Business Key
    'Desconhecido',             -- Cidade
    'XX',                       -- Estado
    'Desconhecido',             -- Região
    '2000-01-01',               -- Data placeholder
    0,                          -- Sem pedidos
    0,                          -- Sem receita
    FALSE,                      -- Não ativo
    'Desconhecido',             -- Segmento
    'Desconhecido'              -- Faixa receita
);

-- =====================================================
-- VALIDAÇÃO
-- =====================================================

-- Verificar contagem total
SELECT COUNT(*) AS total_sellers FROM gold.dim_seller;

-- Verificar distribuição por segmento
SELECT 
    segmento_seller,
    COUNT(*) AS quantidade,
    ROUND(AVG(receita_historica), 2) AS receita_media,
    ROUND(AVG(total_pedidos_historico), 1) AS pedidos_medio
FROM gold.dim_seller
WHERE seller_id != 'UNKNOWN'
GROUP BY segmento_seller
ORDER BY 
    CASE segmento_seller
        WHEN 'Top Seller (100+)' THEN 1
        WHEN 'Grande (50-99)' THEN 2
        WHEN 'Médio (20-49)' THEN 3
        WHEN 'Pequeno (10-19)' THEN 4
        WHEN 'Micro (<10)' THEN 5
    END;

-- Verificar distribuição por faixa de receita
SELECT 
    faixa_receita,
    COUNT(*) AS quantidade,
    ROUND(SUM(receita_historica), 2) AS receita_total
FROM gold.dim_seller
WHERE seller_id != 'UNKNOWN'
GROUP BY faixa_receita
ORDER BY receita_total DESC;

-- Verificar sellers ativos vs inativos
SELECT 
    seller_ativo,
    COUNT(*) AS quantidade,
    ROUND(AVG(receita_historica), 2) AS receita_media
FROM gold.dim_seller
WHERE seller_id != 'UNKNOWN'
GROUP BY seller_ativo;

-- Top 10 sellers por receita
SELECT 
    sk_seller,
    seller_id,
    segmento_seller,
    total_pedidos_historico,
    receita_historica,
    data_primeiro_pedido,
    data_ultimo_pedido
FROM gold.dim_seller
WHERE seller_id != 'UNKNOWN'
ORDER BY receita_historica DESC
LIMIT 10;

-- Exemplos de registros
SELECT * FROM gold.dim_seller 
WHERE seller_ativo = TRUE
LIMIT 10;