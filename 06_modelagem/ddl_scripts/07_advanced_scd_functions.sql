-- ==================================================================
-- AUTOMAÇÃO SCD TYPE 2 - DIMENSÃO CLIENTE
-- Objetivo: Criar histórico automático quando um cliente muda de local
-- ==================================================================

-- 1. Função para gerenciar a expiração e inserção do novo registro
CREATE OR REPLACE FUNCTION gold.atualizar_cliente_scd_type2(
    p_customer_id VARCHAR,
    p_nova_cidade VARCHAR,
    p_novo_estado VARCHAR
) RETURNS VOID AS $$
DECLARE
    v_customer_unique_id VARCHAR;
BEGIN
    -- Recupera o ID único do cliente atual
    SELECT customer_unique_id INTO v_customer_unique_id
    FROM gold.dim_cliente
    WHERE customer_id = p_customer_id AND registro_atual = TRUE;

    -- 1. Expirar o registro atual (Update)
    UPDATE gold.dim_cliente
    SET registro_atual = FALSE,
        data_fim_vigencia = CURRENT_DATE
    WHERE customer_id = p_customer_id AND registro_atual = TRUE;

    -- 2. Inserir o novo registro (Insert)
    INSERT INTO gold.dim_cliente (
        customer_id, 
        customer_unique_id, 
        cidade, 
        estado, 
        regiao, -- Mantém a região baseada no novo estado (simplificado)
        data_inicio_vigencia, 
        data_fim_vigencia, 
        registro_atual
    ) VALUES (
        p_customer_id,
        v_customer_unique_id,
        p_nova_cidade,
        p_novo_estado,
        CASE 
            WHEN p_novo_estado IN ('SP', 'RJ', 'MG', 'ES') THEN 'Sudeste'
            WHEN p_novo_estado IN ('PR', 'SC', 'RS') THEN 'Sul'
            ELSE 'Outros' -- Simplificação para o exemplo
        END,
        CURRENT_DATE,
        NULL,
        TRUE
    );
END;
$$ LANGUAGE plpgsql;

-- 2. Função de Gatilho (Trigger Function)
CREATE OR REPLACE FUNCTION gold.fn_trigger_scd_cliente()
RETURNS TRIGGER AS $$
BEGIN
    -- Se mudou cidade ou estado, aciona o versionamento
    IF NEW.cidade <> OLD.cidade OR NEW.estado <> OLD.estado THEN
        
        -- Chama a função manual de atualização
        PERFORM gold.atualizar_cliente_scd_type2(
            OLD.customer_id,
            NEW.cidade,
            NEW.estado
        );
        
        -- Retorna NULL para cancelar o UPDATE direto (pois já fizemos INSERT do novo)
        -- Ou retorna OLD para manter o registro antigo inalterado (já que expiramos ele manualmente)
        RETURN NULL; 
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Criar o Trigger na Tabela
DROP TRIGGER IF EXISTS trg_scd_cliente ON gold.dim_cliente;

CREATE TRIGGER trg_scd_cliente
BEFORE UPDATE ON gold.dim_cliente
FOR EACH ROW
EXECUTE FUNCTION gold.fn_trigger_scd_cliente();