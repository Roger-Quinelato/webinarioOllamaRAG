import unittest
from types import SimpleNamespace

import chromadb

from ollama_embedding_provider import ErroProviderEmbeddingsOllama, ProviderEmbeddingsOllama
from session_index import IndiceSessao, criar_indice_sessao


DIMENSAO = 1024


def chunks_de_teste():
    """Descreve chunks de teste."""
    return [
        {
            "id": f"upload-{numero}",
            "texto": f"Trecho do upload {numero}.",
            "metadados": {
                "arquivo": "upload.pdf",
                "pagina": numero,
                "ano": 2025,
                "tema": "upload",
                "idioma": "pt",
                "chunk_id": f"upload-{numero}",
            },
        }
        for numero in range(1, 4)
    ]


def provider_de_teste(*, vetores=None, erro=None):
    """Descreve provider de teste."""
    def embed(**kwargs):
        """Descreve embed."""
        if erro:
            raise erro
        return SimpleNamespace(
            embeddings=vetores if vetores is not None else [[0.1] * DIMENSAO for _ in kwargs["input"]]
        )

    return ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))


class SessionIndexTest(unittest.TestCase):
    """Agrupa testes de Session Index Test. Herda de unittest.TestCase."""
    def test_cria_indice_sessao_com_perfil_bge_m3(self):
        """Verifica que cria indice sessao com perfil bge-m3."""
        indice = criar_indice_sessao(
            provider_de_teste(), "sessao-123", chunks_de_teste(), chromadb.EphemeralClient()
        )

        self.assertIsInstance(indice, IndiceSessao)
        self.assertEqual(indice.base_ativa.nome, "Índice de Sessão (sessao-123)")
        self.assertEqual(indice.base_ativa.tipo, "Índice de Sessão")
        self.assertEqual(indice.base_ativa.sessao_id, "sessao-123")
        self.assertEqual(indice.base_ativa.colecao.metadata["dimensao_embedding"], DIMENSAO)
        self.assertEqual(indice.base_ativa.colecao.count(), 3)

    def test_indices_sao_isolados_com_cliente_compartilhado(self):
        """Verifica que indices sao isolados com cliente compartilhado."""
        cliente = chromadb.EphemeralClient()
        primeiro = criar_indice_sessao(provider_de_teste(), "sessao-1", chunks_de_teste(), cliente)
        segundo = criar_indice_sessao(provider_de_teste(), "sessao-2", chunks_de_teste(), cliente)

        self.assertNotEqual(primeiro.nome_colecao, segundo.nome_colecao)
        primeiro.base_ativa.colecao.add(
            ids=["chunk-extra"], documents=["extra"], metadatas=[{"arquivo": "extra.pdf"}],
            embeddings=[[0.1] * DIMENSAO],
        )
        self.assertEqual(primeiro.base_ativa.colecao.count(), 4)
        self.assertEqual(segundo.base_ativa.colecao.count(), 3)

    def test_descartar_remove_colecao_e_eh_idempotente(self):
        """Verifica que descartar remove coleção e eh idempotente."""
        cliente = chromadb.EphemeralClient()
        indice = criar_indice_sessao(provider_de_teste(), "sessao-1", chunks_de_teste(), cliente)

        indice.descartar()
        indice.descartar()

        self.assertNotIn(indice.nome_colecao, {colecao.name for colecao in cliente.list_collections()})

    def test_descartar_preserva_corpus_oficial(self):
        """Verifica que descartar preserva Corpus Oficial."""
        cliente = chromadb.EphemeralClient()
        cliente.create_collection("artigos_rag_hibrido")
        indice = criar_indice_sessao(provider_de_teste(), "sessao-1", chunks_de_teste(), cliente)

        indice.descartar()

        self.assertIn("artigos_rag_hibrido", {colecao.name for colecao in cliente.list_collections()})

    def test_rejeita_embeddings_de_dimensao_incompativel_sem_criar_colecao(self):
        """Verifica que rejeita embeddings de dimensão incompativel sem criar coleção."""
        cliente = chromadb.EphemeralClient()
        colecoes_antes = {colecao.name for colecao in cliente.list_collections()}
        with self.assertRaisesRegex(ValueError, "1024"):
            criar_indice_sessao(
                provider_de_teste(vetores=[[0.1, 0.2, 0.3]] * 3), "sessao-1", chunks_de_teste(), cliente
            )
        self.assertEqual({colecao.name for colecao in cliente.list_collections()}, colecoes_antes)

    def test_rejeita_embeddings_vazios_quantidade_errada_e_ids_duplicados(self):
        """Verifica que rejeita embeddings vazios quantidade errada e ids duplicados."""
        cliente = chromadb.EphemeralClient()
        with self.assertRaisesRegex(ValueError, "quantidade"):
            criar_indice_sessao(provider_de_teste(vetores=[]), "sessao-1", chunks_de_teste(), cliente)
        with self.assertRaisesRegex(ValueError, "quantidade"):
            criar_indice_sessao(provider_de_teste(vetores=[[0.1] * DIMENSAO]), "sessao-1", chunks_de_teste(), cliente)
        chunks = chunks_de_teste()
        chunks[1]["id"] = chunks[0]["id"]
        with self.assertRaisesRegex(ValueError, "IDs únicos"):
            criar_indice_sessao(provider_de_teste(), "sessao-1", chunks, cliente)

    def test_propagacao_erro_ollama_nao_cria_colecao(self):
        """Verifica que propagação erro Ollama não cria coleção."""
        cliente = chromadb.EphemeralClient()
        colecoes_antes = {colecao.name for colecao in cliente.list_collections()}
        with self.assertRaises(ErroProviderEmbeddingsOllama):
            criar_indice_sessao(
                provider_de_teste(erro=ConnectionError()), "sessao-1", chunks_de_teste(), cliente
            )
        self.assertEqual({colecao.name for colecao in cliente.list_collections()}, colecoes_antes)


if __name__ == "__main__":
    unittest.main()
