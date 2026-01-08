{{ config(materialized='table') }}

/* A mágica acontece aqui: O DuckDB lê direto do Parquet gerado pelo Spark.
   Usamos o caminho relativo para sair da pasta do dbt e achar o lakehouse.
*/
with source_data as (
    select * from read_parquet('../09_lakehouse/silver/order_items/*.parquet')
)

select
    -- Extração de Ano e Mês (Sintaxe DuckDB/Postgres)
    year(shipping_limit_date) as ano,
    month(shipping_limit_date) as mes,

    -- KPIs
    count(*) as total_pedidos,
    sum(price) as receita_total,
    avg(price) as ticket_medio,
    sum(freight_value) as total_frete

from source_data
group by 1, 2
order by 1, 2