import unittest
from unittest.mock import patch, MagicMock

from streamlit.testing.v1 import AppTest

class AppTestIntegracao(unittest.TestCase):
    @patch("openai_provider.obter_chave_openai")
    def test_app_sem_chave_openai_mostra_aviso(self, mock_obter_chave):
        from openai_provider import ChaveOpenAIAusente
        mock_obter_chave.side_effect = ChaveOpenAIAusente("Configure OPENAI_API_KEY")
        at = AppTest.from_file("../app.py").run(timeout=30)
        self.assertFalse(at.exception)
        warnings = [w.value for w in at.warning]
        self.assertTrue(any("OPENAI_API_KEY" in w for w in warnings))

    @patch("openai_provider.obter_chave_openai", return_value="fake-key")
    @patch("hybrid_index.abrir_colecao_hibrida")
    def test_app_com_chave_inicia_corretamente(self, mock_abrir_colecao, mock_obter_chave):
        mock_colecao = MagicMock()
        mock_colecao.metadata = {
            "provedor_embedding": "Ollama",
            "modelo_embedding": "bge-m3",
            "dimensao_embedding": 1024,
            "versao_colecao": "bge-m3-v1",
            "status": "ready",
            "corpus": "Corpus Oficial"
        }
        mock_abrir_colecao.return_value = mock_colecao

        at = AppTest.from_file("../app.py").run(timeout=30)
        self.assertFalse(at.exception)
        
        # Check title
        self.assertEqual(at.title[0].value, "📚 Assistente RAG sobre artigos de RAG")
        self.assertEqual(at.radio[0].label, "Base Ativa")
        self.assertEqual(at.radio[0].value, "Corpus Oficial")
        self.assertEqual(at.file_uploader[0].label, "Até 3 PDFs")

    @patch("openai_provider.obter_chave_openai", return_value="fake-key")
    @patch("hybrid_index.abrir_colecao_hibrida")
    def test_indice_de_sessao_exige_upload_explicito(self, mock_abrir_colecao, mock_obter_chave):
        mock_abrir_colecao.return_value = MagicMock(metadata={
            "provedor_embedding": "Ollama", "modelo_embedding": "bge-m3",
            "dimensao_embedding": 1024, "versao_colecao": "bge-m3-v1", "status": "ready",
        })
        at = AppTest.from_file("../app.py").run(timeout=30)

        at.radio[0].set_value("Índice de Sessão").run(timeout=30)

        self.assertFalse(at.exception)
        self.assertTrue(any("Crie um Índice de Sessão" in erro.value for erro in at.error))

if __name__ == "__main__":
    unittest.main()
