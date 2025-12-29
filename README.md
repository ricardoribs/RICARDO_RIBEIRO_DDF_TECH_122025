### Case Técnico Dadosfera – Engenharia de Dados

Autor: Ricardo Ribeiro
Data: Dezembro/2025
Contexto: Implementação de Plataforma de Dados End-to-End para E-commerce.

## Item 0: Planejamento e Agilidade

Este projeto adota uma abordagem híbrida, combinando planejamento estruturado com entregas incrementais, priorizando valor contínuo, controle de riscos e evolução progressiva da solução.

Abaixo, o status atual das atividades do projeto:

ID	Atividade	Estimativa	Status	Dependência
00	Planejamento e Estruturação do Repositório	1h	Concluído	-
01	Seleção e Aquisição de Dados (>100k rows)	2h	Em andamento	00
02	Ingestão na Dadosfera (Carga + Microtransformação)	3h	Pendente	01
03	Catalogação e Criação do Dicionário de Dados	2h	Pendente	02
04	Análise de Qualidade de Dados (Data Quality)	4h	Pendente	03
05	Processamento com GenAI (Criação de Features via LLM)	5h	Pendente	01, 02
06	Modelagem de Dados Analítica (Star Schema)	4h	Pendente	04, 05
07	Análise de Dados e Construção de Dashboard (Metabase)	5h	Pendente	06
08	Construção de Pipelines de Dados (Automação)	4h	Pendente	06
09	Desenvolvimento de Data Apps (Streamlit)	6h	Pendente	07
10	Gravação e Preparação da Apresentação Final	4h	Pendente	00–09

## Análise de Riscos (Principais Pontos)

1. Rate Limit da API OpenAI
Mitigação por meio de processamento em batch, uso de backoff exponencial e controle de volume de requisições.

2. Qualidade e Consistência dos Dados
Mitigação por meio de validações automatizadas utilizando Great Expectations, aplicadas antes da persistência dos dados na plataforma.

## Estrutura do Projeto

1. 00_planejamento/
Documentação do planejamento, metodologia adotada e análise completa de riscos.

2. 01_base_dados/
Scripts de aquisição, amostras e dicionários da base de dados Olist (mais de 100 mil registros).

3. Demais diretórios serão adicionados progressivamente conforme o avanço do projeto e das entregas.
