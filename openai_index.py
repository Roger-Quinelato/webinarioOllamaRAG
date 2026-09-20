"""Reindexação do Corpus Oficial em uma coleção Chroma com embeddings OpenAI."""

import json
import os
import tempfile
import time
from pathlib import Path

import chromadb

import config
from openai_provider import MODELO_EMBEDDING


COLECAO_OPENAI = "artigos_rag_openai"
MANIFESTO_OPENAI = "openai_manifest.json"
VERSAO_COLECAO = "openai-embeddings-v1"
_METADADOS_COLECAO = {
    "modelo_embedding": MODELO_EMBEDDING,
    "versao_colecao": VERSAO_COLECAO,
    "corpus": "Corpus Oficial",
    "provedor_embedding": "OpenAI",
    "hnsw:space": "cosine",
    "status": "ready",
}
_METADADOS_CHUNK_OBRIGATORIOS = ("arquivo", "pagina", "ano", "idioma", "tema", "chunk_id")


class ColecaoOpenAIIncompativel(RuntimeError):
    """A coleção persistente não corresponde ao índice OpenAI esperado."""


def _validar_metadados_colecao(colecao):
    metadados = colecao.metadata or {}
    incompatibilidades = [
        campo
        for campo, esperado in _METADADOS_COLECAO.items()
        if campo in {"modelo_embedding", "versao_colecao", "corpus"}
        and metadados.get(campo) != esperado
    ]
    if incompatibilidades:
        raise ColecaoOpenAIIncompativel(
            "Coleção OpenAI incompatível ("
            + ", ".join(incompatibilidades)
            + "). Execute a reindexação do Corpus Oficial antes de consultar."
        )


def abrir_colecao_openai(chroma_client=None):
    """Abre apenas a coleção publicada no manifesto; nunca cria coleção vazia."""
    chroma_client = chroma_client or chromadb.PersistentClient(path=str(config.PASTA_CHROMA))
    manifesto = Path(config.PASTA_CHROMA) / MANIFESTO_OPENAI
    if not manifesto.exists():
        raise ColecaoOpenAIIncompativel("Corpus Oficial OpenAI não publicado; execute a reindexação.")
    try:
        nome = json.loads(manifesto.read_text(encoding="utf-8"))["colecao"]
        colecao = chroma_client.get_collection(nome)
    except (OSError, ValueError, KeyError, TypeError, Exception) as erro:
        if isinstance(erro, ColecaoOpenAIIncompativel):
            raise
        raise ColecaoOpenAIIncompativel("Manifesto ou coleção OpenAI inválidos; execute a reindexação.") from None
    _validar_metadados_colecao(colecao)
    if (colecao.metadata or {}).get("status") != "ready":
        raise ColecaoOpenAIIncompativel("Coleção OpenAI ainda não está pronta para consulta.")
    return colecao


def _validar_corpus(chunks):
    arquivos = {chunk["metadados"].get("arquivo") for chunk in chunks}
    esperados = set(config.ARTIGOS_CORPUS)
    if arquivos != esperados:
        faltantes = sorted(esperados - arquivos)
        extras = sorted(arquivos - esperados)
        raise ValueError(f"Corpus Oficial inválido; faltantes={faltantes}, extras={extras}")
    for chunk in chunks:
        faltantes = [campo for campo in _METADADOS_CHUNK_OBRIGATORIOS if campo not in chunk["metadados"]]
        if faltantes:
            raise ValueError(f"Chunk {chunk.get('id', '<sem id>')} sem metadados: {faltantes}")


def reindexar_corpus_oficial(
    provider, *, chunks=None, chroma_client=None, progresso=print, recriar=False
):
    """Indexa o corpus com OpenAI sem remover a coleção Chroma legada."""
    if chunks is None:
        from corpus import gerar_chunks

        chunks = gerar_chunks()
    chunks = list(chunks)
    _validar_corpus(chunks)
    chroma_client = chroma_client or chromadb.PersistentClient(path=str(config.PASTA_CHROMA))
    nomes_existentes = {colecao.name for colecao in chroma_client.list_collections()}
    nome_candidato = COLECAO_OPENAI if COLECAO_OPENAI not in nomes_existentes else f"{COLECAO_OPENAI}_{int(time.time() * 1000000)}"
    colecao = chroma_client.create_collection(name=nome_candidato, embedding_function=None,
                                              metadata={**_METADADOS_COLECAO, "status": "building"})
    inicio = time.perf_counter()
    lote = 64
    for posicao in range(0, len(chunks), lote):
        parte = chunks[posicao:posicao + lote]
        vetores = provider.gerar_embeddings([chunk["texto"] for chunk in parte])
        if len(vetores) != len(parte):
            raise ValueError("O Provider OpenAI devolveu quantidade de embeddings diferente da entrada.")
        colecao.add(
            ids=[chunk["id"] for chunk in parte],
            documents=[chunk["texto"] for chunk in parte],
            metadatas=[chunk["metadados"] for chunk in parte],
            embeddings=vetores,
        )
        if progresso:
            progresso(f"  {min(posicao + lote, len(chunks))}/{len(chunks)} chunks indexados")
    esperado = {chunk["id"] for chunk in chunks}
    if colecao.count() != len(esperado) or set(colecao.get(include=[])["ids"]) != esperado:
        raise ValueError("A coleção candidata não contém exatamente os chunks esperados.")
    colecao.modify(metadata={k: v for k, v in _METADADOS_COLECAO.items() if k != "hnsw:space"})
    manifesto = Path(config.PASTA_CHROMA) / MANIFESTO_OPENAI
    manifesto.parent.mkdir(parents=True, exist_ok=True)
    fd, temporario = tempfile.mkstemp(prefix="openai_manifest.", dir=manifesto.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
            json.dump({"colecao": nome_candidato, "status": "ready"}, arquivo)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, manifesto)
    finally:
        if os.path.exists(temporario):
            os.unlink(temporario)
    arquivos = {chunk["metadados"]["arquivo"] for chunk in chunks}
    resultado = {
        "artigos": len(arquivos),
        "chunks": colecao.count(),
        "modelo_embedding": MODELO_EMBEDDING,
        "colecao": nome_candidato,
        "duracao_segundos": time.perf_counter() - inicio,
    }
    return resultado
