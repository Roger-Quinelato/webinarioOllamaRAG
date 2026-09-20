import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402
import rag  # noqa: E402
from retrieval_calibration import PERGUNTAS_NEGATIVAS, PERGUNTAS_POSITIVAS  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")


# why: dá ao autor um segundo sinal (idioma_csv × idioma_detectado, contagem de frases,
# início do abstract) para a conferência manual do critério 1.6, sem que ele precise abrir
# cada PDF — heurística de palavras funcionais en/pt, sem dependência nova (ticket #11/T11).
_PALAVRAS_FUNCIONAIS = {
    "pt": {"de", "que", "não", "para", "com", "uma", "dos", "das", "como", "mais",
           "são", "por", "ao", "os", "as", "é", "na", "no", "se", "também"},
    "en": {"the", "and", "of", "in", "to", "is", "for", "that", "with", "as",
           "on", "are", "this", "by", "from", "an", "be", "we", "our"},
}


def _detectar_idioma(texto):
    palavras = re.findall(r"[a-zà-úA-ZÀ-Ú]+", texto.lower())
    contagens = {idioma: sum(1 for p in palavras if p in funcionais)
                 for idioma, funcionais in _PALAVRAS_FUNCIONAIS.items()}
    if not any(contagens.values()):
        return "?"
    return max(contagens, key=contagens.get)


def _contar_frases(texto):
    return len([f for f in re.split(r"[.!?]+", texto) if f.strip()])


def e1_resumos():
    metadados = rag.carregar_metadados()
    if not metadados:
        print("1.6 FALHA: Nenhum metadado encontrado (nada para checar)")
        sys.exit(1)
    falhas = 0
    for meta in metadados:
        resumo = meta["resumo"]
        idioma_detectado = _detectar_idioma(resumo) if resumo else "?"
        frases = _contar_frases(resumo) if resumo else 0
        paginas = rag.extrair_paginas(config.PASTA_ARTIGOS / meta["arquivo"])
        abstract = rag.extrair_abstract(paginas[0]) if paginas else ""
        primeiras_palavras = " ".join(abstract.split()[:3])
        print(f"{meta['arquivo']} [idioma_csv={meta['idioma']} idioma_detectado={idioma_detectado}] "
              f"vazio={not resumo} frases={frases}")
        print(f"   abstract[:3 palavras]={primeiras_palavras!r}")
        print(f"   resumo={resumo}")
        if not resumo:
            print(f"1.6 FALHA: Resumo vazio para {meta['arquivo']}")
            falhas += 1
    if falhas:
        sys.exit(1)


def e2():
    colecao = rag.abrir_colecao()
    dados = colecao.get(include=["metadatas"])
    metas = dados["metadatas"]
    contagem_antes = colecao.count()
    if not metas or contagem_antes == 0:
        print("2.2 FALHA: Coleção vazia (nada para checar)")
        sys.exit(1)
    if len(metas) != contagem_antes:
        print(f"2.2 FALHA: contagem diverge (get={len(metas)}, count={contagem_antes})")
        sys.exit(1)
    print(f"2.2 total de chunks: {len(metas)}")
    obrigatorios = set(config.COLUNAS_METADADOS) | {"pagina", "chunk_id", "tipo_chunk"}
    incompletos = [m.get("chunk_id") for m in metas if not obrigatorios <= set(m)]
    if incompletos:
        print(f"2.2 FALHA: chunks sem algum metadado obrigatório: {len(incompletos)} {incompletos[:5]}")
        sys.exit(1)
    print(f"2.2 amostra: {metas[0]}")
    tipos = Counter(m["tipo_chunk"] for m in metas)
    resumos_por_artigo = Counter(m["arquivo"] for m in metas if m["tipo_chunk"] == "resumo")
    print(f"2.3 por tipo_chunk: {dict(tipos)} | resumos por artigo: {dict(resumos_por_artigo)}")
    print(f"2.4 metadata da coleção: {colecao.metadata}")
    amostra = colecao.get(limit=50, include=["embeddings"])
    dimensoes = sorted({len(v) for v in amostra['embeddings']})
    print(f"2.4 dimensões distintas em 50 vetores: {dimensoes}")
    if len(dimensoes) != 1:
        print(f"2.4 FALHA: Mais de um modelo de embedding na coleção (dimensões distintas: {dimensoes})")
        sys.exit(1)
    print(f"2.6 contagem neste processo novo (reabrindo chroma_db/): {contagem_antes}")


