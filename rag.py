import json
import math
import re
import sys
from contextlib import contextmanager
from itertools import combinations
from pathlib import Path

import chromadb
import httpx
import numpy as np
import ollama
from corpus import carregar_metadados, salvar_metadados, limpar_texto, extrair_paginas, dividir_texto, gerar_chunks

import config


class OllamaIndisponivel(RuntimeError):
    """Representa erro Ollama Indisponível. Herda de RuntimeError."""
    pass


_cliente = None


def cliente_ollama():
    """Descreve cliente Ollama."""
    global _cliente
    if _cliente is None:
        _cliente = ollama.Client(host=config.OLLAMA_HOST)
    return _cliente


def _erro_ollama(erro, modelo=None):
    """Auxilia erro Ollama."""
    if isinstance(erro, ollama.ResponseError) and erro.status_code == 404 and modelo:
        return OllamaIndisponivel(f"O modelo '{modelo}' não está baixado. Rode no terminal: ollama pull {modelo}")
    return OllamaIndisponivel(
        f"Não consegui falar com o Ollama em {config.OLLAMA_HOST}. "
        "Abra o aplicativo Ollama (ou rode `ollama serve`) e tente de novo. "
        f"Detalhe: {erro}"
    )


_ERROS_CONEXAO = (ConnectionError, httpx.ConnectError, httpx.TimeoutException, ollama.ResponseError)


# why: ponto único de saída amigável para os scripts de CLI — sem isto, 03-07 e opcional/*.py
# reimplementavam o mesmo try/except em volta do corpo inteiro (achado 7.4/Duplicated Code).
@contextmanager
def cli_seguro():
    """Descreve CLI seguro."""
    try:
        yield
    except OllamaIndisponivel as erro:
        print(f"\nERRO: {erro}")
        sys.exit(2)


def verificar_ollama(modelos=None):
    """Verifica Ollama."""
    try:
        instalados = [m.model for m in cliente_ollama().list().models]
    except _ERROS_CONEXAO as erro:
        raise _erro_ollama(erro) from None
    modelos = modelos or [config.MODELO_EMBEDDING, config.MODELO_CHAT]
    faltando = [m for m in modelos if not any(i == m or i == f"{m}:latest" for i in instalados)]
    return instalados, faltando



def validar_metadados(linhas, cabecalho, pasta=None):
    """Valida metadados."""
    pasta = Path(pasta or config.PASTA_ARTIGOS)
    erros = []
    if cabecalho != config.COLUNAS_METADADOS:
        erros.append(f"Cabeçalho {cabecalho} diferente de {config.COLUNAS_METADADOS}")
    no_csv = {linha["arquivo"] for linha in linhas}
    na_pasta = {p.name for p in pasta.glob("*.pdf")}
    erros += [f"Linha sem PDF: {nome}" for nome in sorted(no_csv - na_pasta)]
    erros += [f"PDF sem linha no CSV: {nome}" for nome in sorted(na_pasta - no_csv)]
    for linha in linhas:
        if linha["tema"] not in config.TEMAS:
            erros.append(f"{linha['arquivo']}: tema '{linha['tema']}' fora de {config.TEMAS}")
        if linha["idioma"] not in config.IDIOMAS:
            erros.append(f"{linha['arquivo']}: idioma '{linha['idioma']}' fora de {config.IDIOMAS}")
        if not str(linha["ano"]).isdigit():
            erros.append(f"{linha['arquivo']}: ano '{linha['ano']}' não é inteiro")
    return erros


