"""Índice de Sessão temporário para uploads efêmeros."""

from dataclasses import dataclass
from uuid import uuid4

import chromadb
from chromadb.errors import NotFoundError

from hybrid_index import (
    DIMENSAO_EMBEDDING,
    MODELO_EMBEDDING,
    PROVEDOR_EMBEDDING,
    VERSAO_COLECAO,
)
from ollama_embedding_provider import ProviderEmbeddingsOllama
from openai_rag import BaseAtiva


@dataclass
class IndiceSessao:
    """Coleção efêmera e sua Base Ativa exclusiva de upload."""

    base_ativa: BaseAtiva
    cliente: object
    nome_colecao: str

    def descartar(self):
        """Remove somente esta coleção. Repetir a limpeza é seguro."""
        try:
            self.cliente.delete_collection(self.nome_colecao)
        except NotFoundError:
            pass


def criar_indice_sessao(provider, sessao_id: str, chunks: list, chroma_client=None) -> IndiceSessao:
    """Gera, valida e publica coleção efêmera exclusiva de um upload."""
    if not isinstance(provider, ProviderEmbeddingsOllama):
        raise TypeError("O Índice de Sessão exige ProviderEmbeddingsOllama com bge-m3.")
    chunks = list(chunks)
    if not chunks:
        raise ValueError("O Índice de Sessão não pode ser vazio.")

    ids = [chunk.get("id") or chunk.get("metadados", {}).get("chunk_id") for chunk in chunks]
    if any(not chunk_id for chunk_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("O Índice de Sessão precisa ter IDs únicos para todos os chunks.")

    textos = [chunk["texto"] for chunk in chunks]
    vetores = provider.gerar_embeddings(textos)
    if len(vetores) != len(chunks):
        raise ValueError("O Provider Ollama devolveu quantidade de embeddings diferente da entrada.")
    dimensoes = {len(vetor) for vetor in vetores}
    if dimensoes != {DIMENSAO_EMBEDDING}:
        raise ValueError(
            f"O Provider Ollama precisa devolver embeddings bge-m3 de dimensão {DIMENSAO_EMBEDDING}."
        )

    chroma_client = chroma_client or chromadb.EphemeralClient()
    nome_colecao = f"sessao_{sessao_id.replace('-', '_')}_{uuid4().hex}"
    metadados = {
        "provedor_embedding": PROVEDOR_EMBEDDING,
        "modelo_embedding": MODELO_EMBEDDING,
        "dimensao_embedding": DIMENSAO_EMBEDDING,
        "versao_colecao": VERSAO_COLECAO,
        "corpus": "Índice de Sessão",
        "status": "ready",
    }
    colecao = chroma_client.create_collection(
        name=nome_colecao,
        embedding_function=None,
        metadata={**metadados, "hnsw:space": "cosine"},
    )
    try:
        colecao.add(
            ids=ids,
            documents=textos,
            metadatas=[chunk["metadados"] for chunk in chunks],
            embeddings=vetores,
        )
    except Exception:
        chroma_client.delete_collection(nome_colecao)
        raise

    base_ativa = BaseAtiva(
        nome=f"Índice de Sessão ({sessao_id})",
        colecao=colecao,
        tipo="Índice de Sessão",
        provedor_embedding=PROVEDOR_EMBEDDING,
        modelo_embedding=MODELO_EMBEDDING,
        dimensao_embedding=DIMENSAO_EMBEDDING,
        versao_colecao=VERSAO_COLECAO,
        sessao_id=sessao_id,
    )
    return IndiceSessao(base_ativa, chroma_client, nome_colecao)
