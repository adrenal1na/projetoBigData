from pathlib import Path

import pandas as pd


COLUNAS_OBRIGATORIAS = ["ID", "Duration", "Date", "Pulse", "Maxpulse", "Calories"]


def ler_csv(caminho: Path) -> pd.DataFrame:
    """Lê o CSV sem converter as datas antes da inspeção."""
    # Tipos anuláveis preservam os inteiros mesmo em colunas com lacunas.
    dados = pd.read_csv(
        caminho,
        sep=";",
        engine="python",
        dtype={"Date": "string"},
        dtype_backend="numpy_nullable",
    )
    if dados.columns.tolist() != COLUNAS_OBRIGATORIAS:
        cabecalho = ";".join(COLUNAS_OBRIGATORIAS)
        raise ValueError(f"O cabeçalho deve ser {cabecalho}.")
    if dados.empty:
        raise ValueError("O CSV contém apenas o cabeçalho, sem registros.")
    # Com campos extras, o Pandas pode interpretar a primeira coluna como índice.
    if not isinstance(dados.index, pd.RangeIndex):
        raise ValueError("Há registros com mais campos do que o cabeçalho do CSV.")
    return dados


def selecionar_colunas(dados: pd.DataFrame) -> pd.DataFrame:
    """Cria um subconjunto independente com três colunas."""
    return dados[["ID", "Date", "Calories"]].copy()


def exibir_registros(dados: pd.DataFrame) -> None:
    # A opção de visualização só vale durante esta exibição.
    with pd.option_context("display.max_rows", 9999):
        print(dados.to_string())


def exibir_primeiras_e_ultimas(dados: pd.DataFrame) -> None:
    print("Primeiras 10 linhas")
    print(dados.head(10))
    print("Últimas 10 linhas")
    print(dados.tail(10))


def exibir_informacoes(dados: pd.DataFrame) -> None:
    dados.info(memory_usage="deep")
    linhas, colunas = dados.shape
    print(f"Dimensões: {linhas} linhas e {colunas} colunas")
    print("Tipos por coluna")
    print(dados.dtypes.to_string())
    print("Valores nulos por coluna")
    nulos = dados.isna().sum()
    print(nulos.to_string())
    print(f"Total de valores nulos: {nulos.sum()}")


def executar_microatividades(dados: pd.DataFrame) -> None:
    print("\nMicroatividade 1 — Leitura do CSV")
    print(dados)

    print("\nMicroatividade 2 — Subconjunto de dados")
    print(selecionar_colunas(dados))

    print("\nMicroatividade 3 — Exibição de todos os registros")
    exibir_registros(dados)

    print("\nMicroatividade 4 — Primeiras e últimas linhas")
    exibir_primeiras_e_ultimas(dados)

    print("\nMicroatividade 5 — Informações gerais")
    exibir_informacoes(dados)
