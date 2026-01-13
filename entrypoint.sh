#!/bin/bash
set -e
set -o pipefail 

echo "🚀 [1/2] Aguardando conexão com Prefect Server..."

# Loop infinito até o servidor responder HTTP 200 na API
# Isso garante que o worker não tente registrar o fluxo antes do servidor estar pronto
while ! curl -s --fail http://prefect-server:4200/api/health > /dev/null; do
    echo "⏳ Aguardando servidor Prefect subir..."
    sleep 5
done

echo "✅ Servidor Online! Conectado."

echo "🔥 [2/2] Iniciando Worker de Produção (Modo Serve)..."
echo "ℹ️  O script Python ficará rodando em loop aguardando o agendamento (06:00 AM)."
echo "ℹ️  Para testar agora, acesse http://localhost:4200 e clique em 'Quick Run'."

# Executa o serviço Python.
# O comando NÃO vai terminar (a menos que dê erro), pois está em modo .serve()
# O dbt agora roda DENTRO deste fluxo, como uma task.
python -m src.orchestration.flow_main 2>&1 | tee /app/logs/etl_execution.log