def e2_sobreposicao():
    pagina = rag.extrair_paginas(config.PASTA_ARTIGOS / "lewis2020_rag.pdf")[2]
    pedacos = rag.dividir_texto(pagina)
    if len(pedacos) < 2:
        print("2.1 FALHA: Nada para checar (página não dividida em múltiplos chunks)")
        sys.exit(1)
    print(f"2.1 página 3 de lewis2020_rag.pdf: {len(pagina)} caracteres -> {len(pedacos)} chunks "
          f"de tamanhos {[len(p) for p in pedacos]} (limite {config.TAMANHO_CHUNK})")
    falhas = 0
    for i, (atual, proximo) in enumerate(zip(pedacos, pedacos[1:])):
        inicio_proximo = proximo[:80]
        posicao = atual.find(inicio_proximo)
        print(f"2.1 início do chunk {i + 1} aparece no fim do chunk {i}: {posicao != -1} "
              f"(sobreposição de {len(atual) - posicao if posicao != -1 else 0} caracteres) -> {inicio_proximo!r}")
        if posicao == -1:
            falhas += 1
    if falhas:
        print("2.1 FALHA: sobreposição ausente")
        sys.exit(1)


def e2_reabrir():
    colecao = rag.abrir_colecao()
    contagem_antes = colecao.count()
    if contagem_antes == 0:
        print("2.6 FALHA: Coleção vazia (nada para checar)")
        sys.exit(1)
    codigo = "import rag; print(rag.abrir_colecao().count())"
    saida = subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, capture_output=True, text=True)
    contagem_outro = int(saida.stdout.strip()) if saida.stdout.strip().isdigit() else -1
    print(f"2.6 contagem em outro processo: {saida.stdout.strip()} {saida.stderr.strip()[-200:]}")
    if saida.returncode != 0 or contagem_outro != contagem_antes:
        print("2.6 FALHA: reabrir em outro processo divergiu ou falhou")
        sys.exit(1)


