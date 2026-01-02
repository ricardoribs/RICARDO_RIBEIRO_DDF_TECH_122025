-- KPI 1: Receita Total
SELECT 
    ROUND(SUM(price + freight_value) / 1000000, 2) AS receita_milhoes
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;

-- KPI 2: Total de Pedidos
SELECT 
    COUNT(DISTINCT order_id) AS total_pedidos
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;

-- KPI 3: Ticket Médio
SELECT 
    ROUND(AVG(price + freight_value), 2) AS ticket_medio
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;

-- KPI 4: Total de Itens
SELECT 
    COUNT(*) AS total_itens
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS;