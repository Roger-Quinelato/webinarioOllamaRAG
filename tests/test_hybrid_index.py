import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import chromadb

import config
from hybrid_index import (
    COLECAO_HIBRIDA,
    MANIFESTO_HIBRIDO,
    MODELO_EMBEDDING,
    PROVEDOR_EMBEDDING,
    VERSAO_COLECAO,
    ColecaoHibridaIncompativel,
    abrir_colecao_hibrida,
    reindexar_corpus_oficial,
)
from ollama_embedding_provider import ProviderEmbeddingsOllama


def chunks_de_teste():
    """Descreve chunks de teste."""
    return [
        {
            "id": f"artigo-{numero}-p001-c00",
            "texto": f"Trecho do artigo {numero}.",
            "metadados": {
                "arquivo": list(config.ARTIGOS_CORPUS)[numero - 1],
                "titulo": f"Artigo {numero}",
                "autores": "Autoria de teste",
                "ano": 2025,
                "veiculo": "Veículo de teste",
                "tema": "retrieval",
                "idioma": "pt",
                "resumo": f"Resumo do artigo {numero}.",
                "pagina": 1,
                "chunk_id": f"artigo-{numero}-p001-c00",
                "tipo_chunk": "pagina",
            },
        }
        for numero in range(1, 9)
    ]


