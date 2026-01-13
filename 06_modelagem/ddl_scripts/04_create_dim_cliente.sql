-- =====================================================
-- DIM_CLIENTE: Dimensão de Clientes
-- Tipo: SCD Type 2 (mantém histórico de mudanças)
-- Registros esperados: ~99.000 clientes
-- =====================================================

CREATE TABLE gold.dim_cliente (
    -- Chave Surrogate (PK)
    sk_cliente SERIAL PRIMARY KEY,              -- Auto-increment
    
    -- Chaves de Negócio (Business Keys)
    customer_id VARCHAR(50) NOT NULL,           -- ID do cliente (muda por pedido)
    customer_unique_id VARCHAR(50),             -- ID real único do cliente
    
    -- Atributos Geográficos
    cidade VARCHAR(100),                        -- customer_city
    estado VARCHAR(2),                          -- customer_state (UF)
    regiao VARCHAR(20),                         -- Norte, Nordeste, Sul, Sudeste, Centro-Oeste
    cep_prefix VARCHAR(5),                      -- Primeiros 5 dígitos do CEP
    
    -- Métricas e Segmentação
    data_primeira_compra DATE,                  -- Data do primeiro pedido
    total_compras INT DEFAULT 0,                -- Quantidade de pedidos
    valor_total_gasto DECIMAL(10,2) DEFAULT 0,  -- Soma de todas as compras
    segmento_cliente VARCHAR(20),               -- Novo, Recorrente, VIP, Inativo
    
    -- Campos SCD Type 2 (Slowly Changing Dimension)
    data_inicio_vigencia DATE NOT NULL,         -- Quando este registro ficou válido
    data_fim_vigencia DATE,                     -- NULL = versão atual
    registro_atual BOOLEAN NOT NULL DEFAULT TRUE, -- TRUE = versão mais recente
    
    -- Índices para Performance
    INDEX idx_customer_id (customer_id),
    INDEX idx_customer_unique_id (customer_unique_id),
    INDEX idx_estado (estado),
    INDEX idx_regiao (regiao),
    INDEX idx_registro_atual (registro_atual),
    INDEX idx_segmento (segmento_cliente)
);

-- =====================================================
-- POPULAR DIMENSÃO CLIENTE (Versão Inicial)
-- =====================================================

-- Inserir clientes únicos da camada Bronze
INSERT INTO gold.dim_cliente (
    customer_id,
    customer_unique_id,
    cidade,
    estado,
    cep_prefix,
    data_primeira_compra,
    total_compras,
    valor_total_gasto,
    segmento_cliente,
    data_inicio_vigencia,
    data_fim_vigencia,
    registro_atual
)
SELECT 
    c.customer_id,
    c.customer_unique_id,
    
    -- Dados geográficos
    c.customer_city AS cidade,
    c.customer_state AS estado,
    SUBSTRING(c.customer_zip_code_prefix::TEXT, 1, 5) AS cep_prefix,
    
    -- Métricas calculadas (se possível fazer JOIN com orders)
    CURRENT_DATE AS data_primeira_compra,  -- Placeholder
    0 AS total_compras,                     -- Será atualizado depois
    0 AS valor_total_gasto,                 -- Será atualizado depois
    'Novo' AS segmento_cliente,             -- Inicialmente todos são novos
    
    -- SCD Type 2
    CURRENT_DATE AS data_inicio_vigencia,
    NULL AS data_fim_vigencia,              -- NULL = versão atual
    TRUE AS registro_atual                  -- TRUE = versão mais recente
    
FROM bronze.olist_customers c
WHERE c.customer_id IS NOT NULL;

-- =====================================================
-- ADICIONAR REGIÕES BASEADO NO ESTADO
-- =====================================================

