import unittest

import config
from retrieval_calibration import avaliar_limiar, calcular_limiar_com_margem


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


if __name__ == "__main__":
    unittest.main()
