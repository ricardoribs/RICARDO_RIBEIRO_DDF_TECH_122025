-- =====================================================
-- 🕵️ EXEMPLO PRÁTICO: SCD TYPE 2 EM AÇÃO
-- =====================================================

-- 1. Estado Inicial: Inserir um Cliente Novo
INSERT INTO gold.dim_cliente (
    customer_id, customer_unique_id, cidade, estado, regiao,
    data_inicio_vigencia, registro_atual
) VALUES (
    'CUST_TEST_001', 'UNIQUE_001', 'São Paulo', 'SP', 'Sudeste',
    '2024-01-01', TRUE
);

-- Verificar inserção
SELECT * FROM gold.dim_cliente WHERE customer_id = 'CUST_TEST_001';


-- 2. A MUDANÇA: Cliente se muda para o Rio de Janeiro
-- Ao tentar fazer um UPDATE simples, o Trigger vai interceptar
-- e criar o histórico automaticamente.
UPDATE gold.dim_cliente
SET cidade = 'Rio de Janeiro', estado = 'RJ'
WHERE customer_id = 'CUST_TEST_001' AND registro_atual = TRUE;


-- 3. PROVA REAL: Consultar o Histórico Completo
-- Devemos ver DUAS linhas agora: uma expirada (SP) e uma ativa (RJ)
SELECT 
    sk_cliente,
    customer_id,
    cidade,
    estado,
    data_inicio_vigencia,
    data_fim_vigencia,
    registro_atual
FROM gold.dim_cliente
WHERE customer_unique_id = 'UNIQUE_001'
ORDER BY sk_cliente;

/*
Resultado Esperado:
| Cidade         | Estado | Inicio     | Fim        | Atual |
|----------------|--------|------------|------------|-------|
| São Paulo      | SP     | 2024-01-01 | 2026-01-06 | FALSE |
| Rio de Janeiro | RJ     | 2026-01-06 | NULL       | TRUE  |
*/

-- 4. Análise Temporal (Time Travel Query)
-- "Quanto esse cliente gastou enquanto morava em SP?"
SELECT 
    c.cidade,
    COUNT(f.order_id) as total_compras
FROM gold.fato_vendas f
JOIN gold.dim_cliente c ON f.sk_cliente = c.sk_cliente
WHERE c.customer_unique_id = 'UNIQUE_001'
AND c.cidade = 'São Paulo' -- Filtra pela versão histórica
GROUP BY c.cidade;