"""Valida o limiar ativo contra perguntas positivas e negativas versionadas."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from hybrid_index import abrir_colecao_hibrida  # noqa: E402
from ollama_embedding_provider import ProviderEmbeddingsOllama  # noqa: E402
from retrieval_calibration import medir_retrieval  # noqa: E402


try:
    resultado = medir_retrieval(
        abrir_colecao_hibrida(),
        ProviderEmbeddingsOllama(),
        limiar=config.DISTANCIA_MAXIMA_RETRIEVAL,
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
except Exception as erro:
    print(f"ERRO: {erro}")
    raise SystemExit(2)
