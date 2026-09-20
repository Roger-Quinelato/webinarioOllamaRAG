import unittest
from unittest.mock import patch, MagicMock

import streamlit as st
from streamlit.testing.v1 import AppTest

class AppTestIntegracao(unittest.TestCase):
    """Agrupa testes de App Test Integração. Herda de unittest.TestCase."""
    def setUp(self):
        """Descreve set Up."""
        st.cache_resource.clear()

    @patch("generation_providers.criar_generation_router")
    def test_app_sem_provider_mostra_aviso(self, mock_criar_router):
        """Verifica que app sem provider mostra aviso."""
        from generation_providers import NenhumProviderGeracaoConfigurado
        mock_criar_router.side_effect = NenhumProviderGeracaoConfigurado("Configure OPENAI_API_KEY, NVIDIA_API_KEY ou GEMINI_API_KEY")
        at = AppTest.from_file("../app.py").run(timeout=30)
        self.assertFalse(at.exception)
        warnings = [w.value for w in at.warning]
        self.assertTrue(any("NVIDIA_API_KEY" in w for w in warnings))

    @patch("generation_providers.criar_generation_router", return_value=MagicMock())
    @patch("hybrid_index.abrir_colecao_hibrida")
    def test_app_com_provider_inicia_corretamente(self, mock_abrir_colecao, _mock_criar_router):
        """Verifica que app com provider inicia corretamente."""
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
        self.assertEqual(len(at.file_uploader), 0)
        self.assertTrue(any("após a apresentação" in info.value for info in at.info))

    @patch("generation_providers.criar_generation_router", return_value=MagicMock())
    @patch("hybrid_index.abrir_colecao_hibrida")
    def test_upload_pdfs_permanece_desativado_no_treino(self, mock_abrir_colecao, _mock_criar_router):
        """Verifica que upload pdfs permanece desativado no treino."""
        mock_abrir_colecao.return_value = MagicMock(metadata={
            "provedor_embedding": "Ollama", "modelo_embedding": "bge-m3",
            "dimensao_embedding": 1024, "versao_colecao": "bge-m3-v1", "status": "ready",
        })
        at = AppTest.from_file("../app.py").run(timeout=30)

        self.assertFalse(at.exception)
        self.assertEqual(len(at.file_uploader), 0)
        self.assertTrue(any("após a apresentação" in info.value for info in at.info))

    @patch("generation_providers.criar_generation_router", return_value=MagicMock())
    @patch("hybrid_index.abrir_colecao_hibrida")
    def test_inicio_cria_router_de_providers(self, mock_abrir_colecao, mock_criar_router):
        """Verifica que inicio cria router de providers."""
        mock_abrir_colecao.return_value = MagicMock(metadata={
            "provedor_embedding": "Ollama", "modelo_embedding": "bge-m3",
            "dimensao_embedding": 1024, "versao_colecao": "bge-m3-v1", "status": "ready",
        })
        at = AppTest.from_file("../app.py").run(timeout=30)

        self.assertFalse(at.exception)
        mock_criar_router.assert_called_once()

if __name__ == "__main__":
    unittest.main()