def e3():
    colecao = rag.abrir_colecao()
    if colecao.count() == 0:
        print("3.1 FALHA: Nada para checar (coleção vazia)")
        sys.exit(1)
    pergunta = "Quais métricas o Ragas usa para avaliar um pipeline de RAG?"
    falhas = 0
    for k in (1, 4, 8):
        resultados = rag.buscar(pergunta, k=k, colecao=colecao)
        distancias = [r["distancia"] for r in resultados]
        campos = all({"texto", "distancia", "arquivo", "pagina"} <= set(r) for r in resultados)
        print(f"3.1/3.2 k={k}: {len(resultados)} resultados | ordenado={distancias == sorted(distancias)} "
              f"| campos texto/distancia/arquivo/pagina={campos}")
        if len(resultados) != k or distancias != sorted(distancias) or not campos:
            falhas += 1
            print(f"FALHA na busca simples para k={k}")
    resultados = rag.buscar(pergunta, k=4, colecao=colecao)
    posicoes = [r["posicao"] for r in resultados if r["arquivo"] == "es2023_ragas.pdf"]
    print(f"3.3 pergunta: {pergunta!r} | esperado es2023_ragas.pdf | posições no top-4: {posicoes}")
    if not posicoes:
        falhas += 1
        print("FALHA: artigo es2023_ragas.pdf não retornou no top-k")
    filtros = {"ano >= 2023": ({"ano": {"$gte": 2023}}, lambda r: r["ano"] >= 2023),
               "tema = retrieval": ({"tema": "retrieval"}, lambda r: r["tema"] == "retrieval"),
               "idioma = en": ({"idioma": "en"}, lambda r: r["idioma"] == "en")}
    for nome, (filtro, regra) in filtros.items():
        resultados = rag.buscar("Como funciona a recuperação de passagens?", k=8, where=filtro, colecao=colecao)
        obedece = all(map(regra, resultados))
        print(f"3.4 {nome}: {len(resultados)} resultados, todos obedecem = {obedece}")
        if not resultados or not obedece:
            falhas += 1
            print(f"FALHA no filtro {nome}")
    pergunta_pt = "O desempenho cai quando a informação relevante está no meio de um contexto longo?"
    resultados = rag.buscar(pergunta_pt, k=3, colecao=colecao)
    print(f"3.5 cross-lingual: {pergunta_pt!r} -> {[(r['arquivo'], r['pagina'], r['idioma']) for r in resultados]}")
    if resultados:
        print(f"    trecho do 1º: {resultados[0]['texto'][:200]}")
    else:
        falhas += 1
    # T12/#12: idioma=pt passou a ter 2 artigos reais (rocha2025_ragsft, medeiros2025_embeddings_pt);
    # o filtro que garante zero resultados sem depender do idioma agora é um ano fora do corpus.
    vazio = rag.buscar("O que é RAG?", k=4, where={"ano": {"$gte": 2030}}, colecao=colecao)
    print(f"3.6 filtro ano>=2030 (sem artigos): {len(vazio)} resultados, sem erro")
    if len(vazio) > 0:
        falhas += 1
        print("FALHA: Filtro para ano>=2030 encontrou resultados")
    com_pt = rag.buscar("O que é RAG?", k=4, where={"idioma": "pt"}, colecao=colecao)
    obedece_pt = all(r['idioma'] == 'pt' for r in com_pt)
    print(f"3.6b filtro idioma=pt (com artigos, T12/#12): {len(com_pt)} resultados, "
          f"todos pt = {obedece_pt}")
    if not com_pt or not obedece_pt:
        falhas += 1
        print("FALHA: Filtro idioma=pt retornou 0 ou violou a regra")

    if falhas:
        sys.exit(1)


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
    # T12/#12: idioma=pt deixou de esvaziar o estágio 1 (2 artigos reais agora); troca para um
    # filtro por ano fora do corpus, que continua esvaziando os resumos independente do idioma.
    vazio = rag.buscar_dois_estagios("O que é RAG?", k=4, where={"ano": {"$gte": 2030}}, colecao=colecao)
    print(f"4.4a estágio 1 vazio (ano>=2030): caminho = {vazio['caminho']!r}, {len(vazio['resultados'])} resultados")

    # hazard (T07): 4.4a só cobre o filtro herdado deixando o estágio 1 sem NENHUM resumo — não
    # prova que o limiar de distância (achado 4.4 original, calibrado no T06) dispara sozinho para
    # uma pergunta fora da base sem filtro nenhum, caso em que o estágio 1 sempre acha 3 "vizinhos".
    prefixo_esperado = "busca simples (estágio 1 sem correspondência: resumo mais próximo"
    # why: reaproveita a mesma pergunta-teste de _PERGUNTAS_FORA_ESTAGIO_1 (T06) em vez de repetir
    # a string aqui — se a calibração mudar de pergunta, os dois lugares não podem se desalinhar.
    fora = rag.buscar_dois_estagios(_PERGUNTAS_FORA_ESTAGIO_1[0], k=4, colecao=colecao)
    prefixo_ok = fora["caminho"].startswith(prefixo_esperado)
    print(f"4.4b pergunta fora da base sem filtro: caminho = {fora['caminho']!r} "
          f"| começa com {prefixo_esperado!r} = {prefixo_ok} | {len(fora['resultados'])} resultados")
    if fora["caminho"] == "dois estágios" or not prefixo_ok:
        sys.exit(1)


# hazard (T06): DISTANCIA_MAXIMA_ESTAGIO_1 em config.py foi um número escolhido sem dados — esta
# checagem calibra o limiar contra perguntas reais dentro e fora da base, para não escolher um
# valor que derrube (recuse) pergunta dentro da base (pior erro) ou nunca dispare o fallback
# (achado 4.4 original).
_PERGUNTAS_DENTRO_ESTAGIO_1 = PERGUNTAS_POSITIVAS
_PERGUNTAS_FORA_ESTAGIO_1 = PERGUNTAS_NEGATIVAS


def _escolher_limiar_estagio_1(distancias_dentro, distancias_fora):
    # why: "escolher o valor que não derruba nenhuma pergunta dentro da base" (spec do T06) é
    # sempre a maior distância "dentro", haja ou não sobreposição com "fora" — sobreposição só
    # muda se esse valor também aceita algum falso positivo de fallback (declarado tolerável).
    # Extraído como função pura (sem rag/Ollama) para dar para testar o ramo de sobreposição com
    # dados sintéticos — os dados reais deste corpus não sobrepõem, então só um autoteste prova
    # que a lógica funciona (achado do /code-review).
    maior_dentro = max(distancias_dentro)
    menor_fora = min(distancias_fora)
    return maior_dentro, maior_dentro >= menor_fora


