import unittest
import tempfile
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

import chromadb

import config
from openai_index import (
    COLECAO_OPENAI,
    MODELO_EMBEDDING,
    VERSAO_COLECAO,
    ColecaoOpenAIIncompativel,
    abrir_colecao_openai,
    reindexar_corpus_oficial,
)


def chunks_de_teste():
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


def chunks_de_teste_quantidade(quantidade):
    base = chunks_de_teste()
    return [
        {
            **base[indice % len(base)],
            "id": f"artigo-{indice % len(base) + 1}-p001-c{indice:03d}",
            "texto": f"Trecho {indice} " + ("x" * 40),
            "metadados": {
                **base[indice % len(base)]["metadados"],
                "chunk_id": f"artigo-{indice % len(base) + 1}-p001-c{indice:03d}",
            },
        }
        for indice in range(quantidade)
    ]


class ProviderFake:
    def __init__(self):
        self.textos = []

    def gerar_embeddings(self, textos):
        self.textos.extend(textos)
        return [[float(indice), 1.0] for indice, _ in enumerate(textos, start=1)]


class ErroLimiteFake(RuntimeError):
    status_code = 429

    def __init__(self, retry_after=None):
        super().__init__("limite de teste")
        self.retry_after = retry_after


class ProviderComLimiteFake(ProviderFake):
    def __init__(self, erros):
        super().__init__()
        self.erros = list(erros)
        self.chamadas = []

    def gerar_embeddings(self, textos):
        self.chamadas.append(list(textos))
        if self.erros:
            raise self.erros.pop(0)
        return super().gerar_embeddings(textos)