UPDATE gold.dim_cliente
SET regiao = CASE 
    WHEN estado IN ('SP', 'RJ', 'MG', 'ES') THEN 'Sudeste'
    WHEN estado IN ('PR', 'SC', 'RS') THEN 'Sul'
    WHEN estado IN ('BA', 'SE', 'AL', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA') THEN 'Nordeste'
    WHEN estado IN ('AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC') THEN 'Norte'
    WHEN estado IN ('MT', 'MS', 'GO', 'DF') THEN 'Centro-Oeste'
    ELSE 'Desconhecido'
END;

-- =====================================================
-- ATUALIZAR MÉTRICAS DE COMPRAS
-- (Se tiver acesso à tabela orders e order_items)
-- =====================================================

-- Atualizar total de compras e valor gasto por cliente
UPDATE gold.dim_cliente dc
SET 
    total_compras = subq.num_pedidos,
    valor_total_gasto = subq.valor_total,
    data_primeira_compra = subq.primeira_compra
FROM (
    SELECT 
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS num_pedidos,
        MIN(o.order_purchase_timestamp) AS primeira_compra,
        COALESCE(SUM(oi.price + oi.freight_value), 0) AS valor_total
    FROM bronze.olist_orders o
    LEFT JOIN bronze.olist_order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
) subq
WHERE dc.customer_id = subq.customer_id
  AND dc.registro_atual = TRUE;

-- =====================================================
-- SEGMENTAR CLIENTES
-- =====================================================

-- Segmentação baseada em valor gasto
UPDATE gold.dim_cliente
SET segmento_cliente = CASE 
    WHEN valor_total_gasto >= 5000 THEN 'VIP'
    WHEN total_compras >= 5 THEN 'Recorrente'
    WHEN total_compras >= 2 THEN 'Ativo'
    WHEN total_compras = 1 THEN 'Novo'
    ELSE 'Inativo'
END
WHERE registro_atual = TRUE;

-- =====================================================
-- CRIAR FAIXAS DE VALOR (LTV - Lifetime Value)
-- =====================================================

ALTER TABLE gold.dim_cliente 
ADD COLUMN faixa_ltv VARCHAR(30);

UPDATE gold.dim_cliente
SET faixa_ltv = CASE 
    WHEN valor_total_gasto >= 2000 THEN 'Alto Valor (>R$2k)'
    WHEN valor_total_gasto >= 1000 THEN 'Médio-Alto (R$1k-2k)'
    WHEN valor_total_gasto >= 500 THEN 'Médio (R$500-1k)'
    WHEN valor_total_gasto >= 200 THEN 'Baixo-Médio (R$200-500)'
    WHEN valor_total_gasto > 0 THEN 'Baixo Valor (<R$200)'
    ELSE 'Sem Compras'
END
WHERE registro_atual = TRUE;

-- =====================================================
-- INSERIR CLIENTE "DESCONHECIDO" (para NULLs)
-- =====================================================

INSERT INTO gold.dim_cliente (
    sk_cliente,
    customer_id,
    customer_unique_id,
    cidade,
    estado,
    regiao,
    data_primeira_compra,
    total_compras,
    valor_total_gasto,
    segmento_cliente,
    faixa_ltv,
    data_inicio_vigencia,
    data_fim_vigencia,
    registro_atual
)
VALUES (
    -1,                         -- SK negativo
    'UNKNOWN',                  -- Business Key
    'UNKNOWN',                  -- Unique ID
    'Desconhecido',             -- Cidade
    'XX',                       -- Estado
    'Desconhecido',             -- Região
    '2000-01-01',               -- Data placeholder
    0,                          -- Sem compras
    0,                          -- Sem valor gasto
    'Desconhecido',             -- Segmento
    'Desconhecido',             -- Faixa LTV
    '2000-01-01',               -- Data início
    NULL,                       -- Sem fim (atual)
    TRUE                        -- Registro atual
);

-- =====================================================
-- FUNÇÃO PARA IMPLEMENTAR SCD TYPE 2
-- (Para quando cliente mudar de cidade/estado)
-- =====================================================

CREATE OR REPLACE FUNCTION atualizar_cliente_scd_type2(
    p_customer_id VARCHAR(50),
    p_nova_cidade VARCHAR(100),
    p_novo_estado VARCHAR(2)
)
RETURNS VOID AS $$
BEGIN
    -- 1. Encerrar registro atual
    UPDATE gold.dim_cliente
    SET 
        data_fim_vigencia = CURRENT_DATE,
        registro_atual = FALSE
    WHERE customer_id = p_customer_id
      AND registro_atual = TRUE;
    
    -- 2. Inserir novo registro
    INSERT INTO gold.dim_cliente (
        customer_id,
        customer_unique_id,
        cidade,
        estado,
        regiao,
        cep_prefix,
        data_primeira_compra,
        total_compras,
        valor_total_gasto,
        segmento_cliente,
        faixa_ltv,
        data_inicio_vigencia,
        data_fim_vigencia,
        registro_atual
    )
    SELECT 
        customer_id,
        customer_unique_id,
        p_nova_cidade,          -- Nova cidade
        p_novo_estado,          -- Novo estado
        CASE 
            WHEN p_novo_estado IN ('SP', 'RJ', 'MG', 'ES') THEN 'Sudeste'
            WHEN p_novo_estado IN ('PR', 'SC', 'RS') THEN 'Sul'
            WHEN p_novo_estado IN ('BA', 'SE', 'AL', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA') THEN 'Nordeste'
            WHEN p_novo_estado IN ('AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC') THEN 'Norte'
            WHEN p_novo_estado IN ('MT', 'MS', 'GO', 'DF') THEN 'Centro-Oeste'
            ELSE 'Desconhecido'
        END,                     -- Nova região
        cep_prefix,
        data_primeira_compra,
        total_compras,
        valor_total_gasto,
        segmento_cliente,
        faixa_ltv,
        CURRENT_DATE,            -- Nova data de início
        NULL,                    -- Sem data de fim
        TRUE                     -- Novo registro atual
    FROM gold.dim_cliente
    WHERE customer_id = p_customer_id
      AND data_fim_vigencia = CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VALIDAÇÃO
-- =====================================================

-- Verificar contagem total
SELECT COUNT(*) AS total_clientes FROM gold.dim_cliente;

-- Verificar apenas registros atuais
SELECT COUNT(*) AS clientes_atuais 
FROM gold.dim_cliente 
WHERE registro_atual = TRUE;

-- Verificar distribuição por segmento
SELECT 
    segmento_cliente,
    COUNT(*) AS quantidade,
    ROUND(AVG(valor_total_gasto), 2) AS gasto_medio,
    ROUND(AVG(total_compras), 1) AS compras_media
FROM gold.dim_cliente
WHERE registro_atual = TRUE AND customer_id != 'UNKNOWN'
GROUP BY segmento_cliente
ORDER BY quantidade DESC;

-- Verificar distribuição por faixa de LTV
SELECT 
    faixa_ltv,
    COUNT(*) AS quantidade,
    ROUND(SUM(valor_total_gasto), 2) AS valor_total
FROM gold.dim_cliente
WHERE registro_atual = TRUE AND customer_id != 'UNKNOWN'
GROUP BY faixa_ltv
ORDER BY valor_total DESC;

-- Verificar distribuição geográfica
SELECT 
    regiao,
    COUNT(*) AS quantidade,
    ROUND(AVG(valor_total_gasto), 2) AS gasto_medio
FROM gold.dim_cliente
WHERE registro_atual = TRUE AND customer_id != 'UNKNOWN'
GROUP BY regiao
ORDER BY quantidade DESC;

-- Top 10 clientes por valor gasto
SELECT 
    sk_cliente,
    customer_id,
    cidade,
    estado,
    total_compras,
    valor_total_gasto,
    segmento_cliente,
    faixa_ltv
FROM gold.dim_cliente
WHERE registro_atual = TRUE AND customer_id != 'UNKNOWN'
ORDER BY valor_total_gasto DESC
LIMIT 10;

-- Verificar histórico SCD (se houver mudanças)
SELECT 
    customer_unique_id,
    COUNT(*) AS versoes,
    MIN(data_inicio_vigencia) AS primeira_versao,
    MAX(data_inicio_vigencia) AS ultima_versao
FROM gold.dim_cliente
WHERE customer_id != 'UNKNOWN'
GROUP BY customer_unique_id
HAVING COUNT(*) > 1
ORDER BY versoes DESC;

-- Exemplos de registros
SELECT * FROM gold.dim_cliente 
WHERE registro_atual = TRUE
LIMIT 10;