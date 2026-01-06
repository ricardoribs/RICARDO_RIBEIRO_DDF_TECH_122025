import pytest
import pandas as pd
import os
import sys
import shutil

# --- Configuração de Caminhos ---
# Adiciona a pasta '08_pipelines' ao path para importar o módulo
PIPELINE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../08_pipelines'))
sys.path.append(PIPELINE_DIR)

from pipeline_avancado_observabilidade import load_data, validate_with_metrics, transform_data, save_data

def test_pipeline_ponta_a_ponta_happy_path():
    """
    Teste de Integração: Executa o fluxo completo (ETL) e verifica artefatos.
    Cenário: Dados normais, fluxo deve concluir com sucesso e gerar arquivo.
    """
    print("\n🔄 Iniciando Teste de Integração: Bronze -> Gold")

    # 1. Ingestão (Ler arquivo real)
    try:
        df_raw = load_data()
        print(f"   ✅ Ingestão OK: {len(df_raw)} registros.")
    except FileNotFoundError:
        pytest.fail("Arquivo de origem não encontrado. O teste de integração precisa da base de dados real.")

    # 2. Validação
    metrics = validate_with_metrics(df_raw)
    assert metrics['valid_records'] > 0, "A validação não deve rejeitar todos os registros"
    print("   ✅ Validação OK.")

    # 3. Transformação
    df_gold = transform_data(df_raw)
    assert 'total_revenue' in df_gold.columns, "Coluna de receita deve existir no Gold"
    assert 'seller_id' in df_gold.columns, "Coluna seller_id deve existir no Gold"
    print("   ✅ Transformação OK.")

    # 4. Carga (Salvar arquivo físico)
    output_path = save_data(df_gold)
    
    # 5. Verificação do Artefato Final
    assert os.path.exists(output_path), f"Arquivo final não foi criado em: {output_path}"
    
    # Verifica se o arquivo salvo não está vazio
    df_saved = pd.read_csv(output_path)
    assert len(df_saved) == len(df_gold), "O arquivo salvo no disco deve ter o mesmo tamanho do DataFrame em memória"
    print(f"   ✅ Carga OK: Arquivo gerado em {output_path}")

    # Limpeza (Cleanup) - Opcional, para não deixar lixo de teste
    # Comente a linha abaixo se quiser inspecionar o arquivo gerado pelo teste
    # if os.path.exists(output_path):
    #     os.remove(output_path)