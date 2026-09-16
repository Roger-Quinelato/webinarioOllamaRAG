import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rag  # noqa: E402

with rag.cli_seguro():
    colecao = rag.abrir_colecao()
    perguntas = [
        "Como avaliar se a resposta é fiel ao contexto recuperado?",
        "Recuperar mais documentos sempre melhora a resposta do modelo?",
        "Como treinar um retriever denso com poucos exemplos de perguntas e passagens?",
    ]

    for pergunta in perguntas:
        print("=" * 100)
        print(f"Pergunta: {pergunta}\n")
        simples = rag.buscar(pergunta, k=4, colecao=colecao)
        print("Busca simples (todos os chunks):")
        print(rag.tabela_resultados(simples))

        dois = rag.buscar_dois_estagios(pergunta, k=4, colecao=colecao)
        print(f"\nCaminho usado: {dois['caminho']}")
        print("Estágio 1 — artigos escolhidos pelos resumos:")
        for artigo in dois["artigos"]:
            print(f"   {artigo['posicao']}. dist={artigo['distancia']:.4f} {artigo['arquivo']} — {artigo['titulo']}")
        print("Estágio 2 — chunks só desses artigos:")
        print(rag.tabela_resultados(dois["resultados"]))

        arquivos_simples = [r["arquivo"] for r in simples]
        arquivos_dois = [r["arquivo"] for r in dois["resultados"]]
        print(f"\nArtigos no top-4 simples:       {arquivos_simples}")
        print(f"Artigos no top-4 dois estágios: {arquivos_dois}")
        mudou = [r["chunk_id"] for r in simples] != [r["chunk_id"] for r in dois["resultados"]]
        print(f"Resultado mudou? {'sim' if mudou else 'não'}")

    print("=" * 100)
    print("Filtro que não casa com nenhum resumo (ano fora do corpus, T12/#12: idioma=pt já tem 2 artigos):")
    vazio = rag.buscar_dois_estagios("O que é RAG?", k=4, where={"ano": {"$gte": 2030}}, colecao=colecao)
    print(f"Caminho usado: {vazio['caminho']}")
    print(rag.tabela_resultados(vazio["resultados"]))

    print("\nPergunta fora da base (achado 4.4 — deve cair para busca simples, sem quebrar):")
    fora = rag.buscar_dois_estagios("Qual é a receita de pão de queijo mineiro?", k=4, colecao=colecao)
    print(f"Caminho usado: {fora['caminho']}")
    for artigo in fora["artigos"]:
        print(f"   estágio 1: dist={artigo['distancia']:.4f} {artigo['arquivo']}")
    print(rag.tabela_resultados(fora["resultados"]))
