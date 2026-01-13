# 🛍️ Olist Intelligent Data App

Interface visual para consumo de dados e interação com Agentes de Inteligência Artificial. Este dashboard foi projetado para ser **Stateless** e **Seguro**.

## 🛠️ Stack Tecnológica
* **Frontend:** Streamlit
* **Visualização:** Plotly / Altair
* **GenAI:** Google Gemini (via `google-generativeai`)
* **Configuração:** Pydantic Settings (Validação de Variáveis de Ambiente)

## ✨ Funcionalidades
1.  **Analytics Dashboard:** Conecta diretamente ao Lakehouse (DuckDB) para exibir KPIs da camada Gold.
2.  **Marketing Generator:** Agentes de IA que leem dados dos produtos e geram sugestões de marketing em tempo real.

---

## 🚀 Como Executar

### Opção A: Via Docker (Recomendado)
O dashboard sobe automaticamente junto com a stack.
Acesse no navegador:
👉 **[http://localhost:8501](http://localhost:8501)**

### Opção B: Execução Local (Desenvolvimento)
Se precisar rodar fora do Docker, você deve configurar o `PYTHONPATH` para a raiz do projeto e garantir que o `.env` exista.

```bash
# Na raiz do projeto (onde está o docker-compose.yml):
export PYTHONPATH=$PYTHONPATH:$(pwd)
streamlit run src/app/dashboard.py
```

---

## Segurança e Performance
Autenticação Zero-Touch
Removemos caixas de input de senha da interface. O Dashboard lê automaticamente a GOOGLE_API_KEY injetada de forma segura pelo Docker/System Environment via src.config.

* Benefício: Chaves não vazam em prints de tela ou logs de sessão.

Concorrência (DuckDB)
A conexão com o banco de dados Analytics (olist_gold.duckdb) é feita explicitamente em modo Leitura (read_only=True).

* Benefício: Permite que o Dashboard fique aberto consultando dados enquanto o pipeline dbt roda em background atualizando as tabelas, eliminando erros de "Database Lock".

---

## Resiliência (GenAI)
O aplicativo possui sistema de Fallback:

* Validação Prévia: Se a chave de API não for detectada pelo config.py, os widgets de IA são desabilitados automaticamente para evitar crash.

* Erros de Cota: Tratamento de exceção para limites da API do Gemini.