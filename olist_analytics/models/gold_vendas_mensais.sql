{{ config(materialized='table') }}

with vendas_diarias as (
    select
        date_trunc('month', order_purchase_timestamp) as mes_referencia
        , count(distinct order_id) as total_pedidos
        , sum(price) as receita_total
        , avg(price) as ticket_medio
    from {{ source('lakehouse', 'orders_enriched') }}
    where order_status = 'delivered'
    group by 1
)

select * from vendas_diarias
order by mes_referencia desc