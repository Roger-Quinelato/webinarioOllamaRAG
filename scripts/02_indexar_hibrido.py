"""Reindexa o Corpus Oficial com bge-m3 via Ollama em uma coleção híbrida."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from corpus import gerar_chunks  # noqa: E402
from hybrid_index import reindexar_corpus_oficial  # noqa: E402
from ollama_embedding_provider import ProviderEmbeddingsOllama  # noqa: E402


try:
    resultado = reindexar_corpus_oficial(
        ProviderEmbeddingsOllama(),
        chunks=gerar_chunks(),
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
except Exception as erro:
    print(f"ERRO: {erro}")
    raise SystemExit(2)