def _autoteste_escolher_limiar():
    limiar, sobreposicao = _escolher_limiar_estagio_1([0.30, 0.50, 0.65], [0.60, 0.70])
    ok = sobreposicao and abs(limiar - 0.65) < 1e-9
    print(f"T06 autoteste (dados sintéticos com sobreposição, prova o ramo que os dados reais não "
          f"exercitam): limiar sugerido={limiar:.4f} sobreposição={sobreposicao} -> {'OK' if ok else 'FALHOU'}")
    if not ok:
        sys.exit(1)


def e4_limiar():
    _autoteste_escolher_limiar()
    colecao = rag.abrir_colecao()

    def distancia_estagio_1(pergunta):
        # why: rag.buscar() força tipo_chunk="pagina" (combinar_filtros com um where tipo_chunk=
        # "resumo" dá resultado vazio); rag.buscar_dois_estagios(n_artigos=1) já roda a mesma busca
        # do estágio 1 internamente e devolve "artigos" com a distância real, mesmo quando o limiar
        # decide cair no fallback — evita tocar a função privada _consultar direto daqui.
        dois = rag.buscar_dois_estagios(pergunta, n_artigos=1, colecao=colecao)
        return dois["artigos"][0]["distancia"]

    grupos = {"dentro da base": [(p, distancia_estagio_1(p)) for p in _PERGUNTAS_DENTRO_ESTAGIO_1],
              "fora da base": [(p, distancia_estagio_1(p)) for p in _PERGUNTAS_FORA_ESTAGIO_1]}

    print("T06 distância do resumo mais próximo (estágio 1):")
    for nome, casos in grupos.items():
        print(f"  {nome}:")
        for p, d in casos:
            print(f"    {d:.4f}  {p}")

    dentro, fora = grupos["dentro da base"], grupos["fora da base"]
    limiar_sugerido, sobreposicao = _escolher_limiar_estagio_1([d for _, d in dentro], [d for _, d in fora])
    menor_fora = min(d for _, d in fora)
    print(f"\nT06 maior distância dentro da base: {limiar_sugerido:.4f}")
    print(f"T06 menor distância fora da base: {menor_fora:.4f}")
    if sobreposicao:
        print(f"T06 intervalos SE SOBREPÕEM (maior dentro {limiar_sugerido:.4f} ≥ menor fora {menor_fora:.4f}) "
              f"— limiar sugerido = {limiar_sugerido:.4f} (a maior distância dentro da base): falso positivo "
              f"de fallback (tratar uma pergunta fora como se fosse mais uma dentro) é aceitável, recusa "
              f"indevida de pergunta dentro da base não é.")
    else:
        print(f"T06 intervalos não se sobrepõem — limiar seguro em qualquer ponto de "
              f"({limiar_sugerido:.4f}, {menor_fora:.4f}); sugerido = {limiar_sugerido:.4f}")
    print(f"\nT06 config.DISTANCIA_MAXIMA_ESTAGIO_1 atual: {config.DISTANCIA_MAXIMA_ESTAGIO_1}")
    if config.DISTANCIA_MAXIMA_ESTAGIO_1 < limiar_sugerido:
        print(f"T06 limiar atual ({config.DISTANCIA_MAXIMA_ESTAGIO_1}) é MENOR que o sugerido "
              f"({limiar_sugerido:.4f}) — derrubaria pergunta legítima, precisa subir")
        sys.exit(1)
    print("T06 limiar atual cobre com folga todas as perguntas dentro da base testadas")


def e6_ollama_desligado():
    rag._cliente = None
    config.OLLAMA_HOST = "http://localhost:11999"
    falhas = 0
    for nome, chamada in {"gerar_embeddings": lambda: rag.gerar_embeddings(["teste"]),
                          "responder": lambda: list(rag.responder("teste", []))}.items():
        try:
            chamada()
            print(f"6.7 {nome}: NÃO levantou erro")
            falhas += 1
        except rag.OllamaIndisponivel as erro:
            print(f"6.7 {nome}: OllamaIndisponivel -> {erro}")
    if falhas:
        print("6.7 FALHA: chamada que deveria levantar OllamaIndisponivel não levantou")
        sys.exit(1)


