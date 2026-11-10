from pathlib import Path

from src.microatividades import executar_microatividades, ler_csv
from src.tratamento_dados import salvar_csv, tratar_dados


DIRETORIO_DADOS = Path(__file__).resolve().parent / "dados"
CSV_ORIGINAL = DIRETORIO_DADOS / "dados_originais.csv"
CSV_TRATADO = DIRETORIO_DADOS / "dados_tratados.csv"


def main(caminho_original: Path = CSV_ORIGINAL, caminho_tratado: Path = CSV_TRATADO) -> None:
    if caminho_original.resolve() == caminho_tratado.resolve():
        raise SystemExit("Use arquivos diferentes para o CSV original e o CSV tratado.")

    try:
        dados_originais = ler_csv(caminho_original)
    except FileNotFoundError:
        raise SystemExit(
            "CSV original da faculdade não encontrado. "
            f"Coloque o arquivo em {caminho_original}."
        ) from None
    except (OSError, ValueError) as erro:
        raise SystemExit(f"Não foi possível ler o CSV original. {erro}") from None

    executar_microatividades(dados_originais)
    dados_tratados = tratar_dados(dados_originais)
    salvar_csv(dados_tratados, caminho_tratado)
    print(f"\nRegistros antes do tratamento: {len(dados_originais)}")
    print(f"Registros após o tratamento: {len(dados_tratados)}")
    print(f"Arquivo gerado: {caminho_tratado}")


if __name__ == "__main__":
    main()
