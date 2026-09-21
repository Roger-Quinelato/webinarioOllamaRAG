import tempfile
import unittest
from pathlib import Path

import config
import corpus
import rag


class SalvarMetadadosTest(unittest.TestCase):
    """Agrupa testes da escrita de metadados.csv. Herda de unittest.TestCase."""

    def test_salvar_metadados_grava_csv_que_carregar_metadados_le_de_volta(self):
        """Verifica que salvar metadados grava csv que carregar metadados le de volta."""
        linha = {coluna: "x" for coluna in config.COLUNAS_METADADOS}
        linha.update(ano="2020", resumo="Resumo novo")
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "metadados.csv"
            corpus.salvar_metadados([linha], caminho)
            lidas = corpus.carregar_metadados(caminho)

        self.assertEqual(lidas[0]["resumo"], "Resumo novo")
        self.assertEqual(lidas[0]["ano"], 2020)

    def test_rag_continua_expondo_salvar_metadados(self):
        """Verifica que rag continua expondo salvar metadados."""
        self.assertIs(rag.salvar_metadados, corpus.salvar_metadados)


if __name__ == "__main__":
    unittest.main()
