SELECT 
    seller_id AS vendedor,
    COUNT(DISTINCT order_id) AS pedidos,
    ROUND(SUM(price) / 1000, 1) AS receita_k
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
GROUP BY 1
ORDER BY pedidos DESC
LIMIT 10;