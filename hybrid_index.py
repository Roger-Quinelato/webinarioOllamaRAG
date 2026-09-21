"""Índice híbrido do Corpus Oficial com embeddings locais via Ollama."""

import json
import os
import tempfile
import time
from hashlib import sha256
from pathlib import Path

import chromadb
from chromadb.errors import NotFoundError

import config
from ollama_embedding_provider import ProviderEmbeddingsOllama


PROVEDOR_EMBEDDING = "Ollama"
COLECAO_HIBRIDA = "artigos_rag_hibrido"
MANIFESTO_HIBRIDO = "hybrid_manifest.json"
MODELO_EMBEDDING = config.MODELO_EMBEDDING
VERSAO_COLECAO = config.VERSAO_COLECAO_EMBEDDING
DIMENSAO_EMBEDDING = config.DIMENSAO_EMBEDDING
LOTE_EMBEDDING = 32
_METADADOS_CHUNK_OBRIGATORIOS = ("arquivo", "pagina", "ano", "idioma", "tema", "chunk_id")


class ColecaoHibridaIncompativel(RuntimeError):
    """A coleção publicada não corresponde ao índice híbrido esperado. Herda de RuntimeError."""


def abrir_colecao_hibrida(chroma_client=None):
    """Abre somente a coleção híbrida pronta publicada no manifesto."""
    chroma_client = chroma_client or chromadb.PersistentClient(path=str(config.PASTA_CHROMA))
    manifesto = Path(config.PASTA_CHROMA) / MANIFESTO_HIBRIDO
    try:
        publicado = json.loads(manifesto.read_text(encoding="utf-8"))
        colecao = chroma_client.get_collection(publicado["colecao"])
    except (OSError, ValueError, KeyError, TypeError, NotFoundError):
        raise ColecaoHibridaIncompativel(
            "Corpus Oficial híbrido não publicado; execute a reindexação."
        ) from None
    metadados = colecao.metadata or {}
    esperados = {
        "provedor_embedding": PROVEDOR_EMBEDDING,
        "modelo_embedding": MODELO_EMBEDDING,
        "versao_colecao": VERSAO_COLECAO,
        "corpus": "Corpus Oficial",
        "status": "ready",
    }
    incompatibilidades = [
        campo
        for campo, esperado in esperados.items()
        if metadados.get(campo) != esperado or publicado.get(campo) != esperado
    ]
    dimensao = metadados.get("dimensao_embedding")
    if (
        dimensao != DIMENSAO_EMBEDDING
        or publicado.get("dimensao_embedding") != DIMENSAO_EMBEDDING
    ):
        incompatibilidades.append("dimensao_embedding")
    if incompatibilidades:
        raise ColecaoHibridaIncompativel(
            "Coleção híbrida incompatível ("
            + ", ".join(dict.fromkeys(incompatibilidades))
            + "). Execute a reindexação do Corpus Oficial antes de consultar."
        )
    return colecao


def _validar_corpus(chunks):
    """Valida corpus."""
    arquivos = {chunk["metadados"].get("arquivo") for chunk in chunks}
    esperados = set(config.ARTIGOS_CORPUS)
    if arquivos != esperados:
        raise ValueError(
            f"Corpus Oficial inválido; faltantes={sorted(esperados - arquivos)}, "
            f"extras={sorted(arquivos - esperados)}"
        )
    ids = [chunk.get("id") for chunk in chunks]
    if len(ids) != len(set(ids)):
        raise ValueError("O Corpus Oficial precisa ter IDs únicos para todos os chunks.")
    for chunk in chunks:
        faltantes = [campo for campo in _METADADOS_CHUNK_OBRIGATORIOS if campo not in chunk["metadados"]]
        if faltantes:
            raise ValueError(f"Chunk {chunk.get('id', '<sem id>')} sem metadados: {faltantes}")


def _publicar_manifesto(dados):
    """Auxilia publicar manifesto."""
    manifesto = Path(config.PASTA_CHROMA) / MANIFESTO_HIBRIDO
    manifesto.parent.mkdir(parents=True, exist_ok=True)
    fd, temporario = tempfile.mkstemp(prefix="hybrid_manifest.", dir=manifesto.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, manifesto)
    finally:
        if os.path.exists(temporario):
            os.unlink(temporario)


