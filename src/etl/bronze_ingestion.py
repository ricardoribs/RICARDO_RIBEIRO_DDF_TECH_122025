import json
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from src.config import settings

class BronzeIngestor:
    def __init__(self, spark: SparkSession, lakehouse_path: Path):
        self.spark = spark
        self.lakehouse_path = Path(lakehouse_path) # Garante que é Pathlib
        self.schema_path = settings.SCHEMAS_DIR / "order_items.json"

    def _load_schema(self) -> StructType:
        """Carrega o schema JSON externo para garantir desacoplamento."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"❌ Arquivo de Schema não encontrado: {self.schema_path}")
            
        with open(self.schema_path, "r") as f:
            schema_json = json.load(f)
        return StructType.fromJson(schema_json)

    def ingest_orders(self, input_path: str):
        """
        Lê CSV bruto e salva em Parquet na camada Bronze.
        Valida existência do arquivo antes de processar.
        """
        path_obj = Path(input_path)
        
        # 1. Validação de Defesa (Fail Fast)
        if not path_obj.exists():
            raise FileNotFoundError(f"❌ Input file not found at: {path_obj.absolute()}")

        # 2. Carrega Schema Externo
        schema = self._load_schema()
        
        print(f"📥 Ingesting from: {path_obj.name}")
        
        # 3. Leitura com Schema aplicado (Enforce Schema)
        df = (
            self.spark.read
            .format("csv")
            .option("header", "true")
            .schema(schema) # Schema forte, nada de inferSchema (lento e perigoso)
            .load(str(path_obj))
        )

        # 4. Escrita na Bronze (Overwrite para garantir idempotência no batch diário)
        output_path = self.lakehouse_path / "bronze" / "order_items"
        
        (
            df.write
            .mode("overwrite")
            .format("parquet")
            .save(str(output_path))
        )
        
        print(f"✅ Saved to Bronze: {output_path}")