class OpenAIIndexTest(unittest.TestCase):
    def tearDown(self):
        cliente = chromadb.EphemeralClient()
        for colecao in cliente.list_collections():
            if colecao.name.startswith(COLECAO_OPENAI):
                cliente.delete_collection(colecao.name)

    def test_indexa_em_lotes_de_no_maximo_32_chunks(self):
        cliente = chromadb.EphemeralClient()
        provider = ProviderComLimiteFake([])

        reindexar_corpus_oficial(
            provider,
            chunks=chunks_de_teste_quantidade(33),
            chroma_client=cliente,
            progresso=None,
        )

        self.assertEqual([len(chamada) for chamada in provider.chamadas], [32, 1])

    def test_429_repete_somente_lote_com_retry_after(self):
        cliente = chromadb.EphemeralClient()
        provider = ProviderComLimiteFake([ErroLimiteFake(retry_after=7)])
        esperas = []

        reindexar_corpus_oficial(
            provider,
            chunks=chunks_de_teste_quantidade(33),
            chroma_client=cliente,
            progresso=None,
            esperar=esperas.append,
            aleatorio=lambda _inicio, _fim: 0,
        )

        self.assertEqual([len(chamada) for chamada in provider.chamadas], [32, 32, 1])
        self.assertEqual(esperas, [7])

    def test_429_sem_retry_after_usa_backoff_exponencial_com_jitter(self):
        cliente = chromadb.EphemeralClient()
        provider = ProviderComLimiteFake([ErroLimiteFake(), ErroLimiteFake()])
        esperas = []

        reindexar_corpus_oficial(
            provider,
            chunks=chunks_de_teste(),
            chroma_client=cliente,
            progresso=None,
            esperar=esperas.append,
            aleatorio=lambda _inicio, _fim: 0.25,
        )

        self.assertEqual(esperas, [1.25, 2.25])
        self.assertEqual([len(chamada) for chamada in provider.chamadas], [8, 8, 8])

    def test_limita_estimativa_antes_de_ultrapassar_40_mil_tpm(self):
        cliente = chromadb.EphemeralClient()
        provider = ProviderComLimiteFake([])
        esperas = []
        chunks = chunks_de_teste_quantidade(10)
        for chunk in chunks:
            chunk["texto"] = "x" * 16_000

        reindexar_corpus_oficial(
            provider,
            chunks=chunks,
            chroma_client=cliente,
            progresso=None,
            esperar=esperas.append,
            agora=lambda: 0,
        )

        self.assertEqual([len(chamada) for chamada in provider.chamadas], [5, 5])
        self.assertEqual(esperas, [60])

    def test_falha_de_limite_preserva_manifesto_publicado(self):
        cliente = chromadb.EphemeralClient()
        chunks = chunks_de_teste()
        with tempfile.TemporaryDirectory() as pasta_temporaria, patch.object(config, "PASTA_CHROMA", Path(pasta_temporaria)):
            anterior = reindexar_corpus_oficial(
                ProviderFake(), chunks=chunks, chroma_client=cliente, progresso=None
            )
            manifesto = Path(config.PASTA_CHROMA) / "openai_manifest.json"
            antes = manifesto.read_text(encoding="utf-8")

            with self.assertRaises(ErroLimiteFake):
                reindexar_corpus_oficial(
                    ProviderComLimiteFake([ErroLimiteFake()]),
                    chunks=chunks,
                    chroma_client=cliente,
                    progresso=None,
                    max_tentativas_429=0,
                )

            self.assertEqual(manifesto.read_text(encoding="utf-8"), antes)
            self.assertEqual(abrir_colecao_openai(cliente).name, anterior["colecao"])

    def test_recusa_colecao_incompativel_com_orientacao_de_reindexacao(self):
        cliente = chromadb.EphemeralClient()
        cliente.create_collection(
            COLECAO_OPENAI,
            metadata={"modelo_embedding": "modelo-antigo", "versao_colecao": VERSAO_COLECAO},
        )

        with self.assertRaisesRegex(ColecaoOpenAIIncompativel, "reindexação"):
            abrir_colecao_openai(cliente)
        cliente.delete_collection(COLECAO_OPENAI)

    def test_reindexa_oito_artigos_preserva_legado_e_registra_metadados(self):
        cliente = chromadb.EphemeralClient()
        legado = cliente.create_collection("artigos_rag")
        legado.add(ids=["legado-1"], documents=["vetor legado"], embeddings=[[1.0, 0.0]])
        provider = ProviderFake()

        resultado = reindexar_corpus_oficial(
            provider,
            chunks=chunks_de_teste(),
            chroma_client=cliente,
        )

        nova = cliente.get_collection(COLECAO_OPENAI)
        self.assertEqual(resultado["artigos"], 8)
        self.assertEqual(resultado["chunks"], 8)
        self.assertEqual(resultado["modelo_embedding"], MODELO_EMBEDDING)
        self.assertGreaterEqual(resultado["duracao_segundos"], 0)
        self.assertEqual(nova.count(), 8)
        self.assertEqual(legado.count(), 1)
        self.assertEqual(nova.metadata["modelo_embedding"], MODELO_EMBEDDING)
        self.assertEqual(nova.metadata["versao_colecao"], VERSAO_COLECAO)
        self.assertEqual(nova.metadata["corpus"], "Corpus Oficial")
        metadados = nova.get(ids=["artigo-1-p001-c00"], include=["metadatas"])["metadatas"][0]
        for campo in ("arquivo", "pagina", "ano", "idioma", "tema", "chunk_id"):
            self.assertIn(campo, metadados)
        self.assertEqual(len(provider.textos), 8)

    def test_reindexacao_e_idempotente(self):
        cliente = chromadb.EphemeralClient()
        provider = ProviderFake()
        chunks = chunks_de_teste()

        reindexar_corpus_oficial(provider, chunks=chunks, chroma_client=cliente)
        reindexar_corpus_oficial(provider, chunks=chunks, chroma_client=cliente)

        self.assertEqual(cliente.get_collection(COLECAO_OPENAI).count(), 8)


if __name__ == "__main__":
    unittest.main()
