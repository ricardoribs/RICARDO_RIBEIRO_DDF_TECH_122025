import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath, Field, SecretStr

class Settings(BaseSettings):
    # --- DADOS ---
    # Define caminhos padrão, mas permite sobrescrever via ENV VARS
    BASE_DIR: Path = Path("/app")
    RAW_DATA_DIR: DirectoryPath = Field(default=Path("/app/01_base_dados"))
    LAKEHOUSE_DIR: DirectoryPath = Field(default=Path("/app/09_lakehouse"))
    
    # --- SEGURANÇA (Obrigatórios) ---
    # SecretStr impede que a chave apareça em logs (print(settings.GOOGLE_API_KEY) mostra '**********')
    GOOGLE_API_KEY: SecretStr
    
    # --- SERVIÇOS ---
    PREFECT_API_URL: str = "http://prefect-server:4200/api"
    
    # Configuração Pydantic para ler arquivo .env automaticamente
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignora variáveis extras no .env
    )

# Instância única para ser importada em todo o projeto
try:
    settings = Settings()
except Exception as e:
    print("❌ ERRO CRÍTICO DE CONFIGURAÇÃO: Verifique seu arquivo .env")
    print(e)
    # Em produção, isso deve parar o container
    # raise e