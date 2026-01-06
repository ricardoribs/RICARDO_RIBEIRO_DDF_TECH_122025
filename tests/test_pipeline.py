import pytest
import pandas as pd
import sys
import os

# --- Configuração de Caminho para Importação ---
# Adiciona a pasta '08_pipelines' ao path do Python para conseguir importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../08_pipelines')))

# Importa as funções do nosso pipeline mais avançado
from pipeline_avancado_observabilidade import load_data, validate_with_metrics, transform_data

def test_ingestao_retorna_dataframe_valido():
    """
    Testa se a função de carga consegue ler o arquivo e retorna um DataFrame
    com dados (Smoke Test).
    """
    try:
        df = load_data()
        assert isinstance(df, pd.DataFrame), "O retorno deve ser um DataFrame pandas"
        assert len(df) > 0, "O DataFrame não deve estar vazio"
        # Opcional: Checar colunas críticas
        assert 'order_id' in df.columns
        assert 'price' in df.columns
    except FileNotFoundError:
        pytest.skip("Arquivo de dados original não encontrado para teste de integração.")

def test_validacao_detecta_precos_invalidos():
    """
    Testa se a função de validação contabiliza corretamente preços zerados ou negativos.
    """
    # 1. Criar DataFrame Mock (Falso) com erro
    df_invalido = pd.DataFrame({
        'order_id': ['1', '2'],
        'price': [-10.0, 50.0],  # Um preço negativo (ERRO)
        'freight_value': [10.0, 10.0]
    })
    
    # 2. Rodar validação
    metrics = validate_with_metrics(df_invalido)
    
    # 3. Assertivas
    # Esperamos 1 registro válido e 1 falha
    assert metrics['valid_records'] == 1
    assert metrics['checks_failed'] >= 1

def test_validacao_detecta_frete_negativo():
    """
    Testa se a lógica de validação pega fretes negativos.
    """
    df_frete_ruim = pd.DataFrame({
        'order_id': ['3'],
        'price': [100.0],
        'freight_value': [-5.0] # Frete negativo (ERRO)
    })
    
    metrics = validate_with_metrics(df_frete_ruim)
    assert metrics['checks_failed'] > 0

def test_transformacao_agrega_corretamente():
    """
    Testa se a transformação Gold está somando as receitas corretamente.
    """
    # Dados de entrada: Seller A vendeu 100 e 200
    df_input = pd.DataFrame({
        'seller_id': ['Seller_A', 'Seller_A', 'Seller_B'],
        'price': [100.0, 200.0, 50.0],
        'freight_value': [10.0, 10.0, 5.0],
        'order_id': ['1', '2', '3']
    })
    
    # Executa transformação
    df_gold = transform_data(df_input)
    
    # Verifica Seller A
    row_a = df_gold[df_gold['seller_id'] == 'Seller_A'].iloc[0]
    assert row_a['total_revenue'] == 300.0  # 100 + 200
    assert row_a['total_orders'] == 2       # 2 pedidos