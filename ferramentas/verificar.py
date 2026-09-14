import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402
import rag  # noqa: E402


def e1_resumos():
    for meta in rag.carregar_metadados():
        print(f"{meta['arquivo']} [idioma={meta['idioma']}] vazio={not meta['resumo']}")
        print(f"   {meta['resumo']}")


def e2():
    colecao = rag.abrir_colecao()
    dados = colecao.get(include=["metadatas"])
    metas = dados["metadatas"]
    print(f"2.2 total de chunks: {len(metas)}")
    obrigatorios = set(config.COLUNAS_METADADOS) | {"pagina", "chunk_id", "tipo_chunk"}
    incompletos = [m.get("chunk_id") for m in metas if not obrigatorios <= set(m)]
    print(f"2.2 chunks sem algum metadado obrigatório: {len(incompletos)} {incompletos[:5]}")
    print(f"2.2 amostra: {metas[0]}")
    tipos = Counter(m["tipo_chunk"] for m in metas)
    resumos_por_artigo = Counter(m["arquivo"] for m in metas if m["tipo_chunk"] == "resumo")
    print(f"2.3 por tipo_chunk: {dict(tipos)} | resumos por artigo: {dict(resumos_por_artigo)}")
    print(f"2.4 metadata da coleção: {colecao.metadata}")
    amostra = colecao.get(limit=50, include=["embeddings"])
    print(f"2.4 dimensões distintas em 50 vetores: {sorted({len(v) for v in amostra['embeddings']})}")
    contagem_antes = colecao.count()
    print(f"2.6 contagem neste processo novo (reabrindo chroma_db/): {contagem_antes}")


def e2_sobreposicao():
    pagina = rag.extrair_paginas(config.PASTA_ARTIGOS / "lewis2020_rag.pdf")[2]
    pedacos = rag.dividir_texto(pagina)
    print(f"2.1 página 3 de lewis2020_rag.pdf: {len(pagina)} caracteres → {len(pedacos)} chunks "
          f"de tamanhos {[len(p) for p in pedacos]} (limite {config.TAMANHO_CHUNK})")
    for i, (atual, proximo) in enumerate(zip(pedacos, pedacos[1:])):
        inicio_proximo = proximo[:80]
        posicao = atual.find(inicio_proximo)
        print(f"2.1 início do chunk {i + 1} aparece no fim do chunk {i}: {posicao != -1} "
              f"(sobreposição de {len(atual) - posicao if posicao != -1 else 0} caracteres) → {inicio_proximo!r}")


def e2_reabrir():
    codigo = "import rag; print(rag.abrir_colecao().count())"
    saida = subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, capture_output=True, text=True)
    print(f"2.6 contagem em outro processo: {saida.stdout.strip()} {saida.stderr.strip()[-200:]}")


def e3():
    colecao = rag.abrir_colecao()
    pergunta = "Quais métricas o Ragas usa para avaliar um pipeline de RAG?"
    for k in (1, 4, 8):
        resultados = rag.buscar(pergunta, k=k, colecao=colecao)
        distancias = [r["distancia"] for r in resultados]
        campos = all({"texto", "distancia", "arquivo", "pagina"} <= set(r) for r in resultados)
        print(f"3.1/3.2 k={k}: {len(resultados)} resultados | ordenado={distancias == sorted(distancias)} "
              f"| campos texto/distancia/arquivo/pagina={campos}")
    resultados = rag.buscar(pergunta, k=4, colecao=colecao)
    posicoes = [r["posicao"] for r in resultados if r["arquivo"] == "es2023_ragas.pdf"]
    print(f"3.3 pergunta: {pergunta!r} | esperado es2023_ragas.pdf | posições no top-4: {posicoes}")
    filtros = {"ano >= 2023": ({"ano": {"$gte": 2023}}, lambda r: r["ano"] >= 2023),
               "tema = retrieval": ({"tema": "retrieval"}, lambda r: r["tema"] == "retrieval"),
               "idioma = en": ({"idioma": "en"}, lambda r: r["idioma"] == "en")}
    for nome, (filtro, regra) in filtros.items():
        resultados = rag.buscar("Como funciona a recuperação de passagens?", k=8, where=filtro, colecao=colecao)
        print(f"3.4 {nome}: {len(resultados)} resultados, todos obedecem = {all(map(regra, resultados))}")
    pergunta_pt = "O desempenho cai quando a informação relevante está no meio de um contexto longo?"
    resultados = rag.buscar(pergunta_pt, k=3, colecao=colecao)
    print(f"3.5 cross-lingual: {pergunta_pt!r} → {[(r['arquivo'], r['pagina'], r['idioma']) for r in resultados]}")
    print(f"    trecho do 1º: {resultados[0]['texto'][:200]}")
    vazio = rag.buscar("O que é RAG?", k=4, where={"idioma": "pt"}, colecao=colecao)
    print(f"3.6 filtro idioma=pt (sem artigos): {len(vazio)} resultados, sem erro")


