# Dicionário de Dados - Olist E-commerce

**Fonte:** [Kaggle - Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
**Contexto:** Dados reais de e-commerce brasileiro contendo 100k pedidos entre 2016 e 2018.

## 🗂️ Estrutura Relacional

O esquema segue um modelo que permite análises de vendas, logística e comportamento do consumidor.

### 1. Tabela Fato: `olist_order_items_dataset.csv`
Esta é a tabela principal para análise de receita. Cada linha é um item dentro de um pedido.
* **Registros:** >112.000 (Atende ao requisito do Case >100k)
* `order_id` (String): Identificador único do pedido.
* `order_item_id` (Int): Número sequencial do item no pedido.
* `product_id` (String): ID do produto (FK).
* `seller_id` (String): ID do vendedor (FK).
* `shipping_limit_date` (Date): Data limite de envio.
* `price` (Float): Preço do item.
* `freight_value` (Float): Valor do frete do item.

### 2. Tabela Fato: `olist_orders_dataset.csv`
Contém o status e as datas do pedido como um todo.
* `order_id` (String): PK.
* `customer_id` (String): ID do cliente (FK).
* `order_status` (String): Status (delivered, shipped, canceled).
* `order_purchase_timestamp` (Timestamp): Data da compra.

### 3. Dimensão: `olist_products_dataset.csv`
Detalhes dos produtos vendidos.
* `product_id` (String): PK.
* `product_category_name` (String): Categoria (Ex: beleza_saude).
* `product_weight_g` (Int): Peso em gramas.

### 4. Dimensão: `olist_customers_dataset.csv`
Detalhes dos compradores.
* `customer_id` (String): PK (chave para orders).
* `customer_unique_id` (String): Identificador único real do cliente.
* `customer_city` (String): Cidade.
* `customer_state` (String): Estado (Sigla).

---
## 📚 Catálogo de Dados (Camada Bronze)

| Tabela Técnica | Nome de Negócio | Camada | Descrição |
|---|---|---|---|
| `TB__E8M6XA__PUBLIC__OLIST_ORDER_ITEMS` | Itens de Pedidos | **[BRONZE]** | Dados brutos contendo preço, frete e IDs. Ingestão direta do PostgreSQL. |