class HybridIndexTest(unittest.TestCase):
    """Agrupa testes de Hybrid Index Test. Herda de unittest.TestCase."""
    def tearDown(self):
        """Descreve tear Down."""
        cliente = chromadb.EphemeralClient()
        for colecao in cliente.list_collections():
            if colecao.name.startswith(COLECAO_HIBRIDA):
                cliente.delete_collection(colecao.name)

    def test_publica_metadados_hibridos_com_dimensao_bge_m3(self):
        """Verifica que publica metadados hibridos com dimensão bge-m3."""
        cliente = chromadb.EphemeralClient()
        chamadas = []

        def embed(**kwargs):
            """Descreve embed."""
            chamadas.append(kwargs)
            return SimpleNamespace(embeddings=[[0.1] * 1024 for _ in kwargs["input"]])

        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))
        with tempfile.TemporaryDirectory() as pasta, patch.object(config, "PASTA_CHROMA", Path(pasta)):
            resultado = reindexar_corpus_oficial(
                provider,
                chunks=chunks_de_teste(),
                chroma_client=cliente,
                progresso=None,
            )
            manifesto = json.loads((Path(pasta) / MANIFESTO_HIBRIDO).read_text(encoding="utf-8"))

        colecao = cliente.get_collection(resultado["colecao"])
        esperados = {
            "provedor_embedding": PROVEDOR_EMBEDDING,
            "modelo_embedding": MODELO_EMBEDDING,
            "dimensao_embedding": 1024,
            "versao_colecao": VERSAO_COLECAO,
            "corpus": "Corpus Oficial",
            "status": "ready",
        }
        self.assertEqual({campo: colecao.metadata[campo] for campo in esperados}, esperados)
        self.assertEqual({campo: manifesto[campo] for campo in esperados}, esperados)
        self.assertEqual(chamadas[0]["model"], "bge-m3")

    def test_recusa_manifesto_incompativel_com_orientacao_de_reindexacao(self):
        """Verifica que Recusa manifesto incompativel com orientação de reindexação."""
        cliente = chromadb.EphemeralClient()
        cliente.create_collection(
            COLECAO_HIBRIDA,
            metadata={
                "provedor_embedding": "OpenAI",
                "modelo_embedding": MODELO_EMBEDDING,
            "dimensao_embedding": 1024,
                "versao_colecao": VERSAO_COLECAO,
                "corpus": "Corpus Oficial",
                "status": "ready",
            },
        )
        with tempfile.TemporaryDirectory() as pasta, patch.object(config, "PASTA_CHROMA", Path(pasta)):
            (Path(pasta) / MANIFESTO_HIBRIDO).write_text(
                json.dumps({"colecao": COLECAO_HIBRIDA, **cliente.get_collection(COLECAO_HIBRIDA).metadata}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ColecaoHibridaIncompativel, "reindexação"):
                abrir_colecao_hibrida(cliente)

    def test_recusa_corpus_oficial_com_dimensao_diferente_de_1024(self):
        """Verifica que Recusa Corpus Oficial com dimensão diferente de 1024."""
        cliente = chromadb.EphemeralClient()
        metadados = {
            "provedor_embedding": "Ollama",
            "modelo_embedding": MODELO_EMBEDDING,
            "dimensao_embedding": 3,
            "versao_colecao": VERSAO_COLECAO,
            "corpus": "Corpus Oficial",
            "status": "ready",
        }
        cliente.create_collection(COLECAO_HIBRIDA, metadata=metadados)
        with tempfile.TemporaryDirectory() as pasta, patch.object(config, "PASTA_CHROMA", Path(pasta)):
            (Path(pasta) / MANIFESTO_HIBRIDO).write_text(
                json.dumps({"colecao": COLECAO_HIBRIDA, **metadados}), encoding="utf-8"
            )
            with self.assertRaisesRegex(ColecaoHibridaIncompativel, "dimensao_embedding"):
                abrir_colecao_hibrida(cliente)

    def test_recusa_manifesto_que_aponta_para_colecao_ausente(self):
        """Verifica que Recusa manifesto que aponta para coleção ausente."""
        cliente = chromadb.EphemeralClient()
        with tempfile.TemporaryDirectory() as pasta, patch.object(config, "PASTA_CHROMA", Path(pasta)):
            (Path(pasta) / MANIFESTO_HIBRIDO).write_text(
                json.dumps({"colecao": "candidata-ausente"}), encoding="utf-8"
            )

            with self.assertRaisesRegex(ColecaoHibridaIncompativel, "reindexação"):
                abrir_colecao_hibrida(cliente)

    def test_recusa_ids_duplicados_antes_de_gerar_embeddings(self):
        """Verifica que Recusa ids duplicados antes de gerar embeddings."""
        chamadas = []

        def embed(**kwargs):
            """Descreve embed."""
            chamadas.append(kwargs)
            return SimpleNamespace(embeddings=[])

        chunks = chunks_de_teste()
        chunks[1]["id"] = chunks[0]["id"]
        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))

        with self.assertRaisesRegex(ValueError, "IDs únicos"):
            reindexar_corpus_oficial(
                provider,
                chunks=chunks,
                chroma_client=chromadb.EphemeralClient(),
                progresso=None,
            )

        self.assertEqual(chamadas, [])

    def test_reindexacao_repetida_e_idempotente_e_preserva_colecoes_existentes(self):
        """Verifica que reindexação repetida e idempotente e preserva colecoes existentes."""
        cliente = chromadb.EphemeralClient()
        cliente.create_collection("artigos_rag")
        cliente.create_collection("artigos_rag_openai")
        chamadas = []

        def embed(**kwargs):
            """Descreve embed."""
            chamadas.append(kwargs)
            return SimpleNamespace(embeddings=[[0.1] * 1024 for _ in kwargs["input"]])

        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))
        with tempfile.TemporaryDirectory() as pasta, patch.object(config, "PASTA_CHROMA", Path(pasta)):
            primeiro = reindexar_corpus_oficial(
                provider, chunks=chunks_de_teste(), chroma_client=cliente, progresso=None
            )
            segundo = reindexar_corpus_oficial(
                provider,
                chunks=list(reversed(chunks_de_teste())),
                chroma_client=cliente,
                progresso=None,
            )

        nomes = {colecao.name for colecao in cliente.list_collections()}
        self.assertEqual(primeiro["colecao"], segundo["colecao"])
        self.assertEqual(primeiro["embeddings_gerados"], 8)
        self.assertEqual(segundo["embeddings_gerados"], 0)
        self.assertEqual(len(chamadas), 1)
        self.assertIn("artigos_rag", nomes)
        self.assertIn("artigos_rag_openai", nomes)
        self.assertEqual(len([nome for nome in nomes if nome.startswith(COLECAO_HIBRIDA)]), 1)

    def test_falha_na_candidata_preserva_publicacao_anterior(self):
        """Verifica que falha na candidata preserva publicação anterior."""
        cliente = chromadb.EphemeralClient()

        def embed(**kwargs):
            """Descreve embed."""
            return SimpleNamespace(embeddings=[[0.1] * 1024 for _ in kwargs["input"]])

        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))
        with tempfile.TemporaryDirectory() as pasta, patch.object(config, "PASTA_CHROMA", Path(pasta)):
            anterior = reindexar_corpus_oficial(
                provider, chunks=chunks_de_teste(), chroma_client=cliente, progresso=None
            )
            conteudo_anterior = (Path(pasta) / MANIFESTO_HIBRIDO).read_text(encoding="utf-8")
            alterados = chunks_de_teste()
            alterados[0]["texto"] += " versão nova"

            def falhar(**_kwargs):
                """Falha valor do fluxo."""
                raise ConnectionError("Ollama indisponível")

            provider_com_falha = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=falhar))
            with self.assertRaises(RuntimeError):
                reindexar_corpus_oficial(
                    provider_com_falha,
                    chunks=alterados,
                    chroma_client=cliente,
                    progresso=None,
                )

            self.assertEqual(
                (Path(pasta) / MANIFESTO_HIBRIDO).read_text(encoding="utf-8"), conteudo_anterior
            )
            self.assertEqual(abrir_colecao_hibrida(cliente).name, anterior["colecao"])


if __name__ == "__main__":
    unittest.main()
