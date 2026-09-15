import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import rag  # noqa: E402

parser = argparse.ArgumentParser(
    description="Shapley exato dos chunks do top-k sobre a resposta (2^k gerações do LLM). Não roda ao vivo."
)
parser.add_argument("--pergunta", default="Quais são os tokens de reflexão (reflection tokens) propostos no Self-RAG?")
parser.add_argument("--k", type=int, default=config.K_PADRAO)
parser.add_argument("--modelo", default=config.MODELO_CHAT)
args = parser.parse_args()

with rag.cli_seguro():
    inicio = time.perf_counter()
    resultados = rag.buscar(args.pergunta, k=args.k)
    print(f"Pergunta: {args.pergunta}\nTop-{args.k}:\n{rag.tabela_resultados(resultados)}\n")
    saida = rag.shapley_chunks(args.pergunta, resultados, modelo=args.modelo)
    saida["segundos"] = time.perf_counter() - inicio

    print(f"\nv(nenhum chunk) = {saida['valor_sem_chunks']:.4f}   v(todos) = {saida['valor_com_todos']:.4f}")
    for item in saida["contribuicoes"]:
        print(f"   chunk {item['chunk']} ({item['arquivo']} p.{item['pagina']}): shapley = {item['shapley']:+.4f}")
    soma = sum(item["shapley"] for item in saida["contribuicoes"])
    print(f"Soma dos Shapley = {soma:+.4f} (deve ser v(todos) - v(nenhum) = "
          f"{saida['valor_com_todos'] - saida['valor_sem_chunks']:+.4f})")
    print(f"Tempo total: {saida['segundos']:.0f}s")

    config.PASTA_RESULTADOS.mkdir(exist_ok=True)
    arquivo = config.PASTA_RESULTADOS / "shapley_chunks.json"
    arquivo.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Salvo em {arquivo.relative_to(config.RAIZ)}")