def e6_ollama_desligado_scripts():
    # hazard: testar só rag.py (e6_ollama_desligado) não prova nada sobre os scripts — cada um
    # importa rag e chama o Ollama por conta própria, e o achado 6.7 mostrou 03-06 e opcional/
    # sem nenhum try/except em volta, deixando o traceback vazar para quem está assistindo a aula.
    ambiente = {**__import__("os").environ, "OLLAMA_HOST": "http://localhost:11999", "PYTHONIOENCODING": "utf-8"}
    alvos = [*sorted((RAIZ / "scripts").glob("0[3-7]_*.py")), *sorted((RAIZ / "opcional").glob("*.py"))]
    falhas = []
    for script in alvos:
        saida = subprocess.run([sys.executable, str(script)], cwd=RAIZ, capture_output=True, text=True,
                               env=ambiente, timeout=60)
        tem_traceback = "Traceback (most recent call last)" in saida.stderr
        mensagem_clara = "ERRO:" in saida.stdout or "OllamaIndisponivel" in saida.stdout
        ok = not tem_traceback and (mensagem_clara or saida.returncode != 0)
        print(f"6.7 {script.relative_to(RAIZ).as_posix()}: exit={saida.returncode} "
              f"traceback={tem_traceback} mensagem_clara={mensagem_clara} → {'OK' if ok else 'FALHOU'}")
        if not ok:
            falhas.append(script.name)
    if falhas:
        print(f"6.7 scripts sem tratamento adequado: {falhas}")
        sys.exit(1)


def e6_fontes():
    # hazard: cobre os casos que a comparação exata anterior perdia (achado 6.5) — citação parcial,
    # ausência de citação, e a recusa disfarçada por citação colada ou espaçamento irregular do LLM.
    resultados = [{"arquivo": f"artigo{i}.pdf", "pagina": i} for i in range(1, 4)]
    recusa = config.RESPOSTA_NAO_ENCONTRADA
    casos = [
        ("citação parcial", "Segundo [2], blá blá.", [2]),
        ("sem citação", "Resposta sem nenhuma citação.", [1, 2, 3]),
        ("recusa exata", recusa, []),
        ("recusa com [1]", f"{recusa} [1]", []),
        ("recusa com espaço extra", "  " + recusa.replace(" ", "  ") + "  ", []),
    ]
    falhas = []
    for nome, texto, esperado in casos:
        indices = [i for i, _ in rag.fontes_da_resposta(texto, resultados)]
        ok = indices == esperado
        print(f"6.5 {nome}: esperado={esperado} obtido={indices} → {'OK' if ok else 'FALHOU'}")
        if not ok:
            falhas.append(nome)
    if falhas:
        print(f"6.5 casos com divergência: {falhas}")
        sys.exit(1)


# hazard (achado 6.5/7.4, T02): função homônima não é a única forma de copiar lógica do
# pipeline — dava para reimplementar a regra de recusa/fontes ou chamar o Ollama direto sem
# nunca definir uma função com o mesmo nome de rag.py, escapando da checagem por nome acima.
# Cada padrão aqui reproduz uma forma real de cópia já vista no código (scripts/06 antes do T01).
# hazard: o padrão de .chat(/.embed( é um heurístico de texto, não AST — um método .chat(/.embed(
# de outra biblioteca (ex.: st.chat_input() do Streamlit, que não bate por terminar diferente)
# poderia disparar um falso positivo; se isso acontecer, a saída impressa aponta o arquivo/trecho
# para conferência manual, então o achado não passa despercebido.
_PADROES_COPIA_PIPELINE = {
    "RESPOSTA_NAO_ENCONTRADA in ...": re.compile(r"RESPOSTA_NAO_ENCONTRADA\s+in\b"),
    "indices_citados(...) or list(range(...))": re.compile(r"indices_citados\([^)]*\)\s*or\s*list\(range\("),
    "import ollama direto": re.compile(r"^\s*import ollama\b", re.MULTILINE),
    "cliente_ollama() direto": re.compile(r"cliente_ollama\("),
    ".chat(/.embed( direto no cliente Ollama (fora de rag.py)": re.compile(r"(?<!\brag)\.(chat|embed)\("),
}


def _achados_copia_pipeline(nome, texto):
    return [rotulo for rotulo, padrao in _PADROES_COPIA_PIPELINE.items() if padrao.search(texto)]


def e7_duplicadas_antes_v2(commit="ba814a0"):
    # why: prova, de um jeito versionado e reexecutável (não um script solto fora do repo), que
    # _achados_copia_pipeline pegaria a duplicação que scripts/06_com_sem_contexto.py tinha antes
    # do T01/T02 — sem precisar reintroduzir a duplicação no código real para testar isso.
    saida = subprocess.run(["git", "show", f"{commit}:scripts/06_com_sem_contexto.py"],
                           cwd=RAIZ, capture_output=True, text=True, check=True)
    achados = _achados_copia_pipeline("scripts/06_com_sem_contexto.py", saida.stdout)
    print(f"7.4 ANTES (scripts/06_com_sem_contexto.py no commit {commit}): {achados or 'nenhum'}")
    if not achados:
        print(f"7.4 ANTES deveria ter achado a cópia e não achou — checagem não prova nada")
        sys.exit(1)


