"""Índice de Sessão temporário para uploads efêmeros."""

import chromadb

from hybrid_index import MODELO_EMBEDDING, PROVEDOR_EMBEDDING, VERSAO_COLECAO
from openai_rag import BaseAtiva


def criar_indice_sessao(provider, sessao_id: str, chunks: list, chroma_client=None) -> BaseAtiva:
    """Cria uma coleção efêmera para os chunks de upload e retorna a BaseAtiva."""
    chroma_client = chroma_client or chromadb.EphemeralClient()
    
    nome_colecao = f"sessao_{sessao_id}".replace("-", "_")
    
    nomes = {col.name for col in chroma_client.list_collections()}
    if nome_colecao in nomes:
        chroma_client.delete_collection(nome_colecao)

    if not chunks:
        raise ValueError("O Índice de Sessão não pode ser vazio.")

    textos = [chunk["texto"] for chunk in chunks]
    vetores = provider.gerar_embeddings(textos)
    
    dimensoes = {len(vetor) for vetor in vetores}
    if len(dimensoes) != 1 or next(iter(dimensoes)) <= 0:
        raise ValueError("Embeddings com dimensão inválida.")
    dimensao = next(iter(dimensoes))
    
    metadados = {
        "provedor_embedding": PROVEDOR_EMBEDDING,
        "modelo_embedding": MODELO_EMBEDDING,
        "dimensao_embedding": dimensao,
        "versao_colecao": VERSAO_COLECAO,
        "corpus": "Índice de Sessão",
        "status": "ready",
    }
    
    colecao = chroma_client.create_collection(
        name=nome_colecao,
        embedding_function=None,
        metadata={**metadados, "hnsw:space": "cosine"},
    )
    
    colecao.add(
        ids=[chunk.get("id") or chunk.get("metadados", {}).get("chunk_id") for chunk in chunks],
        documents=textos,
        metadatas=[chunk["metadados"] for chunk in chunks],
        embeddings=vetores,
    )
        
    return BaseAtiva(
        nome=f"Índice de Sessão ({sessao_id})",
        colecao=colecao,
        tipo="Índice de Sessão",
        provedor_embedding=PROVEDOR_EMBEDDING,
        modelo_embedding=MODELO_EMBEDDING,
        dimensao_embedding=dimensao,
        versao_colecao=VERSAO_COLECAO,
        sessao_id=sessao_id,
    )
