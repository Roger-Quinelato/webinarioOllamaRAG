"""Reindexação do Corpus Oficial em uma coleção Chroma com embeddings OpenAI."""

import time
from pathlib import Path

import chromadb

import config
from openai_provider import MODELO_EMBEDDING


COLECAO_OPENAI = "artigos_rag_openai"
VERSAO_COLECAO = "openai-embeddings-v1"
_METADADOS_COLECAO = {
    "modelo_embedding": MODELO_EMBEDDING,
    "versao_colecao": VERSAO_COLECAO,
    "corpus": "Corpus Oficial",
    "provedor_embedding": "OpenAI",
    "hnsw:space": "cosine",
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
    """Abre ou cria a coleção nova e valida seu contrato antes do uso."""
    chroma_client = chroma_client or chromadb.PersistentClient(path=str(config.PASTA_CHROMA))
    nomes = {colecao.name for colecao in chroma_client.list_collections()}
    if COLECAO_OPENAI in nomes:
        colecao = chroma_client.get_collection(COLECAO_OPENAI)
        _validar_metadados_colecao(colecao)
        return colecao
    return chroma_client.create_collection(
        name=COLECAO_OPENAI,
        embedding_function=None,
        metadata=dict(_METADADOS_COLECAO),
    )


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
        from rag import gerar_chunks

        chunks = gerar_chunks()
    chunks = list(chunks)
    _validar_corpus(chunks)
    try:
        colecao = abrir_colecao_openai(chroma_client)
    except ColecaoOpenAIIncompativel:
        if not recriar:
            raise
        chroma_client = chroma_client or chromadb.PersistentClient(path=str(config.PASTA_CHROMA))
        chroma_client.delete_collection(COLECAO_OPENAI)
        colecao = abrir_colecao_openai(chroma_client)
    inicio = time.perf_counter()
    lote = 64
    for posicao in range(0, len(chunks), lote):
        parte = chunks[posicao:posicao + lote]
        vetores = provider.gerar_embeddings([chunk["texto"] for chunk in parte])
        if len(vetores) != len(parte):
            raise ValueError("O Provider OpenAI devolveu quantidade de embeddings diferente da entrada.")
        colecao.upsert(
            ids=[chunk["id"] for chunk in parte],
            documents=[chunk["texto"] for chunk in parte],
            metadatas=[chunk["metadados"] for chunk in parte],
            embeddings=vetores,
        )
        if progresso:
            progresso(f"  {min(posicao + lote, len(chunks))}/{len(chunks)} chunks indexados")
    arquivos = {chunk["metadados"]["arquivo"] for chunk in chunks}
    resultado = {
        "artigos": len(arquivos),
        "chunks": colecao.count(),
        "modelo_embedding": MODELO_EMBEDDING,
        "colecao": COLECAO_OPENAI,
        "duracao_segundos": time.perf_counter() - inicio,
    }
    return resultado