def e7_duplicadas():
    import ast
    import json

    # hazard: a versão anterior desta checagem só comparava nomes de função, não varria
    # ferramentas/, ignorava opcional/ na lista de "usadas por" e nunca falhava — o ✅ do
    # critério 7.4 se apoiava nela sem que ela pudesse de fato reprovar nada (achado da revisão).
    arquivos_py = [RAIZ / "rag.py", RAIZ / "app.py",
                   *sorted((RAIZ / "scripts").glob("*.py")),
                   *sorted((RAIZ / "opcional").glob("*.py")),
                   *sorted((RAIZ / "ferramentas").glob("*.py"))]

    definidas = {}
    for arquivo in arquivos_py:
        for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
            if isinstance(no, ast.FunctionDef):
                definidas.setdefault(no.name, []).append(arquivo.relative_to(RAIZ).as_posix())

    notebook = json.loads((RAIZ / "webinario_rag.ipynb").read_text(encoding="utf-8"))
    for celula in notebook["cells"]:
        if celula["cell_type"] == "code":
            for no in ast.walk(ast.parse("".join(celula["source"]))):
                if isinstance(no, ast.FunctionDef):
                    definidas.setdefault(no.name, []).append("webinario_rag.ipynb")

    # Uma função homônima em rag.py e em outro lugar é o sinal real de cópia divergente do
    # pipeline; homônimas fora de rag.py (ex.: "colecao" em app.py e no notebook, que são coisas
    # diferentes — cache do Streamlit vs. variável local) são só coincidência de nome e não contam.
    funcoes_rag = {n for n, locais in definidas.items() if "rag.py" in locais}
    duplicadas_do_pipeline = {n: locais for n, locais in definidas.items()
                              if n in funcoes_rag and len(set(locais)) > 1}
    print(f"7.4 funções de rag.py também definidas em outro arquivo: {duplicadas_do_pipeline or 'nenhuma'}")

    fora_do_rag = {n: locais for n, locais in definidas.items() if "rag.py" not in locais}
    print(f"7.4 funções fora do rag.py (apresentação/verificação, não reimplementam o pipeline): {fora_do_rag}")

    arquivos_chamadores = [RAIZ / "app.py", *sorted((RAIZ / "scripts").glob("*.py")),
                           *sorted((RAIZ / "opcional").glob("*.py"))]
    chamadas = sorted({no.attr for arquivo in arquivos_chamadores
                       for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8")))
                       if isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name) and no.value.id == "rag"})
    print(f"7.4 funções do rag.py usadas por app.py, scripts/ e opcional/: {chamadas}")

    chamadas_privadas = [c for c in chamadas if c.startswith("_")]
    print(f"7.4 chamadores tocando internals privados de rag.py (leak de 7.4/Shotgun Surgery): "
          f"{chamadas_privadas or 'nenhum'}")

    # scripts/, opcional/ e app.py só chamam rag.py (regra de "Arquitetura" do CLAUDE.md); o
    # notebook é gerado, mas suas células viram código real quando executadas, então valem a
    # mesma regra. ferramentas/ fica de fora: são scripts de apoio (medição, construção do
    # notebook), não o pipeline em si, e medir.py chama rag.chat() direto de propósito.
    copia_pipeline = {}
    for arquivo in arquivos_chamadores:
        achados = _achados_copia_pipeline(arquivo.name, arquivo.read_text(encoding="utf-8"))
        if achados:
            copia_pipeline[arquivo.relative_to(RAIZ).as_posix()] = achados
    for celula in notebook["cells"]:
        if celula["cell_type"] == "code":
            achados = _achados_copia_pipeline("webinario_rag.ipynb", "".join(celula["source"]))
            if achados:
                copia_pipeline.setdefault("webinario_rag.ipynb", []).extend(achados)
    print(f"7.4 padrões de cópia de lógica do pipeline fora de rag.py: {copia_pipeline or 'nenhum'}")

    if duplicadas_do_pipeline or chamadas_privadas or copia_pipeline:
        sys.exit(1)


