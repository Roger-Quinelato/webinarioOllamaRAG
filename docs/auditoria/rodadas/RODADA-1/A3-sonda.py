"""Sonda do eixo A3 (material didático) — RODADA-1.

Só leitura sobre o projeto. NÃO chama o Ollama, NÃO reindexa, NÃO reexecuta o notebook:
lê o `webinario_rag.ipynb` salvo como JSON, mede o chunking (que é PDF puro, sem LLM) e
exercita o ChromaDB numa coleção temporária dentro da pasta de sonda.

Uso:
    .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py
"""
import json
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

import chromadb  # noqa: E402

import config  # noqa: E402
import rag  # noqa: E402

NB = RAIZ / "webinario_rag.ipynb"
NB_OFF = RAIZ / "docs" / "evidencias" / "E7" / "webinario_rag_offline.ipynb"
CONSTRUTOR = RAIZ / "ferramentas" / "construir_notebook.py"


def celulas(caminho):
    nb = json.loads(Path(caminho).read_text(encoding="utf-8"))
    return nb["cells"], [c for c in nb["cells"] if c["cell_type"] == "code"]


def saida(celula):
    partes = []
    for o in celula.get("outputs", []):
        if o.get("output_type") == "stream":
            partes.append("".join(o.get("text", [])))
        elif o.get("output_type") in ("execute_result", "display_data"):
            d = o.get("data", {})
            for chave in ("text/markdown", "text/plain"):
                if chave in d:
                    partes.append("".join(d[chave]))
                    break
        elif o.get("output_type") == "error":
            partes.append("ERRO " + o.get("ename", ""))
    return "\n".join(partes)


print("=" * 100)
print("A3-01 — artigos citados no notebook (markdown do bloco 2.1) x config.ARTIGOS_CORPUS")
print("=" * 100)
md_todas = "\n".join("".join(c["source"]) for c, in zip(celulas(NB)[0]) if c["cell_type"] == "markdown")
for nome in config.ARTIGOS_CORPUS:
    print(f"  {nome:<34} citado no notebook: {nome in md_todas}")
print(f"  config.ARTIGOS_CORPUS tem {len(config.ARTIGOS_CORPUS)} artigos; "
      f"metadados.csv tem {len(rag.carregar_metadados())} linhas")
fonte = CONSTRUTOR.read_text(encoding="utf-8")
print(f"  ocorrências de 'arxiv.org' em construir_notebook.py: {fonte.count('arxiv.org')}")
print(f"  ocorrências de 'sol.sbc.org.br' em construir_notebook.py: {fonte.count('sol.sbc.org.br')}")

print()
print("=" * 100)
print("A3-02 — bloco 5: 'Fontes citadas' x 'Trechos enviados ao prompt' na saída salva")
print("=" * 100)
_, codigo = celulas(NB)
for indice, celula in enumerate(codigo):
    texto = saida(celula)
    if "**Fontes citadas**" in texto and "**Trechos enviados ao prompt**" in texto:
        bloco_citadas = re.search(r"\*\*Fontes citadas\*\*\n```\n(.*?)\n```", texto, re.S).group(1)
        bloco_enviados = re.search(r"\*\*Trechos enviados ao prompt\*\*\n```\n(.*?)\n```", texto, re.S).group(1)
        resposta = re.search(r"### Com contexto\n(.*?)\n\n\*\*Fontes citadas", texto, re.S)
        citacoes = re.findall(r"\[(\d+)\]", resposta.group(1)) if resposta else []
        print(f"  célula de código #{indice} (execution_count={celula.get('execution_count')})")
        print(f"    citações [n] na resposta 'Com contexto': {citacoes or 'NENHUMA'}")
        print(f"    'Fontes citadas'            = {bloco_citadas.splitlines()}")
        print(f"    'Trechos enviados ao prompt'= {bloco_enviados.splitlines()}")
        print(f"    os dois blocos são idênticos? {bloco_citadas == bloco_enviados}")
for indice, celula in enumerate(codigo):
    texto = saida(celula)
    if "Fontes:\n[" in texto and "Trechos enviados ao prompt" in texto:
        fontes = re.search(r"Fontes:\n((?:\[\d+\].*\n?)+)", texto).group(1).strip().splitlines()
        enviados = re.search(r"\*\*Trechos enviados ao prompt\*\*\n```\n(.*?)\n```", texto, re.S).group(1).splitlines()
        print(f"  célula de código #{indice} (bloco 6, execution_count={celula.get('execution_count')})")
        print(f"    'Fontes:' (citadas)         = {fontes}")
        print(f"    'Trechos enviados ao prompt'= {enviados}")
        print(f"    os dois blocos são idênticos? {fontes == enviados}")

