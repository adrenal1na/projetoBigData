import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
from pandas.testing import assert_frame_equal

import main as aplicacao
from src.microatividades import ler_csv, selecionar_colunas
from src.tratamento_dados import tratar_dados


class TesteTratamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = ler_csv(aplicacao.CSV_ORIGINAL)
        cls.copia_original = cls.original.copy(deep=True)
        with redirect_stdout(io.StringIO()):
            cls.tratado = tratar_dados(cls.original)

    def test_carrega_registros_originais(self):
        self.assertEqual(len(self.original), 32)
        self.assertEqual(self.original["ID"].tolist(), list(range(32)))
        self.assertEqual(self.original.loc[7, "Duration"], 450)
        self.assertEqual(self.original.loc[26, "Date"], "20201226")
        self.assertTrue(pd.isna(self.original.loc[22, "Date"]))

    def test_colunas_obrigatorias(self):
        self.assertEqual(
            self.original.columns.tolist(),
            ["ID", "Duration", "Date", "Pulse", "Maxpulse", "Calories"],
        )

    def test_copia_preserva_original(self):
        assert_frame_equal(self.original, self.copia_original)

    def test_calorias_ausentes_sao_preenchidas(self):
        self.assertFalse(self.tratado["Calories"].isna().any())
        calorias = self.tratado.set_index("ID")["Calories"]
        self.assertEqual(calorias.loc[[18, 28]].tolist(), [0, 0])

    def test_date_tem_tipo_datetime(self):
        self.assertTrue(is_datetime64_any_dtype(self.tratado["Date"]))
        self.assertFalse(self.tratado["Date"].isna().any())

    def test_remove_somente_o_registro_sem_data(self):
        self.assertEqual(len(self.tratado), 31)
        ids_esperados = self.original.loc[self.original["Date"].notna(), "ID"]
        self.assertEqual(self.tratado["ID"].tolist(), ids_esperados.tolist())

    def test_corrige_data_compacta(self):
        datas = self.tratado.set_index("ID")["Date"]
        self.assertEqual(datas.loc[26], pd.Timestamp("2020-12-26"))

    def test_subconjunto_independente(self):
        subconjunto = selecionar_colunas(self.original)
        self.assertEqual(subconjunto.columns.tolist(), ["ID", "Date", "Calories"])
        subconjunto.loc[0, "Calories"] = 0
        self.assertEqual(self.original.loc[0, "Calories"], 4091)

    def test_executa_programa_e_exporta_csv(self):
        original_antes = aplicacao.CSV_ORIGINAL.read_bytes()
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as pasta:
            destino = Path(pasta) / "tratado.csv"
            saida = io.StringIO()
            with redirect_stdout(saida):
                aplicacao.main(aplicacao.CSV_ORIGINAL, destino)

            with destino.open(encoding="utf-8", newline="") as arquivo:
                leitor = csv.DictReader(arquivo, delimiter=";")
                self.assertEqual(leitor.fieldnames, self.original.columns.tolist())
                registros_exportados = list(leitor)

        with aplicacao.CSV_ORIGINAL.open(encoding="utf-8", newline="") as arquivo:
            registros_esperados = []
            for registro in csv.DictReader(arquivo, delimiter=";"):
                if registro["Date"] == "NaN":
                    continue
                if registro["Calories"] == "NaN":
                    registro["Calories"] = "0"
                if registro["Date"] == "20201226":
                    registro["Date"] = "2020-12-26"
                else:
                    registro["Date"] = registro["Date"].strip("'").replace("/", "-")
                registros_esperados.append(registro)

        self.assertEqual(registros_exportados, registros_esperados)
        self.assertEqual(aplicacao.CSV_ORIGINAL.read_bytes(), original_antes)
        relatorio = saida.getvalue()
        for numero in range(1, 6):
            self.assertIn(f"Microatividade {numero}", relatorio)
            self.assertIn(f"Etapa {numero}", relatorio)

    def test_csv_sem_registros_preserva_saida(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as pasta:
            entrada = Path(pasta) / "entrada.csv"
            saida = Path(pasta) / "tratado.csv"
            entrada.write_text("ID;Duration;Date;Pulse;Maxpulse;Calories\n", encoding="utf-8")
            saida.write_text("resultado anterior", encoding="utf-8")

            with self.assertRaisesRegex(SystemExit, "sem registros"):
                aplicacao.main(entrada, saida)

            self.assertEqual(saida.read_text(encoding="utf-8"), "resultado anterior")

    def test_csv_com_campo_extra_e_rejeitado(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as pasta:
            entrada = Path(pasta) / "entrada.csv"
            entrada.write_text(
                "ID;Duration;Date;Pulse;Maxpulse;Calories\n"
                "0;60;'2020/12/01';110;130;4091;extra\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "mais campos"):
                ler_csv(entrada)

    def test_csv_original_nao_pode_ser_usado_como_saida(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as pasta:
            entrada = Path(pasta) / "entrada.csv"
            conteudo_original = aplicacao.CSV_ORIGINAL.read_bytes()
            entrada.write_bytes(conteudo_original)

            with self.assertRaisesRegex(SystemExit, "arquivos diferentes"):
                aplicacao.main(entrada, entrada)

            self.assertEqual(entrada.read_bytes(), conteudo_original)


if __name__ == "__main__":
    unittest.main()
