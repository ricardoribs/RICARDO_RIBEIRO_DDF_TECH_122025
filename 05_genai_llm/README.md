# Item 5 - GenAI e LLMs: Extração de Features com Gemini

## Objetivo

Transformar dados não estruturados de produtos em features estruturadas usando **Google Gemini 2.5 Flash**, permitindo análises avançadas e enriquecimento do catálogo.

---

## Tecnologia Utilizada

### Modelo: **Gemini 2.5 Flash**

* **Provider:** Google AI
* **Vantagens:**

  * Gratuito (tier free)
  * Rápido (flash variant)
  * Suporte nativo a JSON
  * Português brasileiro
* **Limitações:**

  * Rate limit restrito (60 requests/min no free tier)
  * Necessita pausa de 10-15s entre requests

---

## Processo de Extração

### INPUT (Dados Brutos):

```
Categoria Original: esporte_lazer
Peso: 400.0g
Dimensões (CxLxA): 24x18x11 cm
```

### PROCESSING (Gemini 2.5):

```python
SYSTEM_PROMPT = """
Você é um especialista em categorização de produtos e Master Data Management.
Analise os dados técnicos do produto e enriqueça as informações.

SCHEMA JSON ESPERADO:
{
  "categoria_normalizada": "string",
  "subcategoria": "string",
  "tags": ["string"],
  "perfil_logistico": "string",
  "publico_alvo": "string",
  "sugestao_nome_produto": "string"
}
"""
```

### OUTPUT (Features Estruturadas):

```json
{
  "categoria_normalizada": "Esporte e Lazer",
  "tags": ["esporte", "lazer", "atividade física", "recreação"],
  "publico_alvo": "Geral, entusiastas de esporte e lazer",
  "perfil_logistico": "Leve",
  "sugestao_nome_produto": "Kit Esportivo Versátil"
}
```

---

## Resultados Obtidos

### Métricas da Execução:

| Métrica                 | Valor                 |
| ----------------------- | --------------------- |
| Produtos processados    | 10 (amostra)          |
| Taxa de sucesso         | 80% (8/10)            |
| Tempo médio por produto | 13.75s                |
| Tempo total             | 2min 17s              |
| Custo                   | $0.00 (tier gratuito) |

### Features Extraídas por Produto:

1. categoria_normalizada
2. tags
3. publico_alvo
4. perfil_logistico
5. sugestao_nome_produto

---

## Análise dos Resultados

### Exemplo Real - Produto 1:

**Input:**

```
Categoria Original: esporte_lazer
Peso: 400g
Dimensões: 24x18x11cm
```

**Output Gemini:**

```json
{
  "categoria_normalizada": "esporte_lazer",
  "tags": ["esporte", "lazer", "atividade física", "recreação", "fitness"],
  "publico_alvo": "Geral, entusiastas de esporte e lazer, pessoas ativas"
}
```

**Valor Agregado:**

* 5 tags descritivas geradas
* Público-alvo identificado
* Perfil para sistema de recomendação

---

### Exemplo Real - Produto 2:

**Input:**

```
Categoria Original: moveis_decoracao
Peso: 1300g
Dimensões: 60x12x12cm
```

**Output Gemini:**

```json
{
  "categoria_normalizada": "Móveis e Decoração",
  "tags": ["móveis", "decoração", "casa", "ambiente", "lar", "design"],
  "publico_alvo": "Adultos, proprietários de casas, pessoas interessadas em decoração"
}
```

**Valor Agregado:**

* Categoria normalizada (padrão consistente)
* 6 tags para busca semântica
* Segmentação clara de público

---

## Implementação Técnica

### Arquitetura do Código:

```python
# 1. Preparação de Dados
df["descricao_sintetica"] = df.apply(criar_descricao_sintetica, axis=1)

# 2. Configuração do Modelo
model = genai.GenerativeModel("models/gemini-2.5-flash")

# 3. Extração com Rate Limit Control
for row in df_sample.iterrows():
    features = extrair_features_safe(row["descricao_sintetica"])
    resultados.append(features)
    time.sleep(10)

# 4. Exportação
df_final.to_csv("olist_enriched_sample.csv")
```

### Tratamento de Erros:

```python
def extrair_features_safe(texto):
    try:
        resp = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(resp.text)
    except Exception as e:
        if "429" in str(e):
            time.sleep(30)
        return None
```

---

## Análise de Custos

### Gemini 2.5 Flash (Tier Gratuito):

| Cenário      | Produtos | Tempo Estimado | Custo |
| ------------ | -------- | -------------- | ----- |
| Teste        | 10       | 2-3 min        | $0.00 |
| Piloto       | 100      | 20-30 min      | $0.00 |
| Produção     | 1.000    | 3-4 horas      | $0.00 |
| Full Dataset | 32.950   | ~5 dias        | $0.00 |

### Comparativo com OpenAI:

| Modelo           | 1.000 produtos | 32.950 produtos |
| ---------------- | -------------- | --------------- |
| Gemini 2.5 Flash | $0.00          | $0.00           |
| GPT-3.5-turbo    | $0.50          | $16.50          |
| GPT-4            | $5.00          | $165.00         |

---

## Estrutura de Arquivos

```
05_genai_llm/
├── README.md
├── notebooks/
│   └── extracao_features_gemini.ipynb
├── datasets/
│   ├── olist_enriched_sample.csv
│   └── olist_enriched_sample.json
├── prompts/
│   └── system_prompt.txt
└── analises/
    └── resultados_extracao.md
```

---

## Casos de Uso

### Enriquecimento de Catálogo

Produtos com informações incompletas enriquecidos automaticamente com categorias, tags e descrições.

### Normalização de Categorias

Padronização de categorias inconsistentes em um conjunto controlado.

### Sistema de Recomendação

Uso de tags como features para cálculo de similaridade.

### Segmentação de Público

Identificação automática de público-alvo para marketing.

---

## Conclusão

O uso do Gemini 2.5 Flash permitiu enriquecer dados não estruturados de forma automatizada, gratuita e escalável, gerando valor direto para análise, recomendação e tomada de decisão.

**Status:** COMPLETO

**Desenvolvido por:** Ricardo Ribeiro
**Data:** Janeiro/2026
**Contexto:** Case Técnico Dadosfera - Item 5