def e4():
    colecao = rag.abrir_colecao()
    pergunta = "Como treinar um retriever denso com poucos exemplos de perguntas e passagens?"
    dois = rag.buscar_dois_estagios(pergunta, k=4, colecao=colecao)
    escolhidos = [a["arquivo"] for a in dois["artigos"]]
    print(f"4.1 estágio 1: {len(dois['artigos'])} artigos | tipos: {[a['tipo_chunk'] for a in dois['artigos']]} "
          f"| {escolhidos}")
    print(f"4.2 estágio 2: todos os resultados dentro dos artigos escolhidos = "
          f"{all(r['arquivo'] in escolhidos for r in dois['resultados'])} "
          f"| tipos: {sorted({r['tipo_chunk'] for r in dois['resultados']})}")
    vazio = rag.buscar_dois_estagios("O que é RAG?", k=4, where={"idioma": "pt"}, colecao=colecao)
    print(f"4.4 estágio 1 vazio (idioma=pt): caminho = {vazio['caminho']!r}, {len(vazio['resultados'])} resultados")


def e6_ollama_desligado():
    rag._cliente = None
    config.OLLAMA_HOST = "http://localhost:11999"
    for nome, chamada in {"gerar_embeddings": lambda: rag.gerar_embeddings(["teste"]),
                          "responder": lambda: list(rag.responder("teste", []))}.items():
        try:
            chamada()
            print(f"6.7 {nome}: NÃO levantou erro")
        except rag.OllamaIndisponivel as erro:
            print(f"6.7 {nome}: OllamaIndisponivel → {erro}")


def e7_duplicadas():
    import ast

    definidas = {}
    for arquivo in [RAIZ / "rag.py", RAIZ / "app.py", *sorted((RAIZ / "scripts").glob("*.py")),
                    *sorted((RAIZ / "opcional").glob("*.py"))]:
        for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
            if isinstance(no, ast.FunctionDef):
                definidas.setdefault(no.name, []).append(arquivo.relative_to(RAIZ).as_posix())
    import json

    notebook = json.loads((RAIZ / "webinario_rag.ipynb").read_text(encoding="utf-8"))
    for celula in notebook["cells"]:
        if celula["cell_type"] == "code":
            for no in ast.walk(ast.parse("".join(celula["source"]))):
                if isinstance(no, ast.FunctionDef):
                    definidas.setdefault(no.name, []).append("webinario_rag.ipynb")
    repetidas = {n: locais for n, locais in definidas.items() if len(set(locais)) > 1}
    print(f"7.4 funções definidas em mais de um arquivo: {repetidas or 'nenhuma'}")
    fora_do_rag = {n: locais for n, locais in definidas.items() if "rag.py" not in locais}
    print(f"7.4 funções fora do rag.py (apresentação/verificação, não reimplementam o pipeline): {fora_do_rag}")
    chamadas = sorted({no.attr for arquivo in [RAIZ / "app.py", *sorted((RAIZ / "scripts").glob("*.py"))]
                       for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8")))
                       if isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name) and no.value.id == "rag"})
    print(f"7.4 funções do rag.py usadas por app.py e scripts/: {chamadas}")


def e7_estrutura():
    import json

    notebook = json.loads((RAIZ / "webinario_rag.ipynb").read_text(encoding="utf-8"))
    titulos = [linha for celula in notebook["cells"] if celula["cell_type"] == "markdown"
               for linha in "".join(celula["source"]).splitlines() if linha.startswith("## ")]
    print("7.3 títulos de bloco no notebook:")
    for titulo in titulos:
        print(f"    {titulo}")
    print("7.6 células que carregam resultado pré-computado ou têm chave para rodar ao vivo:")
    for celula in notebook["cells"]:
        fonte = "".join(celula["source"])
        if celula["cell_type"] == "code" and ("carregar_resultado" in fonte or "_AO_VIVO" in fonte
                                              or "REINDEXAR" in fonte):
            print(f"    [{celula.get('execution_count')}] {fonte.splitlines()[0][:90]}")


if __name__ == "__main__":
    inicio = time.perf_counter()
    globals()[sys.argv[1]]()
    print(f"[{sys.argv[1]} em {time.perf_counter() - inicio:.1f}s]")