print()
print("=" * 100)
print("A3-03 — tempos salvos no .ipynb (extração independente do verificar.py e7_saidas)")
print("=" * 100)
padroes = {
    "bloco 2.4 extração de metadados por LLM": r"Extração em ([\d.]+)s",
    "bloco 2.5 resumo ao vivo": r"RESUMO AO VIVO \(([\d.]+)s\)",
    "bloco 4 SHAP ao vivo": r"SHAP em ([\d.]+)s",
    "bloco 6 resposta em streaming": r"\[([\d.]+)s com ([\w.:]+)\]",
}
tudo = "\n".join(saida(c) for c in codigo)
for rotulo, padrao in padroes.items():
    print(f"  {rotulo:<42} {re.findall(padrao, tudo)}")
print("  modelo de chat anunciado no bloco 1:", re.findall(r"Chat: (\S+)", tudo))
print("  modelo do Shapley pré-computado (bloco 4.1):", re.findall(r"modelo: (\S+)", tudo))

print()
print("=" * 100)
print("A3-04 — rede de segurança: arquivos de resultados/ lidos pelo notebook")
print("=" * 100)
for nome in sorted(set(re.findall(r'carregar_resultado\("([^"]+)"\)', fonte))
                   | set(re.findall(r'PASTA_RESULTADOS / "([^"]+)"', fonte))):
    caminho = config.PASTA_RESULTADOS / nome
    if caminho.exists():
        conteudo = caminho.read_text(encoding="utf-8")
        modelo = re.search(r'"modelo":\s*"([^"]+)"', conteudo)
        print(f"  {nome:<36} existe | {caminho.stat().st_size:>6} bytes | "
              f"mtime={time.strftime('%Y-%m-%d %H:%M', time.localtime(caminho.stat().st_mtime))} | "
              f"modelo={modelo.group(1) if modelo else '—'}")
    else:
        print(f"  {nome:<36} AUSENTE")

print()
print("=" * 100)
print("A3-05 — células que continuam exigindo o Ollama mesmo com LLM_AO_VIVO/SHAP_AO_VIVO = False")
print("=" * 100)
chamadas = ("rag.buscar(", "rag.buscar_dois_estagios(", "rag.indexar(", "rag.gerar_chunks(",
            "rag.resumir_abstract(", "rag.extrair_metadados_llm(", "rag.gerar_texto(",
            "rag.responder(", "rag.explicar_similaridade(", "rag.verificar_ollama(")
precisa_embedding = ("rag.buscar(", "rag.buscar_dois_estagios(", "rag.indexar(")
for indice, celula in enumerate(codigo):
    src = "".join(celula["source"])
    if not any(c in src for c in precisa_embedding):
        continue
    tem_guarda = "LLM_AO_VIVO" in src or "SHAP_AO_VIVO" in src
    dentro_da_guarda = []
    fora_da_guarda = []
    guardando = False
    for linha in src.splitlines():
        if re.match(r"\s*(if|elif)\b.*(LLM_AO_VIVO|SHAP_AO_VIVO)", linha):
            guardando = True
        elif linha and not linha.startswith((" ", "\t")) and not linha.startswith("else"):
            guardando = False
        if any(c in linha for c in precisa_embedding):
            (dentro_da_guarda if guardando else fora_da_guarda).append(linha.strip()[:72])
    print(f"  célula #{indice} (tem chave LLM_AO_VIVO/SHAP_AO_VIVO: {tem_guarda})")
    for linha in fora_da_guarda:
        print(f"      FORA da chave  -> {linha}")
    for linha in dentro_da_guarda:
        print(f"      dentro da chave-> {linha}")
print("  (todas as linhas 'FORA da chave' chamam rag.gerar_embeddings() e portanto o Ollama)")

print()
print("=" * 100)
print("A3-06 — chunking (bloco 2.2/2.3) medido duas vezes; sem Ollama, só leitura dos PDFs")
print("=" * 100)
for tentativa in (1, 2):
    inicio = time.perf_counter()
    chunks = rag.gerar_chunks()
    print(f"  tentativa {tentativa}: {len(chunks)} chunks em {time.perf_counter() - inicio:.1f}s")
