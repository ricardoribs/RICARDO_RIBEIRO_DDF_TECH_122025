# Usamos python:3.10-slim-bullseye (Debian 11) que é estável e TEM o Java 17
FROM python:3.10-slim-bullseye

# 1. Instalar Java (Obrigatório para o PySpark) e utilitários
# No Bullseye, o openjdk-17 está disponível nos backports ou direto
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless procps git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Configurar Variáveis de Ambiente do Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# 3. Diretório de Trabalho
WORKDIR /app

# 4. Instalar Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade google-generativeai

# 5. Copiar todo o código fonte
COPY . .

# 6. Comando padrão
CMD ["bash"]