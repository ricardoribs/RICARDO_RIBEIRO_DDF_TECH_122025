import os

# Mapeamento de Arquivo -> [Lista de Substituições (De, Para)]
substituicoes = {
    "01_base_dados/README.md": [
        ("Capturar.JPG", "print_carga_inicial.jpg"),
        ("dadosfera.JPG", "print_interface_dadosfera.jpg"),
        ("microtransformacao_sql.JPG", "print_microtransformacao.jpg"),
        ("catalogo_bronze.PNG", "print_catalogo_bronze.png"),
    ],
    "04_data_quality/README.md": [("relatorio_gx.PNG", "print_relatorio_gx.png")],
    "07_analise_visualizacao/README.md": [
        ("dashboard_completo.PNG", "print_dashboard_metabase.png")
    ],
    "08_pipelines/README.md": [
        ("pipeline.JPG", "print_pipeline_fluxo.jpg"),
        ("pipeline_dadosfera.PNG", "print_pipeline_dadosfera.png"),
    ],
    "09_data_app/README.md": [("print_streamlit_app.PNG", "print_streamlit_app.png")],
}


def corrigir_links():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("🔄 Iniciando correção de links nos READMEs...")

    for arquivo_relativo, trocas in substituicoes.items():
        caminho_arquivo = os.path.join(base_dir, arquivo_relativo)

        if not os.path.exists(caminho_arquivo):
            print(f"⚠️ Arquivo não encontrado (pulando): {arquivo_relativo}")
            continue

        # Ler conteúdo
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Fazer substituições
        conteudo_novo = conteudo
        alterado = False
        for antigo, novo in trocas:
            if antigo in conteudo_novo:
                conteudo_novo = conteudo_novo.replace(antigo, novo)
                alterado = True
                print(f"   ✅ Em {arquivo_relativo}: '{antigo}' -> '{novo}'")

        # Salvar se houve mudança
        if alterado:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(conteudo_novo)
            print(f"💾 Salvo: {arquivo_relativo}")
        else:
            print(f"ℹ️ Nenhuma alteração necessária em: {arquivo_relativo}")

    print("\n✨ Todos os links foram atualizados!")


if __name__ == "__main__":
    corrigir_links()
