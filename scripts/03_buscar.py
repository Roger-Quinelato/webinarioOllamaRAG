import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rag  # noqa: E402

colecao = rag.abrir_colecao()
pergunta = "Quais métricas o Ragas usa para avaliar um pipeline de RAG?"

print(f"Pergunta: {pergunta}\n")
for k in (1, 4, 8):
    resultados = rag.buscar(pergunta, k=k, colecao=colecao)
    print(f"--- k = {k} ({len(resultados)} resultados)")
    print(rag.tabela_resultados(resultados))
    print()

print("--- Filtros where (k = 4)")
filtros = {
    "ano >= 2023": {"ano": {"$gte": 2023}},
    "tema = retrieval": {"tema": "retrieval"},
    "idioma = en": {"idioma": "en"},
    "ano = 2020 e tema = fundamentos": {"$and": [{"ano": 2020}, {"tema": "fundamentos"}]},
    "idioma = pt (ainda sem artigos em português)": {"idioma": "pt"},
}
for nome, filtro in filtros.items():
    resultados = rag.buscar("Como funciona a recuperação de passagens?", k=4, where=filtro, colecao=colecao)
    print(f"\n[{nome}] {filtro}")
    print(rag.tabela_resultados(resultados))

print("\n--- Cross-lingual: a mesma pergunta em português e em inglês")
for texto in ("O desempenho cai quando a informação relevante está no meio de um contexto longo?",
              "Does performance drop when relevant information is in the middle of a long context?"):
    print(f"\n{texto}")
    print(rag.tabela_resultados(rag.buscar(texto, k=3, colecao=colecao)))
