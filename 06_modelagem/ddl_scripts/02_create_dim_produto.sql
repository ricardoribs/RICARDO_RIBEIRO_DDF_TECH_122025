-- =====================================================
-- DIM_PRODUTO: Dimensão de Produtos
-- Tipo: SCD Type 1 (sobrescreve sem histórico)
-- Registros esperados: ~32.000 produtos
-- =====================================================

CREATE TABLE gold.dim_produto (
    -- Chave Surrogate (PK)
    sk_produto SERIAL PRIMARY KEY,              -- Auto-increment
    
    -- Chave de Negócio (Business Key)
    product_id VARCHAR(50) NOT NULL UNIQUE,     -- ID original do produto
    
    -- Atributos do Produto
    categoria VARCHAR(100),                      -- product_category_name
    peso_gramas INT,                             -- product_weight_g
    comprimento_cm INT,                          -- product_length_cm
    altura_cm INT,                               -- product_height_cm
    largura_cm INT,                              -- product_width_cm
    volume_cm3 INT,                              -- Calculado: comp * alt * larg
    fotos INT,                                   -- product_photos_qty
    descricao_len INT,                           -- Tamanho da descrição
    
    -- Metadados
    data_inclusao DATE DEFAULT CURRENT_DATE,     -- Quando foi cadastrado
    produto_ativo BOOLEAN DEFAULT TRUE,          -- Se ainda está à venda
    
    -- Índices para Performance
    INDEX idx_product_id (product_id),
    INDEX idx_categoria (categoria),
    INDEX idx_produto_ativo (produto_ativo)
);

-- =====================================================
-- POPULAR DIMENSÃO PRODUTO
-- =====================================================

-- Inserir produtos da camada Bronze
INSERT INTO gold.dim_produto (
    product_id,
    categoria,
    peso_gramas,
    comprimento_cm,
    altura_cm,
    largura_cm,
    volume_cm3,
    fotos,
    descricao_len,
    produto_ativo
)
SELECT 
    p.product_id,
    
    -- Tratar categoria null
    COALESCE(p.product_category_name, 'Sem Categoria') AS categoria,
    
    -- Dimensões físicas
    p.product_weight_g AS peso_gramas,
    p.product_length_cm AS comprimento_cm,
    p.product_height_cm AS altura_cm,
    p.product_width_cm AS largura_cm,
    
    -- Calcular volume (comp * alt * larg)
    (COALESCE(p.product_length_cm, 0) * 
     COALESCE(p.product_height_cm, 0) * 
     COALESCE(p.product_width_cm, 0)) AS volume_cm3,
    
    -- Outros atributos
    p.product_photos_qty AS fotos,
    p.product_description_lenght AS descricao_len,
    
    -- Por padrão, todos ativos
    TRUE AS produto_ativo
    
FROM bronze.olist_products p
WHERE p.product_id IS NOT NULL;

-- =====================================================
-- INSERIR PRODUTO "DESCONHECIDO" (para NULLs)
-- =====================================================

INSERT INTO gold.dim_produto (
    sk_produto,
    product_id,
    categoria,
    peso_gramas,
    comprimento_cm,
    altura_cm,
    largura_cm,
    volume_cm3,
    fotos,
    descricao_len,
    produto_ativo
)
VALUES (
    -1,                     -- SK negativo para identificar facilmente
    'UNKNOWN',              -- Business Key
    'Desconhecido',         -- Categoria
    0,                      -- Peso
    0, 0, 0,                -- Dimensões
    0,                      -- Volume
    0,                      -- Fotos
    0,                      -- Descrição
    FALSE                   -- Não ativo
);

-- =====================================================
-- CRIAR CATEGORIAS AGREGADAS (Opcional)
-- =====================================================

-- Adicionar coluna de categoria principal (primeiro nível)
ALTER TABLE gold.dim_produto 
ADD COLUMN categoria_principal VARCHAR(50);

UPDATE gold.dim_produto
SET categoria_principal = CASE 
    WHEN categoria LIKE '%beleza%' OR categoria LIKE '%perfum%' THEN 'Beleza e Perfumaria'
    WHEN categoria LIKE '%informatica%' OR categoria LIKE '%eletronicos%' THEN 'Eletrônicos'
    WHEN categoria LIKE '%moveis%' OR categoria LIKE '%casa%' THEN 'Casa e Decoração'
    WHEN categoria LIKE '%esporte%' OR categoria LIKE '%lazer%' THEN 'Esporte e Lazer'
    WHEN categoria LIKE '%automotivo%' THEN 'Automotivo'
    WHEN categoria LIKE '%livros%' THEN 'Livros'
    WHEN categoria LIKE '%bebe%' THEN 'Bebês'
    WHEN categoria LIKE '%moda%' OR categoria LIKE '%roupa%' THEN 'Moda'
    ELSE 'Outros'
END
WHERE categoria != 'Desconhecido';

-- =====================================================
-- CRIAR FAIXAS DE PESO (para análises)
-- =====================================================

ALTER TABLE gold.dim_produto 
ADD COLUMN faixa_peso VARCHAR(30);

UPDATE gold.dim_produto
SET faixa_peso = CASE 
    WHEN peso_gramas < 100 THEN 'Muito Leve (<100g)'
    WHEN peso_gramas < 500 THEN 'Leve (100-500g)'
    WHEN peso_gramas < 1000 THEN 'Médio (500g-1kg)'
    WHEN peso_gramas < 5000 THEN 'Pesado (1-5kg)'
    WHEN peso_gramas >= 5000 THEN 'Muito Pesado (>5kg)'
    ELSE 'Não Informado'
END;

-- =====================================================
-- VALIDAÇÃO
-- =====================================================

-- Verificar contagem total
SELECT COUNT(*) AS total_produtos FROM gold.dim_produto;

-- Verificar distribuição por categoria
SELECT 
    categoria_principal,
    COUNT(*) AS quantidade,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM gold.dim_produto), 2) AS percentual
FROM gold.dim_produto
WHERE categoria != 'Desconhecido'
GROUP BY categoria_principal
ORDER BY quantidade DESC
LIMIT 10;

-- Verificar produtos sem categoria
SELECT COUNT(*) AS sem_categoria
FROM gold.dim_produto
WHERE categoria = 'Sem Categoria';

-- Verificar distribuição de peso
SELECT 
    faixa_peso,
    COUNT(*) AS quantidade
FROM gold.dim_produto
WHERE faixa_peso IS NOT NULL
GROUP BY faixa_peso
ORDER BY 
    CASE faixa_peso
        WHEN 'Muito Leve (<100g)' THEN 1
        WHEN 'Leve (100-500g)' THEN 2
        WHEN 'Médio (500g-1kg)' THEN 3
        WHEN 'Pesado (1-5kg)' THEN 4
        WHEN 'Muito Pesado (>5kg)' THEN 5
        ELSE 6
    END;

-- Exemplos de registros
SELECT 
    sk_produto,
    product_id,
    categoria,
    categoria_principal,
    peso_gramas,
    faixa_peso,
    volume_cm3,
    fotos
FROM gold.dim_produto
WHERE produto_ativo = TRUE
LIMIT 10;