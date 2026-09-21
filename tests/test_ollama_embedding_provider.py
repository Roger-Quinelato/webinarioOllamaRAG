import unittest
from types import SimpleNamespace

from ollama_embedding_provider import (
    ErroProviderEmbeddingsOllama,
    ProviderEmbeddingsOllama,
)


class ProviderEmbeddingsOllamaTest(unittest.TestCase):
    """Agrupa testes de Provider Embeddings Ollama Test. Herda de unittest.TestCase."""
    def test_embeddings_usam_bge_m3_na_fronteira_ollama(self):
        """Verifica que embeddings usam bge-m3 na fronteira Ollama."""
        chamadas = []

        def embed(**kwargs):
            """Descreve embed."""
            chamadas.append(kwargs)
            return SimpleNamespace(embeddings=[[0.1, 0.2]])

        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))

        self.assertEqual(provider.gerar_embeddings(["Chunk Recuperado"]), [[0.1, 0.2]])
        self.assertEqual(chamadas, [{"model": "bge-m3", "input": ["Chunk Recuperado"]}])

    def test_ollama_indisponivel_tem_mensagem_acionavel(self):
        """Verifica que Ollama indisponivel tem mensagem acionavel."""
        def embed(**_kwargs):
            """Descreve embed."""
            raise ConnectionError("detalhe interno")

        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))

        with self.assertRaisesRegex(ErroProviderEmbeddingsOllama, "Inicie o Ollama") as contexto:
            provider.gerar_embeddings(["Chunk Recuperado"])
        self.assertNotIn("detalhe interno", str(contexto.exception))

    def test_bge_m3_ausente_orienta_instalacao(self):
        """Verifica que bge-m3 ausente orienta instalação."""
        class ModeloAusente(Exception):
            """Representa erro Modelo Ausente. Herda de Exception."""
            status_code = 404

        def embed(**_kwargs):
            """Descreve embed."""
            raise ModeloAusente("detalhe interno")

        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))

        with self.assertRaisesRegex(ErroProviderEmbeddingsOllama, "ollama pull bge-m3"):
            provider.gerar_embeddings(["Chunk Recuperado"])


if __name__ == "__main__":
    unittest.main()
