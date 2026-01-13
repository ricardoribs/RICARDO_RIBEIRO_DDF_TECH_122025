# ==========================================
# Estágio 1: Builder (Compilação pesada)
# ==========================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Instala dependências de sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ==========================================
# Estágio 2: Runner (Imagem final com Java e Curl)
# ==========================================
FROM python:3.10-slim AS runner

WORKDIR /app

# --- CORREÇÃO AQUI ---
# Instala Java (para Spark), Procps (para monitorização) e Curl (para healthcheck)
RUN apt-get update && apt-get install -y \
    default-jre \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configura JAVA_HOME
ENV JAVA_HOME="/usr/lib/jvm/default-java"

# Variáveis de Ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH \
    PREFECT_API_URL=""

# Copia as libs instaladas do builder
COPY --from=builder /root/.local /root/.local

# Copia o código fonte
COPY . .

# Cria diretório de logs
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Script de entrada
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
  CMD test -f /app/src/orchestration/flow_main.py || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]