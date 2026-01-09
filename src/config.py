import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (se existir)
load_dotenv()

class Config:
    """
    Centraliza todas as configurações do projeto.
    Usa pathlib para garantir compatibilidade entre Windows, Linux e Docker.
    """
    # Define a raiz do projeto (sobe 2 níveis a partir deste arquivo)
    BASE_DIR = Path(__file__).parent.parent.absolute()
    
    # Caminhos de Dados
    RAW_DATA_DIR = BASE_DIR / "01_base_dados"
    LAKEHOUSE_DIR = BASE_DIR / "09_lakehouse"
    
    # Credenciais e APIs
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    PREFECT_API_URL = os.getenv("PREFECT_API_URL")
    
    # Configurações do Spark
    SPARK_APP_NAME = "Olist_Modern_Stack"
    # No Docker, usamos local[*], mas em prod apontaríamos para o Master do Cluster
    SPARK_MASTER = "local[*]" 

# Instância única para importar no resto do projeto
settings = Config()