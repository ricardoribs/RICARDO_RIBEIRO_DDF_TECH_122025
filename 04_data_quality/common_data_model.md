# 🏛️ Common Data Model (CDM) - Olist E-commerce

Este documento define o **Modelo de Dados Comum (CDM)** padronizado para o ecossistema de e-commerce da Olist. Ele serve como referência para contratos de dados (Data Contracts), validação de qualidade (Great Expectations) e documentação de governança.

---

## Domínio: Pedidos (Orders)

### Entidade: ORDER
Representa o evento de uma compra realizada.

| Atributo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `order_id` | VARCHAR(32) | **PK** | Identificador único do pedido (Hash). |
| `customer_id` | VARCHAR(32) | **FK** | Referência ao cliente que fez o pedido. |
| `order_status` | ENUM | NOT NULL | Status: `delivered`, `shipped`, `canceled`, `invoiced`. |
| `purchase_timestamp` | TIMESTAMP | NOT NULL | Data e hora da compra. |
| `approved_at` | TIMESTAMP | NULLABLE | Data e hora da aprovação do pagamento. |
| `delivered_carrier_date` | TIMESTAMP | NULLABLE | Data de entrega à transportadora. |
| `delivered_customer_date`| TIMESTAMP | NULLABLE | Data de entrega ao cliente final. |
| `estimated_delivery_date`| TIMESTAMP | NOT NULL | Prazo prometido de entrega. |

### Entidade: ORDER_ITEM
Representa os produtos contidos dentro de um pedido.

| Atributo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `order_id` | VARCHAR(32) | **PK, FK** | Vínculo com o pedido pai. |
| `order_item_id` | INTEGER | **PK** | Número sequencial do item no pedido (1, 2, 3...). |
| `product_id` | VARCHAR(32) | **FK** | Referência ao produto vendido. |
| `seller_id` | VARCHAR(32) | **FK** | Referência ao vendedor responsável. |
| `price` | DECIMAL(10,2)| > 0 | Preço unitário do item. |
| `freight_value` | DECIMAL(10,2)| >= 0 | Valor do frete rateado para este item. |

### Entidade: PAYMENT
Detalhes financeiros da transação.

| Atributo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `order_id` | VARCHAR(32) | **FK** | Vínculo com o pedido. |
| `payment_sequential` | INTEGER | PK | Sequência do pagamento (caso use múltiplos cartões). |
| `payment_type` | ENUM | NOT NULL | `credit_card`, `boleto`, `voucher`, `debit_card`. |
| `payment_installments` | INTEGER | >= 1 | Número de parcelas. |
| `payment_value` | DECIMAL(10,2)| > 0 | Valor total pago nesta forma de pagamento. |

---

## Domínio: Participantes

### Entidade: CUSTOMER
Quem compra o produto.

| Atributo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `customer_id` | VARCHAR(32) | **PK** | ID do pedido do cliente (Key Transitória). |
| `customer_unique_id` | VARCHAR(32) | **UK** | ID único do cliente (CPF/Pessoa Real). |
| `customer_zip_code` | VARCHAR(5) | FK | CEP do cliente (Prefixo). |
| `customer_city` | VARCHAR | NOT NULL | Cidade de entrega. |
| `customer_state` | CHAR(2) | NOT NULL | UF (Sigla do Estado). |

### Entidade: SELLER
Quem vende o produto (Marketplace).

| Atributo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `seller_id` | VARCHAR(32) | **PK** | Identificador único do vendedor. |
| `seller_zip_code` | VARCHAR(5) | FK | CEP de origem. |
| `seller_city` | VARCHAR | NOT NULL | Cidade do vendedor. |
| `seller_state` | CHAR(2) | NOT NULL | UF do vendedor. |

---

## Domínio: Catálogo

### Entidade: PRODUCT
Características dos itens vendidos.

| Atributo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `product_id` | VARCHAR(32) | **PK** | Identificador único do produto. |
| `category_name` | VARCHAR | NULLABLE | Categoria principal (ex: `beleza_saude`). |
| `product_weight_g` | INTEGER | > 0 | Peso em gramas. |
| `product_length_cm` | INTEGER | > 0 | Comprimento da embalagem. |
| `product_height_cm` | INTEGER | > 0 | Altura da embalagem. |
| `product_width_cm` | INTEGER | > 0 | Largura da embalagem. |

---

## Domínio: Reputação

### Entidade: REVIEW
Avaliação do cliente após a compra.

| Atributo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `review_id` | VARCHAR(32) | **PK** | ID da avaliação. |
| `order_id` | VARCHAR(32) | **FK** | Pedido avaliado. |
| `review_score` | INTEGER | 1..5 | Nota de 1 (Péssimo) a 5 (Excelente). |
| `review_comment_title`| VARCHAR | NULLABLE | Título do comentário. |
| `review_comment_message`| TEXT | NULLABLE | Texto da avaliação. |
| `review_creation_date` | TIMESTAMP | NOT NULL | Data de envio da avaliação. |

---

### 📝 Padrões de Nomenclatura (Naming Conventions)
* **Tabelas:** Singular, UPPERCASE ou snake_case (ex: `ORDER_ITEM`).
* **Chaves Primárias:** `nome_tabela` + `_id` (ex: `product_id`).
* **Timestamps:** Sufixo `_date` ou `_timestamp` (UTC).
* **Valores Monetários:** DECIMAL(10,2).

---
*Documento gerado para conformidade com Data Quality Gates.*