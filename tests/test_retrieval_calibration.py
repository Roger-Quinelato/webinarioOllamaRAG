import unittest

import config
from retrieval_calibration import (
    ARQUIVOS_ESPERADOS,
    PERGUNTAS_NEGATIVAS,
    PERGUNTAS_POSITIVAS,
    avaliar_limiar,
    calcular_limiar_com_margem,
    medir_retrieval,
)


class _ProviderFalso:
    def gerar_embeddings(self, textos):
        return [[0.0, 0.0] for _ in textos]


class _ColecaoFalsa:
    """Devolve, para cada pergunta, o arquivo esperado, exceto os trocados em `troca`."""

    metadata = {"dimensao_embedding": 2}

    def __init__(self, troca=None):
        self.troca = troca or {}

    def query(self, **_):
        arquivos = [self.troca.get(p, ARQUIVOS_ESPERADOS.get(p) or "gao2023_survey.pdf") for p in PERGUNTAS_POSITIVAS]
        arquivos += ["outro.pdf"] * len(PERGUNTAS_NEGATIVAS)
        distancias = [0.3] * len(PERGUNTAS_POSITIVAS) + [0.7] * len(PERGUNTAS_NEGATIVAS)
        return {"distances": [[d] for d in distancias], "metadatas": [[{"arquivo": a}] for a in arquivos]}


class RetrievalCalibrationTest(unittest.TestCase):
    """Agrupa testes de Retrieval Calibration Test. Herda de unittest.TestCase."""
    def test_politica_escolhe_ponto_medio_com_margens_iguais(self):
        """Verifica que politica escolhe ponto medio com margens iguais."""
        resultado = calcular_limiar_com_margem([0.21, 0.44], [0.58, 0.81])

        self.assertAlmostEqual(resultado["limiar_calculado"], 0.51)
        self.assertAlmostEqual(resultado["margem_positivas"], 0.07)
        self.assertAlmostEqual(resultado["margem_negativas"], 0.07)

    def test_limiar_ativo_e_o_ponto_medio_da_calibracao_real(self):
        """Verifica que limiar ativo e o ponto medio da calibração real."""
        resultado = calcular_limiar_com_margem(
            [0.44007039070129395],
            [0.5800204873085022],
        )

        self.assertEqual(config.DISTANCIA_MAXIMA_RETRIEVAL, resultado["limiar_calculado"])

    def test_limiar_so_e_aprovado_quando_separa_positivas_e_negativas(self):
        """Verifica que limiar so e aprovado quando separa positivas e negativas."""
        resultado = avaliar_limiar([0.21, 0.42], [0.67, 0.81], limiar=0.60)

        self.assertEqual(resultado["maior_distancia_positiva"], 0.42)
        self.assertEqual(resultado["menor_distancia_negativa"], 0.67)
        self.assertEqual(resultado["intervalo_seguro"], [0.42, 0.67])

        with self.assertRaisesRegex(ValueError, "não separa"):
            avaliar_limiar([0.21, 0.61], [0.67, 0.81], limiar=0.60)

    def test_calibracao_aprova_quando_chunk_mais_proximo_vem_do_documento_esperado(self):
        """Verifica que calibração aprova quando chunk mais próximo vem do documento esperado."""
        resultado = medir_retrieval(_ColecaoFalsa(), _ProviderFalso(), limiar=0.5)

        self.assertEqual(resultado["positivas"][0]["arquivo"], "lewis2020_rag.pdf")

    def test_calibracao_reprova_quando_chunk_mais_proximo_vem_de_outro_documento(self):
        """Verifica que calibração reprova quando chunk mais próximo vem de outro documento."""
        colecao = _ColecaoFalsa({PERGUNTAS_POSITIVAS[0]: "gao2023_survey.pdf"})

        with self.assertRaisesRegex(ValueError, "lewis2020_rag.pdf.*gao2023_survey.pdf"):
            medir_retrieval(colecao, _ProviderFalso(), limiar=0.5)


if __name__ == "__main__":
    unittest.main()
