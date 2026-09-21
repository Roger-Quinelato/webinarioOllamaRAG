import unittest
from unittest.mock import patch, MagicMock

import streamlit as st
from chromadb.errors import ChromaError
from streamlit.testing.v1 import AppTest

import config
from generation_router import ErroProviderGeracao
from openai_rag import MAX_CHUNKS_RETRIEVAL

_METADADOS_OK = {
    "provedor_embedding": "Ollama", "modelo_embedding": "bge-m3",
    "dimensao_embedding": 1024, "versao_colecao": "bge-m3-v1", "status": "ready",
}


class _ColecaoFalsa:
    """Coleção Chroma mínima que registra a última consulta recebida."""

    def __init__(self, metadata=None, erro=None):
        self.name = "corpus_falso"
        self.metadata = dict(_METADADOS_OK if metadata is None else metadata)
        self.erro = erro
        self.consultas = []

    def query(self, **opcoes):
        self.consultas.append(opcoes)
        if self.erro:
            raise self.erro
        return {
            "documents": [["trecho um", "trecho dois"]],
            "metadatas": [[{"arquivo": "a.pdf", "pagina": 1, "ano": 2024, "tema": "retrieval"},
                           {"arquivo": "b.pdf", "pagina": 2, "ano": 2023, "tema": "avaliacao"}]],
            "distances": [[0.1, 0.2]],
        }


class _EmbeddingsFalso:
    def gerar_embeddings(self, textos):
        return [[0.0] * 1024 for _ in textos]


class _GeracaoFalsa:
    """Provider de geração simulado: emite pedaços e, opcionalmente, falha."""

    def __init__(self, pedacos=(), erro=None):
        self.pedacos, self.erro = pedacos, erro

    def transmitir(self, mensagens):
        yield from self.pedacos
        if self.erro:
            raise self.erro

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

    @patch("generation_providers.criar_generation_router")
    def test_app_com_ordem_invalida_mostra_aviso(self, mock_criar_router):
        """Verifica que GENERATION_PROVIDERS_ORDER inválida vira aviso, sem traceback."""
        from generation_providers import OrdemProvidersInvalida
        mock_criar_router.side_effect = OrdemProvidersInvalida("GENERATION_PROVIDERS_ORDER inválida")
        at = AppTest.from_file("../app.py").run(timeout=30)
        self.assertFalse(at.exception)
        self.assertTrue(any("GENERATION_PROVIDERS_ORDER" in w.value for w in at.warning))

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
        self.assertEqual(at.title[0].value, "Assistente RAG sobre artigos de RAG")
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

