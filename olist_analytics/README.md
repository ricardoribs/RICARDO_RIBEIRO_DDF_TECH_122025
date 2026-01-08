```markdown
# 📊 Analytics Engineering (dbt + DuckDB)

Este módulo é responsável pela camada **Gold** do Data Lakehouse. Utilizamos **dbt** para transformação e **DuckDB** como engine SQL serverless para ler os arquivos Parquet gerados pelo Spark.

## 🛠️ Stack Tecnológica
* **Transformação:** dbt (data build tool)
* **Engine SQL:** DuckDB
* **Fonte de Dados:** Arquivos Parquet (Camada Silver)

## 🎯 Modelos
* `gold_vendas_mensais`: Agregação de vendas por ano e mês, calculando ticket médio e receita total.

## 🚀 Como Executar

Para materializar as tabelas da camada Gold:

```bash
# Dentro da pasta olist_analytics/
dbt run --profiles-dir .
```
---

## Testes e Documentação
Para gerar a documentação automática do projeto e linhagem de dados:
```Bash
dbt docs generate
dbt docs serve
```
