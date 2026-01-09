{{ config(materialized='table') }}

with source_data as (
    select * from {{ source('lakehouse', 'order_items') }}
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