def e7_estrutura():
    import json

    notebook = json.loads((RAIZ / "webinario_rag.ipynb").read_text(encoding="utf-8"))
    titulos = [linha for celula in notebook["cells"] if celula["cell_type"] == "markdown"
               for linha in "".join(celula["source"]).splitlines() if linha.startswith("## ")]
    print("7.3 títulos de bloco no notebook:")
    for titulo in titulos:
        print(f"    {titulo}")
    if len(titulos) < 5:
        print("7.3 FALHA: Faltam blocos principais do cronograma no notebook")
        sys.exit(1)

    print("7.6 células que carregam resultado pré-computado ou têm chave para rodar ao vivo:")
    pre_computadas = 0
    for celula in notebook["cells"]:
        fonte = "".join(celula["source"])
        if celula["cell_type"] == "code" and ("carregar_resultado" in fonte or "_AO_VIVO" in fonte
                                              or "REINDEXAR" in fonte):
            print(f"    [{celula.get('execution_count')}] {fonte.splitlines()[0][:90]}")
            pre_computadas += 1
    if pre_computadas < 3:
        print("7.6 FALHA: Células com saída pré-computada de etapas lentas ausentes (deveriam ser pelo menos 3)")
        sys.exit(1)


# hazard (achado 5a.1/7.2/9.1, T08): números de evidência (ex.: tempo do SHAP) citados em docs/
# ficam defasados em relação à última execução salva do notebook, e ninguém percebe porque não há
# checagem automática. Esta extrai os tempos de fato salvos em webinario_rag.ipynb, sem precisar de
# kernel (só lê o JSON), para comparar contra o que os docs afirmam.
_PADROES_TEMPO_NOTEBOOK = {
    "indexação": re.compile(r"Indexa[çc][ãa]o em ([\d.,]+)s"),
    "extração": re.compile(r"Extra[çc][ãa]o em ([\d.,]+)s"),
    "resumo ao vivo": re.compile(r"RESUMO AO VIVO \(([\d.,]+)s\)"),
    "shap": re.compile(r"SHAP em ([\d.,]+)s"),
    "resposta bloco 6": re.compile(r"\[([\d.,]+)s com ([^\]]+)\]"),
}
# "indexação" só aparece quando REINDEXAR=True (não é o padrão do notebook distribuído — evita os
# ~19min de reindexação a cada execução); os outros 4 sempre imprimem sob os flags padrão do
# notebook (LLM_AO_VIVO=True, SHAP_AO_VIVO=True definidos em construir_notebook.py). Exigir todos
# os 5 quebraria a execução normal; exigir só "achou algo" deixaria passar sem ninguém notar se só
# UM desses 4 parar de bater (ex.: alguém reescreve o texto do print em construir_notebook.py) —
# achado do /code-review.
_PADROES_TEMPO_OBRIGATORIOS = {"extração", "resumo ao vivo", "shap", "resposta bloco 6"}


def e7_saidas():
    import json

    notebook = json.loads((RAIZ / "webinario_rag.ipynb").read_text(encoding="utf-8"))
    tempos = {}
    print("7.2/9.1 células do notebook (sem kernel — só lê o .ipynb salvo):")
    for i, celula in enumerate(notebook["cells"], start=1):
        if celula["cell_type"] != "code":
            continue
        fonte = "".join(celula["source"])
        tem_saida = bool(celula.get("outputs"))
        primeira_linha = fonte.splitlines()[0][:70] if fonte else ""
        print(f"    [{i}] saída={tem_saida} | {primeira_linha!r}")
        for saida in celula.get("outputs", []):
            texto = "".join(saida.get("text", [])) or "".join(saida.get("data", {}).get("text/plain", []))
            for nome, padrao in _PADROES_TEMPO_NOTEBOOK.items():
                for m in padrao.finditer(texto):
                    tempos.setdefault(nome, []).append((i, m.group(0)))

    print("\n7.2/9.1 tempos extraídos do notebook atual (para comparar com docs/medicoes.md e afins):")
    faltando = _PADROES_TEMPO_OBRIGATORIOS - tempos.keys()
    if faltando:
        print(f"    padrões obrigatórios sem nenhuma ocorrência: {sorted(faltando)} — ou o notebook não "
              f"foi executado com os flags padrão (LLM_AO_VIVO=True, SHAP_AO_VIVO=True), ou o texto do "
              f"print mudou em construir_notebook.py e o regex correspondente em verificar.py ficou para trás")
        sys.exit(1)
    for nome, ocorrencias in tempos.items():
        for celula_i, texto in ocorrencias:
            print(f"    [célula {celula_i}] {nome}: {texto}")


