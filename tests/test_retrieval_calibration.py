import unittest

from retrieval_calibration import avaliar_limiar


class RetrievalCalibrationTest(unittest.TestCase):
    def test_limiar_so_e_aprovado_quando_separa_positivas_e_negativas(self):
        resultado = avaliar_limiar([0.21, 0.42], [0.67, 0.81], limiar=0.60)

        self.assertEqual(resultado["maior_distancia_positiva"], 0.42)
        self.assertEqual(resultado["menor_distancia_negativa"], 0.67)
        self.assertEqual(resultado["intervalo_seguro"], [0.42, 0.67])

        with self.assertRaisesRegex(ValueError, "não separa"):
            avaliar_limiar([0.21, 0.61], [0.67, 0.81], limiar=0.60)


if __name__ == "__main__":
    unittest.main()