class AppTestFluxoPergunta(unittest.TestCase):
    """Exercita pergunta, streaming, fontes, erros e limpeza com fronteiras simuladas."""

    def setUp(self):
        st.cache_resource.clear()

    def _abrir(self, geracao, colecao=None):
        colecao = colecao or _ColecaoFalsa()
        patches = [
            patch("generation_providers.criar_generation_router", return_value=geracao),
            patch("ollama_embedding_provider.ProviderEmbeddingsOllama", return_value=_EmbeddingsFalso()),
            patch("hybrid_index.abrir_colecao_hibrida", return_value=colecao),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        at = AppTest.from_file("../app.py").run(timeout=30)
        self.assertFalse(at.exception)
        return at, colecao

    def _perguntar(self, at, texto="Como funciona o RAG?"):
        at.chat_input[0].set_value(texto).run(timeout=30)
        self.assertFalse(at.exception)
        return at

    def test_slider_de_k_vai_ate_o_teto_real(self):
        at, _ = self._abrir(_GeracaoFalsa())
        slider = next(s for s in at.sidebar.slider if s.label.startswith("Trechos"))
        self.assertEqual(slider.max, MAX_CHUNKS_RETRIEVAL)
        self.assertLessEqual(slider.value, MAX_CHUNKS_RETRIEVAL)

    def test_streaming_com_citacao_mostra_fontes_citadas(self):
        at, _ = self._abrir(_GeracaoFalsa(["O RAG ", "recupera trechos [1]."]))
        self._perguntar(at)
        mensagens = at.session_state["mensagens"]
        self.assertEqual(mensagens[-1]["texto"], "O RAG recupera trechos [1].")
        self.assertEqual(mensagens[-1]["busca"]["classe_fontes"], "citadas")
        self.assertEqual([e.label for e in at.expander], ["Fontes Citadas (1) · a.pdf"])
        self.assertTrue(any("a.pdf" in m.value for m in at.expander[0].markdown))

    def test_resposta_sem_citacao_mostra_chunks_recuperados_como_fallback(self):
        at, _ = self._abrir(_GeracaoFalsa(["Resposta sem marcador."]))
        self._perguntar(at)
        self.assertEqual(at.session_state["mensagens"][-1]["busca"]["classe_fontes"], "fallback")
        self.assertEqual([e.label for e in at.expander], ["Chunks Recuperados (2)"])

    def test_recusa_nao_mostra_fontes(self):
        at, _ = self._abrir(_GeracaoFalsa([config.RESPOSTA_NAO_ENCONTRADA]))
        self._perguntar(at)
        self.assertEqual(at.session_state["mensagens"][-1]["busca"]["status"], "completa")
        self.assertEqual(at.session_state["mensagens"][-1]["busca"]["classe_fontes"], "recusa")
        self.assertEqual(len(at.expander), 0)
        self.assertTrue(any("Classe: recusa" in c.value for c in at.caption))

    def test_resposta_parcial_e_identificada(self):
        at, _ = self._abrir(_GeracaoFalsa(["Início [1]"], erro=RuntimeError("queda")))
        self._perguntar(at)
        busca = at.session_state["mensagens"][-1]["busca"]
        self.assertEqual(busca["status"], "Resposta Parcial")
        self.assertIn("Início [1]", busca["texto"])
        self.assertTrue(any("interrompida" in w.value for w in at.warning))

    def test_erro_de_provider_remove_a_pergunta(self):
        at, _ = self._abrir(_GeracaoFalsa(erro=ErroProviderGeracao("Provider indisponível.")))
        self._perguntar(at)
        self.assertTrue(any("Provider indisponível." in e.value for e in at.error))
        self.assertEqual(at.session_state["mensagens"], [])

    def test_limpar_conversa_esvazia_o_historico(self):
        at, _ = self._abrir(_GeracaoFalsa(["Ok [1]"]))
        self._perguntar(at)
        self.assertEqual(len(at.session_state["mensagens"]), 2)
        next(b for b in at.sidebar.button if b.label == "Limpar conversa").click().run(timeout=30)
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["mensagens"], [])

    def test_filtro_de_tema_chega_ao_chroma(self):
        at, colecao = self._abrir(_GeracaoFalsa(["Ok [1]"]))
        at.sidebar.multiselect[0].set_value(["avaliacao"]).run(timeout=30)
        self._perguntar(at)
        self.assertIn({"tema": {"$in": ["avaliacao"]}}, colecao.consultas[-1]["where"]["$and"])

    def test_valor_de_k_respeita_o_slider(self):
        at, colecao = self._abrir(_GeracaoFalsa(["Ok [1]"]))
        next(s for s in at.sidebar.slider if s.label.startswith("Trechos")).set_value(2).run(timeout=30)
        self._perguntar(at)
        self.assertEqual(colecao.consultas[-1]["n_results"], 2)

    def test_base_incompativel_exibe_orientacao_de_reindexacao(self):
        colecao = _ColecaoFalsa()
        at, colecao = self._abrir(_GeracaoFalsa(["Ok"]), colecao)
        colecao.metadata["versao_colecao"] = "outra"
        self._perguntar(at)
        self.assertTrue(any("reindexação explícita" in e.value for e in at.error))
        self.assertFalse(any("Confira a configuração e tente novamente" in e.value for e in at.error))
        self.assertEqual(at.session_state["mensagens"], [])

    def test_erro_do_chroma_mantem_mensagem_generica(self):
        at, colecao = self._abrir(_GeracaoFalsa(["Ok"]))
        colecao.erro = ChromaError("falha interna")
        self._perguntar(at)
        self.assertTrue(any("Não foi possível consultar a Base Ativa" in e.value for e in at.error))
        self.assertFalse(any("falha interna" in e.value for e in at.error))
        self.assertEqual(at.session_state["mensagens"], [])


if __name__ == "__main__":
    unittest.main()
