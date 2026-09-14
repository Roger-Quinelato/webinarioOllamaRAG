import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import rag  # noqa: E402

parser = argparse.ArgumentParser(description="Resposta RAG completa, em streaming, com citação das fontes.")
parser.add_argument("pergunta", nargs="?", default="Como o Self-RAG decide quando buscar documentos?")
parser.add_argument("--modelo", default=config.MODELO_CHAT)
parser.add_argument("--dois-estagios", action="store_true")
args = parser.parse_args()

try:
    if args.dois_estagios:
        busca = rag.buscar_dois_estagios(args.pergunta)
        print(f"Caminho: {busca['caminho']}")
        resultados = busca["resultados"]
    else:
        resultados = rag.buscar(args.pergunta)
    print(f"Modelo: {args.modelo}\nPergunta: {args.pergunta}\n")
    inicio = time.perf_counter()
    primeiro_token = None
    for pedaco in rag.responder(args.pergunta, resultados, modelo=args.modelo):
        if primeiro_token is None:
            primeiro_token = time.perf_counter() - inicio
        print(pedaco, end="", flush=True)
    print(f"\n\n[primeiro token em {primeiro_token:.1f}s, resposta completa em {time.perf_counter() - inicio:.1f}s]")
except rag.OllamaIndisponivel as erro:
    print(f"\nERRO: {erro}")
    sys.exit(2)
