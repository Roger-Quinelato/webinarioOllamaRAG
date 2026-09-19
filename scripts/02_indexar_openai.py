"""Reindexa explicitamente o Corpus Oficial em Chroma com embeddings OpenAI."""

import argparse
import json
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import rag  # noqa: E402
from openai_index import reindexar_corpus_oficial  # noqa: E402
from openai_provider import ProviderOpenAI  # noqa: E402


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--recriar",
    action="store_true",
    help="recria somente a coleção OpenAI se seus metadados forem incompatíveis",
)
args = parser.parse_args()

with rag.cli_seguro():
    chunks = rag.gerar_chunks()
    resultado = reindexar_corpus_oficial(
        ProviderOpenAI(),
        chunks=chunks,
        recriar=args.recriar,
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