pagina = rag.extrair_paginas(config.PASTA_ARTIGOS / "lewis2020_rag.pdf")[2]
inicio = time.perf_counter()
partes = rag.dividir_texto(pagina)
print(f"  dividir_texto(página 3 do lewis2020): {len(partes)} partes em {time.perf_counter() - inicio:.3f}s")

print()
print("=" * 100)
print("A3-07 — scripts/03–05 rodados ANTES do scripts/02 (coleção vazia): erro ou silêncio?")
print("=" * 100)
temporaria = Path(tempfile.mkdtemp(prefix="a3-sonda-chroma-"))
try:
    cliente = chromadb.PersistentClient(path=str(temporaria))
    vazia = cliente.get_or_create_collection(name="artigos_rag", embedding_function=None,
                                             metadata={"hnsw:space": "cosine"})
    print(f"  coleção recém-criada: {vazia.count()} vetores")
    vetor = [0.0] * 1024
    for rotulo, where in (("buscar (tipo_chunk=pagina)", {"tipo_chunk": "pagina"}),
                          ("estágio 1 (tipo_chunk=resumo)", {"tipo_chunk": "resumo"})):
        try:
            saida_consulta = rag._consultar(vazia, vetor, 4, where)
            print(f"  {rotulo:<30} -> {len(saida_consulta)} resultados, sem exceção")
        except Exception as erro:  # noqa: BLE001
            print(f"  {rotulo:<30} -> EXCEÇÃO {type(erro).__name__}: {erro}")
    print(f"  rag.tabela_resultados([])            -> {rag.tabela_resultados([])!r}")
    print(f"  rag.montar_prompt('p', [])[:60]      -> {rag.montar_prompt('p', [])[:60]!r}")
    print(f"  rag.fontes_da_resposta('texto', [])  -> {rag.fontes_da_resposta('texto', [])}")
    print("  (scripts/05_shap.py itera sobre rag.buscar(...); com 0 resultados o laço não executa,")
    print("   nenhum shap_similaridade_chunkN.* é escrito e o script sai com 0)")
finally:
    shutil.rmtree(temporaria, ignore_errors=True)

print()
print("=" * 100)
print("A3-08 — gatilho automático de reindexação na célula do bloco 2.3")
print("=" * 100)
celula_indice = next(c for c in codigo if "colecao = rag.abrir_colecao()" in "".join(c["source"]))
for linha in "".join(celula_indice["source"]).splitlines()[:4]:
    print(f"  {linha}")
print("  REINDEXAR na célula de configuração:",
      re.findall(r"REINDEXAR = (\w+)", "".join(codigo[0]["source"])))
print("  -> com REINDEXAR=False, rag.indexar() ainda dispara se colecao.count() != len(chunks)")

print()
print("=" * 100)
print("A3-09 — bloco 5 offline: casamento exato da pergunta com resultados/com_sem_contexto.json")
print("=" * 100)
pergunta_nb = re.search(r'# TODO\(autor\): trocar pela pergunta-teste definitiva\.\npergunta = "([^"]+)"',
                        fonte).group(1)
salvas = [r["pergunta"] for r in json.loads(
    (config.PASTA_RESULTADOS / "com_sem_contexto.json").read_text(encoding="utf-8"))]
print(f"  pergunta do notebook (bloco 5): {pergunta_nb!r}")
print(f"  perguntas em com_sem_contexto.json: {salvas}")
print(f"  casa exatamente? {pergunta_nb in salvas}")
print("  (a célula usa next(r for r in ... if r['pergunta'] == pergunta): sem casamento -> StopIteration)")

print()
print("=" * 100)
print("A3-10 — notebook ao vivo x cópia --offline: as saídas conferem?")
print("=" * 100)
_, codigo_off = celulas(NB_OFF)
print(f"  células de código: ao vivo={len(codigo)} offline={len(codigo_off)}")
for indice in range(min(len(codigo), len(codigo_off))):
    viva, morta = saida(codigo[indice]), saida(codigo_off[indice])
    marca = "=" if viva.strip() == morta.strip() else "≠"
    if marca == "≠":
        print(f"  #{indice} {marca} ao vivo {len(viva):>5} chars | offline {len(morta):>5} chars | "
              f"{''.join(codigo[indice]['source']).splitlines()[0][:52]!r}")
