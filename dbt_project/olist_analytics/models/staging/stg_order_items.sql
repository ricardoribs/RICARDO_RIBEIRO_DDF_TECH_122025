with source as (
    select * from {{ source('lakehouse', 'order_items') }}
),

renamed as (
    select
        -- Identificadores
        order_id,
        order_item_id,
        product_id,
        seller_id,

        -- Métricas (Garantindo tipo numérico para o DuckDB)
        cast(price as double) as price,
        cast(freight_value as double) as freight_value,

        -- Datas
        -- TRUQUE DE ENGENHARIA:
        -- Como a tabela 'orders' (cabeçalho) não foi processada no pipeline ETL,
        -- usamos a 'shipping_limit_date' existente no item como um proxy da data de venda.
        cast(shipping_limit_date as timestamp) as order_date,
        
        -- Mantemos a coluna original também para histórico
        cast(shipping_limit_date as timestamp) as shipping_limit_date

    from source
)

select * from renamed