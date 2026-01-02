SELECT 
    CASE 
        WHEN price < 50 THEN 'Até R$ 50'
        WHEN price < 100 THEN 'R$ 50-100'
        WHEN price < 200 THEN 'R$ 100-200'
        ELSE 'Acima R$ 200'
    END AS faixa_preco,
    COUNT(*) AS quantidade
FROM TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS
GROUP BY 1
ORDER BY 1;