def _nome_candidato(chunks):
    """Auxilia nome candidato."""
    identidade = json.dumps(
        {
            "provedor_embedding": PROVEDOR_EMBEDDING,
            "modelo_embedding": MODELO_EMBEDDING,
            "versao_colecao": VERSAO_COLECAO,
            "chunks": sorted(chunks, key=lambda chunk: chunk["id"]),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"{COLECAO_HIBRIDA}_{sha256(identidade.encode('utf-8')).hexdigest()[:12]}"


def _resultado(colecao, chunks, *, embeddings_gerados, inicio):
    """Auxilia resultado."""
    return {
        "artigos": len({chunk["metadados"]["arquivo"] for chunk in chunks}),
        "chunks": colecao.count(),
        "embeddings_gerados": embeddings_gerados,
        "modelo_embedding": MODELO_EMBEDDING,
        "dimensao_embedding": colecao.metadata["dimensao_embedding"],
        "colecao": colecao.name,
        "duracao_segundos": time.perf_counter() - inicio,
    }


def reindexar_corpus_oficial(provider, *, chunks=None, chroma_client=None, progresso=print):
    """Publica uma nova coleção híbrida sem remover coleções existentes."""
    if not isinstance(provider, ProviderEmbeddingsOllama):
        raise TypeError("A reindexação híbrida exige ProviderEmbeddingsOllama.")
    if chunks is None:
        from corpus import gerar_chunks

        chunks = gerar_chunks()
    chunks = list(chunks)
    _validar_corpus(chunks)
    inicio = time.perf_counter()
    chroma_client = chroma_client or chromadb.PersistentClient(path=str(config.PASTA_CHROMA))
    nome = _nome_candidato(chunks)
    nomes = {colecao.name for colecao in chroma_client.list_collections()}
    if nome in nomes:
        existente = chroma_client.get_collection(nome)
        ids_esperados = {chunk["id"] for chunk in chunks}
        metadados = existente.metadata or {}
        compativel = (
            metadados.get("provedor_embedding") == PROVEDOR_EMBEDDING
            and metadados.get("modelo_embedding") == MODELO_EMBEDDING
            and metadados.get("versao_colecao") == VERSAO_COLECAO
            and metadados.get("corpus") == "Corpus Oficial"
            and metadados.get("status") == "ready"
            and metadados.get("dimensao_embedding") == DIMENSAO_EMBEDDING
            and existente.count() == len(ids_esperados)
            and set(existente.get(include=[])["ids"]) == ids_esperados
        )
        if compativel:
            _publicar_manifesto({"colecao": nome, **metadados})
            return _resultado(existente, chunks, embeddings_gerados=0, inicio=inicio)
        if metadados.get("status") == "building":
            chroma_client.delete_collection(nome)
        else:
            raise ValueError("A coleção candidata existente é incompatível; use outra versão de esquema.")
    vetores = []
    for indice in range(0, len(chunks), LOTE_EMBEDDING):
        parte = chunks[indice : indice + LOTE_EMBEDDING]
        vetores.extend(provider.gerar_embeddings([chunk["texto"] for chunk in parte]))
        if progresso:
            progresso(f"  {len(vetores)}/{len(chunks)} chunks indexados")
    if len(vetores) != len(chunks):
        raise ValueError("O Provider Ollama devolveu quantidade de embeddings diferente da entrada.")
    dimensoes = {len(vetor) for vetor in vetores}
    if dimensoes != {DIMENSAO_EMBEDDING}:
        raise ValueError(
            f"O Provider Ollama devolveu embeddings incompatíveis; "
            f"{MODELO_EMBEDDING} exige dimensão {DIMENSAO_EMBEDDING}."
        )
    dimensao = DIMENSAO_EMBEDDING
    metadados = {
        "provedor_embedding": PROVEDOR_EMBEDDING,
        "modelo_embedding": MODELO_EMBEDDING,
        "dimensao_embedding": dimensao,
        "versao_colecao": VERSAO_COLECAO,
        "corpus": "Corpus Oficial",
        "status": "building",
    }
    colecao = chroma_client.create_collection(
        name=nome,
        embedding_function=None,
        metadata={**metadados, "hnsw:space": "cosine"},
    )
    colecao.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["texto"] for chunk in chunks],
        metadatas=[chunk["metadados"] for chunk in chunks],
        embeddings=vetores,
    )
    ids_esperados = {chunk["id"] for chunk in chunks}
    if colecao.count() != len(ids_esperados) or set(colecao.get(include=[])["ids"]) != ids_esperados:
        raise ValueError("A coleção candidata não contém exatamente os chunks esperados.")
    metadados["status"] = "ready"
    colecao.modify(metadata=metadados)
    _publicar_manifesto({"colecao": nome, **metadados})
    return _resultado(colecao, chunks, embeddings_gerados=len(vetores), inicio=inicio)
