-- =====================================================
-- DIM_TEMPO: Dimensão de Tempo
-- Granularidade: Dia
-- Período: 2016-01-01 a 2020-12-31
-- Registros: 1.826 dias
-- =====================================================

CREATE TABLE gold.dim_tempo (
    -- Chave Surrogate (PK)
    sk_tempo INT PRIMARY KEY,                   -- Formato: YYYYMMDD (ex: 20180115)
    
    -- Atributos de Data
    data_completa DATE NOT NULL UNIQUE,         -- 2018-01-15
    
    -- Hierarquia Temporal
    ano INT NOT NULL,                           -- 2018
    trimestre INT NOT NULL,                     -- 1 (Q1)
    mes INT NOT NULL,                           -- 1 (Janeiro)
    nome_mes VARCHAR(20) NOT NULL,              -- "Janeiro"
    dia_mes INT NOT NULL,                       -- 15
    dia_semana INT NOT NULL,                    -- 2 (1=Domingo, 7=Sábado)
    nome_dia_semana VARCHAR(20) NOT NULL,       -- "Segunda-feira"
    semana_ano INT NOT NULL,                    -- 3 (terceira semana do ano)
    dia_ano INT NOT NULL,                       -- 15 (décimo quinto dia do ano)
    
    -- Flags e Indicadores
    eh_fim_semana BOOLEAN NOT NULL,             -- TRUE se sábado ou domingo
    eh_feriado BOOLEAN DEFAULT FALSE,           -- TRUE se feriado brasileiro
    nome_feriado VARCHAR(50),                   -- "Black Friday", "Natal", etc
    
    -- Índices para Performance
    INDEX idx_data_completa (data_completa),
    INDEX idx_ano_mes (ano, mes),
    INDEX idx_trimestre (ano, trimestre)
);

-- =====================================================
-- POPULAR DIMENSÃO TEMPO (2016-2020)
-- =====================================================

INSERT INTO gold.dim_tempo (
    sk_tempo,
    data_completa,
    ano,
    trimestre,
    mes,
    nome_mes,
    dia_mes,
    dia_semana,
    nome_dia_semana,
    semana_ano,
    dia_ano,
    eh_fim_semana,
    eh_feriado,
    nome_feriado
)
SELECT 
    -- SK no formato YYYYMMDD
    TO_NUMBER(TO_CHAR(data, 'YYYYMMDD')) AS sk_tempo,
    
    -- Data completa
    data AS data_completa,
    
    -- Hierarquia temporal
    EXTRACT(YEAR FROM data) AS ano,
    EXTRACT(QUARTER FROM data) AS trimestre,
    EXTRACT(MONTH FROM data) AS mes,
    TO_CHAR(data, 'Month') AS nome_mes,
    EXTRACT(DAY FROM data) AS dia_mes,
    
    -- Dia da semana (ajustado: 1=Dom, 7=Sáb)
    EXTRACT(DOW FROM data) + 1 AS dia_semana,
    TO_CHAR(data, 'Day') AS nome_dia_semana,
    
    -- Semana e dia do ano
    EXTRACT(WEEK FROM data) AS semana_ano,
    EXTRACT(DOY FROM data) AS dia_ano,
    
    -- Flags
    CASE 
        WHEN EXTRACT(DOW FROM data) IN (0, 6) THEN TRUE 
        ELSE FALSE 
    END AS eh_fim_semana,
    
    FALSE AS eh_feriado,
    NULL AS nome_feriado
    
FROM (
    -- Gerar série de datas (5 anos = 1826 dias)
    SELECT DATE '2016-01-01' + (n || ' days')::INTERVAL AS data
    FROM generate_series(0, 1825) AS n
) datas;

-- =====================================================
-- MARCAR FERIADOS BRASILEIROS
-- =====================================================

-- Ano Novo
UPDATE gold.dim_tempo 
SET eh_feriado = TRUE, nome_feriado = 'Ano Novo'
WHERE dia_mes = 1 AND mes = 1;

-- Natal
UPDATE gold.dim_tempo 
SET eh_feriado = TRUE, nome_feriado = 'Natal'
WHERE dia_mes = 25 AND mes = 12;

-- Black Friday (última sexta de novembro)
UPDATE gold.dim_tempo 
SET eh_feriado = TRUE, nome_feriado = 'Black Friday'
WHERE nome_dia_semana = 'Friday' 
  AND mes = 11 
  AND dia_mes BETWEEN 23 AND 29;

-- Tiradentes
UPDATE gold.dim_tempo 
SET eh_feriado = TRUE, nome_feriado = 'Tiradentes'
WHERE dia_mes = 21 AND mes = 4;

-- Dia do Trabalho
UPDATE gold.dim_tempo 
SET eh_feriado = TRUE, nome_feriado = 'Dia do Trabalho'
WHERE dia_mes = 1 AND mes = 5;

-- Independência do Brasil
UPDATE gold.dim_tempo 
SET eh_feriado = TRUE, nome_feriado = 'Independência'
WHERE dia_mes = 7 AND mes = 9;

-- Nossa Senhora Aparecida
UPDATE gold.dim_tempo 
SET eh_feriado = TRUE, nome_feriado = 'N. S. Aparecida'
WHERE dia_mes = 12 AND mes = 10;

-- Finados
UPDATE gold.dim_tempo 
SET eh_feriado = TRUE, nome_feriado = 'Finados'
WHERE dia_mes = 2 AND mes = 11;

-- Proclamação da República
UPDATE gold.dim_tempo 
SET eh_feriado = TRUE, nome_feriado = 'Proclamação da República'
WHERE dia_mes = 15 AND mes = 11;

-- =====================================================
-- VALIDAÇÃO
-- =====================================================

-- Verificar contagem total (deve ser 1826)
SELECT COUNT(*) AS total_dias FROM gold.dim_tempo;

-- Verificar distribuição por ano
SELECT ano, COUNT(*) AS dias 
FROM gold.dim_tempo 
GROUP BY ano 
ORDER BY ano;

-- Verificar feriados marcados
SELECT nome_feriado, COUNT(*) AS ocorrencias
FROM gold.dim_tempo
WHERE eh_feriado = TRUE
GROUP BY nome_feriado
ORDER BY ocorrencias DESC;

-- Exemplos de registros
SELECT * FROM gold.dim_tempo 
WHERE ano = 2018 AND mes = 11
ORDER BY data_completa
LIMIT 10;