SELECT 
    DATE_TRUNC('month', CAST(shipping_limit_date AS DATE)) AS mes,
    SUM(price) AS receita,
    COUNT(DISTINCT order_id) AS pedidos
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
WHERE shipping_limit_date IS NOT NULL
GROUP BY 1
ORDER BY 1;