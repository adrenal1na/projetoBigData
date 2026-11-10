from pathlib import Path

import pandas as pd

from .microatividades import exibir_informacoes, exibir_primeiras_e_ultimas


DATA_TEMPORARIA = "1900/01/01"
DATA_COMPACTA = "20201226"


def demonstrar_conversao(datas: pd.Series) -> None:
    """Exibe o resultado real da tentativa de conversão intermediária."""
    try:
        conversao = pd.to_datetime(datas)
    except ValueError as erro:
        print(f"A conversão inicial encontrou formatos incompatíveis: {erro}")
    else:
        print("Resultado da conversão inicial")
        print(conversao.to_string())


def tratar_dados(dados_originais: pd.DataFrame) -> pd.DataFrame:
    print("\nEtapa 1 — Importação e inspeção")
    exibir_informacoes(dados_originais)
    exibir_primeiras_e_ultimas(dados_originais)
    dados = dados_originais.copy(deep=True)

    print("\nEtapa 2 — Tratamento de Calories")
    calorias_ausentes = dados["Calories"].isna()
    print("Registros com calorias ausentes")
    print(dados.loc[calorias_ausentes].to_string(index=False))
    dados["Calories"] = dados["Calories"].fillna(0)
    print("Registros após o preenchimento")
    print(dados.loc[calorias_ausentes, ["ID", "Calories"]].to_string(index=False))
    if dados["Calories"].isna().any():
        raise ValueError("Ainda há valores nulos em Calories após o preenchimento.")
    print("Valores nulos restantes em Calories: 0")

    print("\nEtapa 3 — Tratamento inicial de Date")
    datas_ausentes = dados["Date"].isna()
    print("Registros com data ausente")
    print(dados.loc[datas_ausentes].to_string(index=False))
    dados["Date"] = dados["Date"].astype("string").fillna(DATA_TEMPORARIA)
    print("Registros com a data temporária")
    print(dados.loc[datas_ausentes, ["ID", "Date"]].to_string(index=False))
    # As aspas simples fazem parte do texto das datas no CSV original.
    datas = dados["Date"].str.strip().str.strip("'")
    demonstrar_conversao(datas)

    print("\nEtapa 4 — Correção e conversão das datas")
    # Restaura o valor nulo apenas nas linhas preenchidas na etapa anterior.
    datas.loc[datas_ausentes] = pd.NA
    datas_compactas = datas == DATA_COMPACTA
    print(f"Registros com a data {DATA_COMPACTA}")
    print(dados.loc[datas_compactas, ["ID", "Date"]].to_string(index=False))
    datas = datas.replace(DATA_COMPACTA, "2020-12-26")
    datas = datas.str.replace("/", "-", regex=False)
    dados["Date"] = pd.to_datetime(datas, format="%Y-%m-%d", errors="coerce")
    print("Datas corrigidas")
    print(dados.loc[datas_compactas, ["ID", "Date"]].to_string(index=False))

    print("\nEtapa 5 — Remoção de registros com data inválida")
    print("Registros removidos")
    print(dados.loc[dados["Date"].isna()].to_string(index=False))
    dados = dados.dropna(subset=["Date"])
    print("Dados tratados")
    print(dados.to_string(index=False))
    return dados


def salvar_csv(dados: pd.DataFrame, destino: Path) -> None:
    """Exporta os dados tratados no padrão ISO de data e sem o índice."""
    dados.to_csv(destino, sep=";", index=False, encoding="utf-8", date_format="%Y-%m-%d")
