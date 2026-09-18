import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import rag  # noqa: E402

parser = argparse.ArgumentParser(description="Chunking + embeddings + ChromaDB, e demo de metadados extraídos pelo LLM.")
parser.add_argument("--artigo-demo", default="es2023_ragas.pdf", help="artigo usado na demo de extração por LLM")
parser.add_argument("--sem-demo", action="store_true", help="pula a demo de extração de metadados pelo LLM")
args = parser.parse_args()

with rag.cli_seguro():
    print(f"Modelo de embedding: {config.MODELO_EMBEDDING}")
    print(f"Chunk: {config.TAMANHO_CHUNK} caracteres, sobreposição {config.SOBREPOSICAO}")

    inicio = time.perf_counter()
    chunks = rag.gerar_chunks()
    print(f"\n1) Chunking: {len(chunks)} chunks em {time.perf_counter() - inicio:.1f}s")
    print("   por tipo:", dict(Counter(c["metadados"]["tipo_chunk"] for c in chunks)))
    print("   por artigo:", dict(Counter(c["metadados"]["arquivo"] for c in chunks)))

    pagina_longa = [c for c in chunks if c["id"].startswith("lewis2020_rag-p003")]
    print(f"\n   Página 3 de lewis2020_rag.pdf virou {len(pagina_longa)} chunks:")
    for anterior, atual in zip(pagina_longa, pagina_longa[1:]):
        repetido = anterior["texto"][anterior["texto"].find(atual["texto"][:40]):]
        print(f"   - {anterior['id']} ({len(anterior['texto'])} car.) → {atual['id']} ({len(atual['texto'])} car.)")
        print(f"     trecho repetido nos dois ({len(repetido)} car.): {repetido[:90]}…")

    print("\n2) Embeddings + ChromaDB")
    inicio = time.perf_counter()
    colecao = rag.indexar(chunks)
    duracao = time.perf_counter() - inicio
    print(f"   {colecao.count()} vetores na coleção '{config.NOME_COLECAO}' em {duracao:.1f}s")

    amostra = colecao.get(ids=[chunks[0]["id"]], include=["metadatas", "embeddings"])
    print(f"   dimensão do vetor: {len(amostra['embeddings'][0])}")
    print(f"   metadados de {chunks[0]['id']}: {json.dumps(amostra['metadatas'][0], ensure_ascii=False)[:400]}…")

    if not args.sem_demo:
        print(f"\n3) Demo: metadados extraídos pelo LLM ({config.MODELO_CHAT}) × metadados.csv — {args.artigo_demo}")
        manual = next(m for m in rag.carregar_metadados() if m["arquivo"] == args.artigo_demo)
        primeira_pagina = rag.extrair_paginas(config.PASTA_ARTIGOS / args.artigo_demo, limpar=False)[0]
        inicio = time.perf_counter()
        extraido = rag.extrair_metadados_llm(primeira_pagina)
        print(f"   extração em {time.perf_counter() - inicio:.1f}s")
        comparacao = rag.comparar_metadados(manual, extraido)
        for linha in comparacao:
            print(f"   {'=' if linha['igual'] else '≠'} {linha['campo']:<8} csv: {str(linha['csv'])[:60]!r}")
            print(f"     {'':<8} llm: {str(linha['llm'])[:60]!r}")
        config.PASTA_RESULTADOS.mkdir(exist_ok=True)
        saida = config.PASTA_RESULTADOS / "metadados_llm.json"
        saida.write_text(json.dumps({"artigo": args.artigo_demo, "modelo": config.MODELO_CHAT,
                                     "extraido": extraido, "comparacao": comparacao},
                                    ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"   salvo em {saida.relative_to(config.RAIZ)}")
