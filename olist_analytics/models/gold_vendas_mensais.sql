{{ config(materialized='table') }}

-- Define o caminho do Lakehouse (padrão ou via variável)
{% set lakehouse = var('lakehouse_path', '../09_lakehouse') %}

with source_data as (
    -- Lê arquivos Parquet da camada Silver usando a função nativa do DuckDB
    -- O caminho é injetado dinamicamente pelo dbt
    select * from read_parquet('{{ lakehouse }}/silver/order_items/*.parquet')
)

select
    year(shipping_limit_date) as ano,
    month(shipping_limit_date) as mes,
    count(*) as total_pedidos,
    sum(price) as receita_total,
    avg(price) as ticket_medio,
    sum(freight_value) as total_frete
from source_data
group by 1, 2
order by 1, 2
