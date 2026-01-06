import os
import json
import pandas as pd
from great_expectations.dataset import PandasDataset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', '01_base_dados', 'olist_order_items_dataset.csv')
REPORT_FILE = os.path.join(BASE_DIR, 'resultado_validacao.json')


def run_data_quality():
    print("🚀 Iniciando Validação de Qualidade de Dados (GX Estável)")

    df = pd.read_csv(DATA_PATH)
    print(f"📊 Dataset carregado com {len(df)} registros")

    validator = PandasDataset(df)

    validator.expect_column_values_to_not_be_null("order_id")
    validator.expect_column_values_to_not_be_null("product_id")
    validator.expect_column_values_to_not_be_null("seller_id")

    validator.expect_column_values_to_match_regex(
        "order_id", r"^[a-f0-9]{32}$"
    )

    validator.expect_column_values_to_be_between("price", min_value=0.01)
    validator.expect_column_values_to_be_between("freight_value", min_value=0.0)
    validator.expect_column_values_to_be_of_type("order_item_id", "int64")

    validator.expect_column_values_to_match_strftime_format(
        "shipping_limit_date", "%Y-%m-%d %H:%M:%S"
    )

    validator.expect_column_mean_to_be_between(
        "price", min_value=50, max_value=250
    )

    results = validator.validate()

    with open(REPORT_FILE, "w") as f:
        json.dump(results.to_json_dict(), f, indent=2)

    print("✅ Validação finalizada com sucesso")
    print(f"📄 Evidência salva em: {REPORT_FILE}")


if __name__ == "__main__":
    run_data_quality()
