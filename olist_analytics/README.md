# 📊 Analytics Engineering (dbt + DuckDB)

Este módulo é responsável pela camada **Gold** do Data Lakehouse. Utilizamos **dbt** para transformação, **DuckDB** como engine SQL serverless e **SQLFluff** para garantir a qualidade do código.

## 🛠️ Stack Tecnológica
* **Transformação:** dbt (data build tool) - Core v1.x
* **Engine SQL:** DuckDB (Modo Arquivo Local)
* **Qualidade de Código:** SQLFluff (Linter & Fixer)
* **Arquitetura:** Medalhão (Staging -> Marts)

---

## 🧹 Qualidade de Código (SQL Linting)

Implementamos um rigoroso padrão de qualidade usando **SQLFluff** com dialeto dbt/DuckDB. O CI/CD falhará se o código não estiver padronizado.

### Regras Principais
1.  **Aliasing Explícito:** Todo JOIN deve ter alias, e todas as colunas devem ter referência (ex: `o.order_id` e não apenas `order_id`).
2.  **Leading Commas:** Vírgulas no início da linha para facilitar diffs no Git.
3.  **Indentação:** 4 espaços.

### 🛠️ Como corrigir seu SQL automaticamente
Se o seu código estiver "feio", não perca tempo formatando na mão. Use o comando mágico dentro do container:

```bash
# Opção 1: Rodar de fora (via Docker Exec)
docker exec -it olist_etl_worker sqlfluff fix /app/dbt_project/olist_analytics/models --force

# Opção 2: Rodar de dentro (se estiver logado no shell)
sqlfluff fix models/ --force
```
---

## Estrutura de Modelos

## 📂 Camadas do Projeto

| Camada  | Tipo                 | Descrição                                                                 |
|-------- |----------------------|---------------------------------------------------------------------------|
| Staging | View                 | Limpeza leve dos dados, renomeação de colunas e casting de tipos (ex: `stg_order_items`). |
| Marts   | Incremental / Table  | Tabelas fato e dimensão prontas para consumo analítico e ferramentas de BI. |

Destaque: fct_sales_daily
Modelo Incremental que utiliza lógica de deduplicação e watermark para processar apenas novos dados, garantindo idempotência.

---

## Como Executar
Em produção, o Prefect orquestra o dbt automaticamente. Para desenvolvimento ou testes manuais:

Via Docker (Recomendado)
Para rodar todos os modelos garantindo que o ambiente é idêntico à produção:

```bash
docker exec -it olist_etl_worker dbt run --project-dir /app/dbt_project/olist_analytics --profiles-dir /app/dbt_project/olist_analytics
```

Comandos Úteis:

```bash
# Validar conexões
dbt debug

# Instalar pacotes (dbt-utils, etc)
dbt deps

# Gerar Documentação e Linhagem
dbt docs generate
dbt docs serve
```

---

## Troubleshooting: Database Lock
O DuckDB é um banco baseado em arquivo único.

* Erro: IO Error: Cannot open file... file is currently open by another process.

* Causa: Você provavelmente está com o Streamlit ou DBeaver aberto bloqueando a escrita.

* Solução: O Dashboard já está configurado como read_only=True, mas se o erro persistir, encerre conexões externas antes de rodar o dbt run.