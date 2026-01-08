```markdown
# Olist Data App & GenAI Agents

Interface visual para consumo de dados e interação com Agentes de Inteligência Artificial.

## Stack Tecnológica
* **Frontend:** Streamlit
* **Visualização:** Plotly
* **GenAI:** Google Gemini (Texto/Prompting) + Hugging Face (Geração de Imagens)

## Funcionalidades
1.  **Analytics Dashboard:** Consome dados agregados da camada Gold (gerada pelo dbt).
2.  **Marketing Generator:** Agentes de IA que criam descrições e imagens de anúncios baseados nos dados dos produtos.

## Como Executar

```bash
streamlit run app.py
```

---

## Resiliência (GenAI)
O aplicativo possui sistema de Fallback:
* Se a API do Gemini falhar (cota/erro), um prompt de contingência é usado.

* Se o modelo de imagem falhar, o sistema tenta um modelo secundário mais leve.

