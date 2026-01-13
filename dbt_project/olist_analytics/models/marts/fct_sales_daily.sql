{{
    config(
        materialized='incremental',
        unique_key='sales_date'
    )
}}

WITH source_data AS (
    SELECT *
    FROM {{ ref('stg_order_items') }}
),

daily_sales AS (
    SELECT
        CAST(sd.order_date AS DATE) AS sales_date,
        sd.order_id,
        sd.price,
        sd.freight_value
    FROM source_data AS sd

    {% if is_incremental() %}
    WHERE CAST(sd.order_date AS DATE) >
        (SELECT MAX(sales_date) FROM {{ this }})
    {% endif %}
),

aggregated AS (
    SELECT
        sales_date,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(price) AS total_revenue,
        AVG(price) AS avg_ticket,
        SUM(freight_value) AS total_freight
    FROM daily_sales
    GROUP BY 1
)

SELECT
    sales_date,
    total_orders,
    total_revenue,
    avg_ticket,
    total_freight
FROM aggregated
