import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Caminhos dinâmicos baseados na localização deste arquivo
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    
    # Mapeamento de pastas
    RAW_DATA_DIR = PROJECT_ROOT / "01_base_dados"
    LAKEHOUSE_DIR = PROJECT_ROOT / "09_lakehouse"
    
    # Credenciais
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

settings = Settings()