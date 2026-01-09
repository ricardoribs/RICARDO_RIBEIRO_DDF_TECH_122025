{{ config(materialized='table') }}

with source_data as (
    /* [CORREÇÃO SÊNIOR] 
       Substituímos o caminho manual por uma variável dbt (var).
       Isso centraliza a configuração: se a pasta mudar, 
       só precisamos alterar no dbt_project.yml.
    */
    select * from read_parquet('{{ var("lakehouse_path") }}/silver/order_items/*.parquet')
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