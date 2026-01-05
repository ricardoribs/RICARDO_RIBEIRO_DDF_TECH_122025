import pandas as pd
import os
import datetime

# --- Configurações ---
# Caminhos relativos (ajuste conforme sua estrutura)
INPUT_PATH = "../01_base_dados/olist_order_items_dataset.csv"
OUTPUT_DIR = "saida_gold"
LOG_FILE = "pipeline_log.txt"

def log_message(message):
    """Registra logs da execução com timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {message}"
    
    # Tenta imprimir no terminal (pode falhar em alguns Windows antigos, então protegemos)
    try:
        print(full_msg)
    except UnicodeEncodeError:
        print(full_msg.encode('utf-8', errors='ignore').decode('utf-8'))

    # CORREÇÃO AQUI: Adicionado encoding="utf-8" para aceitar emojis no arquivo
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

def step_1_ingestao():
    """Simula a coleta de dados da Dadosfera."""
    log_message("🚀 Iniciando Step 1: Ingestão de Dados...")
    
    # Resolve caminho absoluto para evitar erros
    caminho_abs = os.path.abspath(INPUT_PATH)
    
    if not os.path.exists(caminho_abs):
        raise FileNotFoundError(f"Arquivo não encontrado em: {caminho_abs}")
    
    df = pd.read_csv(caminho_abs)
    log_message(f"✅ Ingestão concluída. Linhas carregadas: {len(df)}")
    return df

def step_2_validacao(df):
    """Verificação simples de qualidade (Data Quality)."""
    log_message("🔍 Iniciando Step 2: Validação de Qualidade...")
    
    # Regra 1: Sem IDs nulos
    if df['order_id'].isnull().any():
        raise ValueError("❌ Falha no Data Quality: IDs nulos encontrados!")
    
    # Regra 2: Preços positivos
    if (df['price'] <= 0).any():
        log_message("⚠️ Aviso: Existem preços zerados ou negativos.")
    else:
        log_message("✅ Check: Todos os preços são positivos.")
        
    log_message("✅ Validação concluída com sucesso.")
    return True

def step_3_transformacao(df):
    """Transformação para Camada Gold (Agregações)."""
    log_message("⚙️ Iniciando Step 3: Transformação e Modelagem...")
    
    # Exemplo: Criar tabela de performance por vendedor (igual ao nosso SQL)
    df_gold = df.groupby('seller_id').agg(
        total_vendas=('price', 'sum'),
        qtd_pedidos=('order_id', 'nunique'),
        ticket_medio=('price', 'mean')
    ).reset_index()
    
    # Ordenar por melhores vendedores
    df_gold = df_gold.sort_values(by='total_vendas', ascending=False)
    
    log_message(f"✅ Transformação concluída. Dataset final gerado com {len(df_gold)} vendedores.")
    return df_gold

def step_4_carga(df_gold):
    """Salva o resultado final (Load)."""
    log_message("💾 Iniciando Step 4: Carga (Save)...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    output_path = os.path.join(OUTPUT_DIR, "sellers_performance_gold.csv")
    df_gold.to_csv(output_path, index=False)
    
    log_message(f"✅ Arquivo salvo com sucesso em: {output_path}")

def main():
    log_message("=== INICIO DO PIPELINE DE DADOS ===")
    try:
        # Orquestração
        dados_brutos = step_1_ingestao()
        step_2_validacao(dados_brutos)
        dados_gold = step_3_transformacao(dados_brutos)
        step_4_carga(dados_gold)
        
        log_message("=== PIPELINE FINALIZADO COM SUCESSO ===")
        
    except Exception as e:
        log_message(f"❌ ERRO CRITICO NO PIPELINE: {str(e)}")

if __name__ == "__main__":
    main()