def extrair_abstract(texto_pagina_1):
    """Extrai abstract."""
    padrao = re.compile(
        r"\b(?:abstract|resumo)\b\s*[—:.\-]?\s*(.+?)"
        r"(?=\n\s*(?:\d\.?\s*)?(?:introduction|introdução|keywords|palavras-chave|index terms)\b|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    achado = padrao.search(texto_pagina_1)
    if not achado:
        return ""
    return limpar_texto(achado.group(1))[:3000]




def gerar_embeddings(textos, modelo=None, lote=16):
    """Gera embeddings."""
    modelo = modelo or config.MODELO_EMBEDDING
    # why: o Ollama rejeita entrada vazia, e o SHAP gera perguntas totalmente mascaradas.
    textos = [t if t.strip() else "." for t in textos]
    vetores = []
    try:
        for i in range(0, len(textos), lote):
            vetores += cliente_ollama().embed(model=modelo, input=textos[i:i + lote]).embeddings
    except _ERROS_CONEXAO as erro:
        raise _erro_ollama(erro, modelo) from None
    return vetores


def abrir_colecao(recriar=False):
    """Abre coleção."""
    cliente = chromadb.PersistentClient(path=str(config.PASTA_CHROMA))
    if recriar and config.NOME_COLECAO in [c.name for c in cliente.list_collections()]:
        cliente.delete_collection(config.NOME_COLECAO)
    # why: embedding_function=None impede o Chroma de baixar o modelo padrão dele; os vetores vêm do Ollama.
    return cliente.get_or_create_collection(
        name=config.NOME_COLECAO,
        embedding_function=None,
        metadata={"hnsw:space": "cosine", "modelo_embedding": config.MODELO_EMBEDDING},
    )


def indexar(chunks=None, progresso=print):
    """Indexa valor do fluxo."""
    chunks = chunks or gerar_chunks()
    colecao = abrir_colecao(recriar=True)
    lote = 64
    for i in range(0, len(chunks), lote):
        parte = chunks[i:i + lote]
        colecao.add(
            ids=[c["id"] for c in parte],
            documents=[c["texto"] for c in parte],
            metadatas=[c["metadados"] for c in parte],
            embeddings=gerar_embeddings([c["texto"] for c in parte]),
        )
        if progresso:
            progresso(f"  {min(i + lote, len(chunks))}/{len(chunks)} chunks indexados")
    return colecao


def combinar_filtros(*condicoes):
    """Combina filtros."""
    condicoes = [c for c in condicoes if c]
    if not condicoes:
        return None
    return condicoes[0] if len(condicoes) == 1 else {"$and": condicoes}


def _consultar(colecao, vetor, k, where):
    """Consulta valor do fluxo."""
    resposta = colecao.query(
        query_embeddings=[vetor], n_results=k, where=where,
        include=["documents", "metadatas", "distances"],
    )
    resultados = []
    for posicao, (texto, meta, distancia) in enumerate(
        zip(resposta["documents"][0], resposta["metadatas"][0], resposta["distances"][0]), start=1
    ):
        resultados.append({"posicao": posicao, "texto": texto, "distancia": distancia,
                           "similaridade": 1 - distancia, **meta})
    return resultados


def buscar(pergunta, k=None, where=None, colecao=None, vetor=None):
    """Busca valor do fluxo."""
    colecao = colecao or abrir_colecao()
    vetor = vetor or gerar_embeddings([pergunta])[0]
    filtro = combinar_filtros({"tipo_chunk": "pagina"}, where)
    return _consultar(colecao, vetor, k or config.K_PADRAO, filtro)


def buscar_dois_estagios(pergunta, k=None, n_artigos=None, where=None, colecao=None):
    """Busca dois estágios."""
    colecao = colecao or abrir_colecao()
    vetor = gerar_embeddings([pergunta])[0]
    n_artigos = n_artigos or config.N_ARTIGOS_ESTAGIO_1
    artigos = _consultar(colecao, vetor, n_artigos, combinar_filtros({"tipo_chunk": "resumo"}, where))
    # hazard: a busca vetorial do ChromaDB é sempre por vizinho mais próximo — sem um limiar de
    # distância, "nenhum resumo relevante" nunca acontece por conta própria (achado 4.4): uma
    # pergunta totalmente fora da base ainda devolve os 3 resumos menos distantes, só que longe.
    sem_correspondencia = not artigos or artigos[0]["distancia"] > config.DISTANCIA_MAXIMA_ESTAGIO_1
    if sem_correspondencia:
        motivo = ("nenhum resumo com esse filtro" if not artigos else
                  f"resumo mais próximo está a distância {artigos[0]['distancia']:.4f}, "
                  f"acima do limiar {config.DISTANCIA_MAXIMA_ESTAGIO_1}")
        return {
            "caminho": f"busca simples (estágio 1 sem correspondência: {motivo})",
            "artigos": artigos,
            "resultados": buscar(pergunta, k, where, colecao, vetor),
        }
    filtro = {"arquivo": {"$in": [a["arquivo"] for a in artigos]}}
    return {
        "caminho": "dois estágios",
        "artigos": artigos,
        "resultados": buscar(pergunta, k, combinar_filtros(where, filtro), colecao, vetor),
    }


def tabela_resultados(resultados, largura_trecho=90):
    """Descreve tabela resultados."""
    linhas = []
    for r in resultados:
        trecho = r["texto"][:largura_trecho].replace("\n", " ")
        linhas.append(f"{r['posicao']:>2}. dist={r['distancia']:.4f} | {r['arquivo']} p.{r['pagina']} "
                      f"| {r['ano']} {r['tema']} {r['idioma']} | {trecho}…")
    return "\n".join(linhas) if linhas else "(nenhum resultado)"


INSTRUCOES_SISTEMA = (
    "Você é um assistente que responde em português do Brasil usando SOMENTE os trechos fornecidos pelo usuário. "
    "Os trechos podem estar em inglês: traduza e explique em português. "
    f"Se a resposta não estiver nos trechos, responda exatamente: \"{config.RESPOSTA_NAO_ENCONTRADA}\" "
    "Cite a fonte de cada informação com o número do trecho entre colchetes, por exemplo [1]."
)


def montar_prompt(pergunta, resultados):
    """Monta prompt."""
    trechos = "\n\n".join(
        f"[{i}] ({r['arquivo']}, p. {r['pagina']})\n{r['texto']}" for i, r in enumerate(resultados, start=1)
    ) or "(nenhum trecho recuperado)"
    return f"Trechos:\n{trechos}\n\nPergunta: {pergunta}"


def montar_prompt_sem_contexto(pergunta):
    """Monta prompt sem contexto."""
    return f"Responda em português, de forma direta.\n\nPergunta: {pergunta}"


def montar_mensagens(pergunta, resultados=None):
    """Monta mensagens."""
    if resultados is None:
        return [{"role": "user", "content": montar_prompt_sem_contexto(pergunta)}]
    return [{"role": "system", "content": INSTRUCOES_SISTEMA},
            {"role": "user", "content": montar_prompt(pergunta, resultados)}]


def formatar_mensagens(mensagens):
    """Formata mensagens."""
    return "\n\n".join(f"=== {m['role'].upper()} ===\n{m['content']}" for m in mensagens)


def _opcoes(max_tokens=None):
    """Auxilia opções."""
    return {"temperature": config.TEMPERATURA, "seed": 42,
            "num_predict": max_tokens or config.MAX_TOKENS_RESPOSTA}


# why: devolve a resposta bruta do Ollama (load_duration, prompt_eval_count…) para quem precisa medir,
# em vez de forçar esse chamador a tocar cliente_ollama()/_opcoes() diretamente (achado 7.4, medir.py).
def chat(mensagens, modelo=None, max_tokens=None):
    """Descreve chat."""
    modelo = modelo or config.MODELO_CHAT
    if isinstance(mensagens, str):
        mensagens = [{"role": "user", "content": mensagens}]
    try:
        return cliente_ollama().chat(model=modelo, messages=mensagens, options=_opcoes(max_tokens))
    except _ERROS_CONEXAO as erro:
        raise _erro_ollama(erro, modelo) from None


def gerar_texto(mensagens, modelo=None, max_tokens=None):
    """Gera texto."""
    return chat(mensagens, modelo, max_tokens).message.content.strip()


def formatar_fontes(resultados, indices=None):
    """Formata fontes."""
    indices = indices if indices is not None else range(1, len(resultados) + 1)
    return "\n".join(f"[{i}] {r['arquivo']}, p. {r['pagina']}" for i, r in zip(indices, resultados))


_CITACAO_RE = re.compile(r"\[(\d+)\]")
_ESPACOS_RE = re.compile(r"\s+")


def indices_citados(texto, n):
    """Descreve indices citados."""
    vistos, ordem = set(), []
    for m in _CITACAO_RE.finditer(texto):
        i = int(m.group(1))
        if 1 <= i <= n and i not in vistos:
            vistos.add(i)
            ordem.append(i)
    return ordem


def eh_recusa(texto):
    # normaliza espaços (múltiplos → um), remove citações [n] e pontuação repetida antes de comparar,
    # para reconhecer a recusa mesmo quando o modelo varia o espaçamento ou cita uma fonte por engano
    # (achado 6.5: comparação exata perdia esses casos).
    """Descreve é Recusa."""
    sem_citacoes = _CITACAO_RE.sub("", texto)
    sem_pontuacao_dupla = re.sub(r"([.,;:!?])\1+", r"\1", sem_citacoes)
    normalizado = _ESPACOS_RE.sub(" ", sem_pontuacao_dupla).strip()
    referencia = _ESPACOS_RE.sub(" ", config.RESPOSTA_NAO_ENCONTRADA).strip()
    return normalizado.startswith(referencia)


def fontes_da_resposta(texto, resultados):
    # hazard: listar os k trechos recuperados como "fontes" mistura o que entrou no prompt com o
    # que a resposta de fato usou (achado 6.5) — aqui só entram os [n] que aparecem no texto
    # gerado; se o modelo não citou nenhum, cai para os recuperados, para nunca ficar sem fontes;
    # e nenhuma fonte é listada quando a resposta é uma recusa.
    """Descreve fontes da resposta."""
    if not resultados or eh_recusa(texto):
        return []
    indices = indices_citados(texto, len(resultados)) or list(range(1, len(resultados) + 1))
    return [(i, resultados[i - 1]) for i in indices]


def montar_bloco_fontes(texto, resultados):
    # why: único lugar que monta o bloco "Fontes:" pronto para exibição — responder() e os scripts
    # que também mostram fontes (ex.: scripts/06) chamam isto em vez de repetir o zip/formatar_fontes
    # cada um por conta própria (mesmo achado 6.5 de duplicação que fontes_da_resposta já resolveu).
    """Monta bloco fontes."""
    fontes = fontes_da_resposta(texto, resultados)
    if not fontes:
        return ""
    indices, citados = zip(*fontes)
    return "\n\nFontes:\n" + formatar_fontes(list(citados), list(indices))


def responder(pergunta, resultados=None, modelo=None, incluir_fontes=True):
    """Responde valor do fluxo."""
    modelo = modelo or config.MODELO_CHAT
    texto = ""
    try:
        for pedaco in cliente_ollama().chat(model=modelo, messages=montar_mensagens(pergunta, resultados),
                                            options=_opcoes(), stream=True):
            texto += pedaco.message.content
            yield pedaco.message.content
    except _ERROS_CONEXAO as erro:
        raise _erro_ollama(erro, modelo) from None
    if incluir_fontes:
        bloco = montar_bloco_fontes(texto, resultados)
        if bloco:
            yield bloco


def resumir_abstract(abstract, idioma, modelo=None):
    """Resume abstract."""
    if idioma == "en":
        instrucao = "Summarize the abstract below in 2 to 3 sentences, in English. Reply with the summary only."
    else:
        instrucao = "Resuma o abstract abaixo em 2 a 3 frases, em português. Responda apenas com o resumo."
    return gerar_texto(f"{instrucao}\n\nAbstract:\n{abstract}", modelo=modelo, max_tokens=200)


def extrair_metadados_llm(texto_pagina_1, modelo=None):
    """Extrai metadados LLM."""
    modelo = modelo or config.MODELO_CHAT
    prompt = (
        "Extraia os metadados do artigo científico a partir do texto da primeira página abaixo.\n"
        "Responda SOMENTE com um JSON com as chaves: titulo, autores (nomes separados por '; '), "
        f"ano (inteiro), veiculo, tema (uma de {config.TEMAS}), idioma (uma de {config.IDIOMAS}).\n\n"
        f"Texto:\n{texto_pagina_1[:4000]}"
    )
    try:
        resposta = cliente_ollama().generate(model=modelo, prompt=prompt, format="json", options=_opcoes(300))
    except _ERROS_CONEXAO as erro:
        raise _erro_ollama(erro, modelo) from None
    try:
        return json.loads(resposta.response)
    except json.JSONDecodeError:
        return {"erro": "o modelo não devolveu JSON válido", "bruto": resposta.response}


def _normalizar(valor):
    """Auxilia normalizar."""
    return re.sub(r"\s+", " ", str(valor)).strip().lower()


def comparar_metadados(manual, extraido, campos=("titulo", "autores", "ano", "veiculo", "tema", "idioma")):
    """Compara metadados."""
    return [{"campo": campo, "csv": manual.get(campo), "llm": extraido.get(campo),
             "igual": _normalizar(manual.get(campo)) == _normalizar(extraido.get(campo))} for campo in campos]


def similaridade_cosseno(a, b):
    """Descreve similaridade cosseno."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def explicar_similaridade(pergunta, texto_chunk, max_evals=200):
    """Explica similaridade."""
    import shap

    alvo = np.asarray(gerar_embeddings([texto_chunk])[0], dtype=float)

    def funcao(perguntas):
        """Descreve função."""
        vetores = np.asarray(gerar_embeddings([str(p) for p in perguntas]), dtype=float)
        return vetores @ alvo / (np.linalg.norm(vetores, axis=1) * np.linalg.norm(alvo))

    explicador = shap.Explainer(funcao, shap.maskers.Text(r"\W+"))
    return explicador([pergunta], max_evals=max_evals, silent=True), funcao


def shapley_chunks(pergunta, resultados, modelo=None, progresso=print):
    """Descreve shapley chunks."""
    n = len(resultados)
    respostas = {}

    def resposta_de(indices):
        """Descreve resposta de."""
        if indices not in respostas:
            respostas[indices] = gerar_texto(montar_mensagens(pergunta, [resultados[i] for i in indices]),
                                             modelo=modelo, max_tokens=200)
            if progresso:
                progresso(f"  coalizão {list(indices)} ({len(respostas)}/{2 ** n})")
        return respostas[indices]

    todos = tuple(range(n))
    referencia = gerar_embeddings([resposta_de(todos)])[0]
    valores = {}
    for tamanho in range(n + 1):
        for indices in combinations(range(n), tamanho):
            valores[indices] = similaridade_cosseno(gerar_embeddings([resposta_de(indices)])[0], referencia)

    contribuicoes = []
    for i in range(n):
        phi = 0.0
        outros = [j for j in range(n) if j != i]
        for tamanho in range(n):
            peso = math.factorial(tamanho) * math.factorial(n - tamanho - 1) / math.factorial(n)
            for s in combinations(outros, tamanho):
                phi += peso * (valores[tuple(sorted(s + (i,)))] - valores[s])
        contribuicoes.append({"chunk": i + 1, "arquivo": resultados[i]["arquivo"],
                              "pagina": resultados[i]["pagina"], "shapley": phi})
    return {
        "pergunta": pergunta,
        "modelo": modelo or config.MODELO_CHAT,
        "valor_sem_chunks": valores[()],
        "valor_com_todos": valores[todos],
        "contribuicoes": contribuicoes,
        "respostas": {",".join(map(str, k)) or "nenhum": v for k, v in respostas.items()},
    }