# hazard (achado 9.1, T10): docs/medicoes.md cita números "na última execução do notebook" (o
# jeito que o documento marca "isto veio de rodar o notebook, não de medir.py") que ficam
# defasados quando o notebook é reexecutado — ninguém percebia porque nada comparava o texto
# contra a evidência real. Esta checagem confere cada um contra E7/saidas_notebook.txt.
_PADRAO_NUMERO_ULTIMA_EXECUCAO = re.compile(r"(\d+(?:[.,]\d+)?)\s*s\s*na última execução do notebook")


def e9_numeros():
    medicoes = (RAIZ / "docs" / "medicoes.md").read_text(encoding="utf-8")
    saidas = (RAIZ / "docs" / "evidencias" / "E7" / "saidas_notebook.txt").read_text(encoding="utf-8")

    achados = _PADRAO_NUMERO_ULTIMA_EXECUCAO.findall(medicoes)
    print(f"9.1 números 'na última execução do notebook' em docs/medicoes.md: {achados}")
    # hazard (/code-review): se a frase exata "na última execução do notebook" for reescrita (ou
    # sumir) em medicoes.md, achados vira [] e a checagem passaria calada com exit 0 sem ter
    # conferido nada — o oposto do que este ticket existe para garantir. Pelo menos 2 menções são
    # esperadas hoje (SHAP no bloco 4, resposta no bloco 6); zero é sinal de checagem quebrada, não
    # de "nada para verificar".
    if not achados:
        print("9.1 nenhuma menção encontrada — ou o texto de medicoes.md mudou e o regex ficou "
              "para trás, ou os números foram removidos; de qualquer forma, precisa de revisão manual")
        sys.exit(1)

    faltando = []
    for numero in achados:
        normalizado = numero.replace(",", ".")
        if not re.search(rf"(?<!\d){re.escape(normalizado)}s\b", saidas):
            faltando.append(numero)
    print(f"9.1 números sem confirmação em docs/evidencias/E7/saidas_notebook.txt: {faltando or 'nenhum'}")
    if faltando:
        sys.exit(1)


# hazard (achado AUD-002): todo script que fala com o Ollama tem de envolver a execução em
# rag.cli_seguro(), senão o Ollama fora vaza traceback cru na aula. e6_ollama_desligado_scripts
# prova isso em runtime, mas seu glob 0[3-7] deixava 01 e 02 de fora — a lacuna exata do AUD-002.
# Esta guarda é estática (só lê o texto): cobre todos os scripts e não roda o pipeline, porque
# indexar() faz delete_collection() antes de embutir (rag.py) e rodar 02 com o Ollama fora zeraria
# o índice. O heurístico de .chat(/.embed( pode dar falso positivo (como em e6_fontes), mas aí a
# linha impressa aponta o arquivo para conferência, então nada passa despercebido.
_ENTRADA_LLM = re.compile(
    r"\brag\.(resumir_abstract|extrair_metadados_llm|indexar|buscar|buscar_dois_estagios|responder|gerar_embeddings)\("
    r"|(?<!\brag)\.(chat|embed)\(|cliente_ollama\(|^\s*import ollama\b",
    re.MULTILINE)


def e6_cli_seguro():
    alvos = [*sorted((RAIZ / "scripts").glob("*.py")), *sorted((RAIZ / "opcional").glob("*.py"))]
    falhas = []
    for script in alvos:
        texto = script.read_text(encoding="utf-8")
        usa_llm = bool(_ENTRADA_LLM.search(texto))
        protegido = "rag.cli_seguro()" in texto
        precisa = usa_llm and not protegido
        print(f"AUD-002 {script.relative_to(RAIZ).as_posix():34s} usa_llm={usa_llm!s:5} "
              f"cli_seguro={protegido!s:5} → {'FALTA' if precisa else 'ok'}")
        if precisa:
            falhas.append(script.relative_to(RAIZ).as_posix())
    if falhas:
        print(f"AUD-002 scripts que falam com o Ollama sem rag.cli_seguro(): {falhas}")
        sys.exit(1)


if __name__ == "__main__":
    inicio = time.perf_counter()
    globals()[sys.argv[1]]()
    print(f"[{sys.argv[1]} em {time.perf_counter() - inicio:.1f}s]")
