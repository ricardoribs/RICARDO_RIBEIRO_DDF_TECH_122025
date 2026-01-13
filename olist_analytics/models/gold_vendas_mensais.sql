{{ config(materialized='table') }}

WITH vendas_diarias AS (
    SELECT
        DATE_TRUNC('month', order_purchase_timestamp) AS mes_referencia
        , COUNT(DISTINCT order_id) AS total_pedidos
        , SUM(price) AS receita_total
        , AVG(price) AS ticket_medio
    -- CORREÇÃO: Usamos source() pois estamos lendo do Data Lake (Parquet), não de outro modelo dbt
    FROM {{ source('lakehouse', 'orders_enriched') }}
    WHERE order_status = 'delivered'
    GROUP BY 1
)

SELECT * FROM vendas_diarias
ORDER BY mes_referencia DESC