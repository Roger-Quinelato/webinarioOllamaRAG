"""Sonda do eixo A2 (Verificação e evidências) — RODADA-1.

Só leitura. Nenhuma chamada ao Ollama (nem embedding, nem chat): os blocos que tocam dados
reais leem apenas o ChromaDB já persistido, arquivos de texto e o AST de ferramentas/verificar.py.

Uso:
    .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A2-sonda.py
"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

EVID = RAIZ / "docs" / "evidencias"


def cabecalho(titulo):
    """Descreve cabecalho."""
    print(f"\n== {titulo} ==")


# ---------------------------------------------------------------- A2-01
def a2_01_indice_atual_vs_evidencia_e2():
    """Estado real da coleção hoje × o que docs/evidencias/E2/*.txt afirma.

    Duas medições independentes da mesma grandeza (count() da API × len(ids) de um get()),
    para não reportar um número vindo de uma leitura só.
    """
    cabecalho("A2-01 índice atual × evidência de E2")
    import rag  # noqa: E402  (import tardio: só aqui precisamos do chromadb)

    colecao = rag.abrir_colecao()
    medicao_1 = colecao.count()
    dados = colecao.get(include=["metadatas"])
    medicao_2 = len(dados["ids"])
    tipos = {}
    artigos = set()
    for m in dados["metadatas"]:
        tipos[m["tipo_chunk"]] = tipos.get(m["tipo_chunk"], 0) + 1
        artigos.add(m["arquivo"])
    print(f"  medição 1 (colecao.count())      = {medicao_1}")
    print(f"  medição 2 (len(get()['ids']))    = {medicao_2}")
    print(f"  por tipo_chunk                   = {tipos}")
    print(f"  artigos distintos                = {len(artigos)}")

    for nome in ("E2/verificacao_E2.txt", "E2/reverificacao_e2.txt"):
        texto = (EVID / nome).read_text(encoding="utf-8")
        total = re.search(r"2\.2 total de chunks: (\d+)", texto)
        por_tipo = re.search(r"2\.3 por tipo_chunk: (\{[^}]*\})", texto)
        print(f"  {nome}: total={total.group(1) if total else '?'} por_tipo={por_tipo.group(1) if por_tipo else '?'}")


# ---------------------------------------------------------------- A2-02
def a2_02_e9_numeros_confirma_numero_velho():
    """e9_numeros confere medicoes.md contra E7/saidas_notebook.txt, que é append-only.

    Testa com DUAS entradas diferentes: os números do T09 (36 / 70,6), que o próprio
    docs/evidencias/E9/reconciliacao_numeros.txt registra como "DEPOIS" correto, e os
    do pré-T10 (94 / 163,8), que o mesmo arquivo registra como o erro que a checagem
    foi criada para pegar.
    """
    cabecalho("A2-02 e9_numeros × histórico acumulado de saidas_notebook.txt")
    saidas = (EVID / "E7" / "saidas_notebook.txt").read_text(encoding="utf-8")
    medicoes = (RAIZ / "docs" / "medicoes.md").read_text(encoding="utf-8")
    padrao = re.compile(r"(\d+(?:[.,]\d+)?)\s*s\s*na última execução do notebook")
    print(f"  medicoes.md hoje afirma: {padrao.findall(medicoes)}")
    for numero in ("36", "70,6", "94", "163,8", "48", "34", "50", "190,7", "17,9"):
        normalizado = numero.replace(",", ".")
        casos = re.findall(rf"(?<!\d){re.escape(normalizado)}s\b", saidas)
        print(f"  '{numero}s' seria CONFIRMADO por saidas_notebook.txt? {bool(casos)} ({len(casos)} ocorrência(s))")
    marcadores = [l for l in saidas.splitlines() if l.startswith("# ") or "células do notebook" in l]
    print(f"  blocos acumulados no arquivo (marcadores): {len(marcadores)}")
    for l in marcadores[:12]:
        print(f"    {l[:110]}")


# ---------------------------------------------------------------- A2-03
def a2_03_checagens_que_nunca_reprovam():
    """Quais funções eN de verificar.py podem sair com código != 0?

    Duas leituras independentes do mesmo fato: AST (procura chamadas a sys.exit/raise/assert
    no corpo da função) e varredura textual do bloco de linhas da função.
    """
    cabecalho("A2-03 funções de verificar.py que não têm como reprovar")
    origem = (RAIZ / "ferramentas" / "verificar.py").read_text(encoding="utf-8")
    linhas = origem.splitlines()
    arvore = ast.parse(origem)
    for no in arvore.body:
        if not isinstance(no, ast.FunctionDef) or no.name.startswith("_"):
            continue
        por_ast = False
        for filho in ast.walk(no):
            if isinstance(filho, ast.Raise) or isinstance(filho, ast.Assert):
                por_ast = True
            if (isinstance(filho, ast.Call) and isinstance(filho.func, ast.Attribute)
                    and filho.func.attr == "exit"):
                por_ast = True
        bloco = "\n".join(linhas[no.lineno - 1:no.end_lineno])
        por_texto = bool(re.search(r"sys\.exit|raise |assert ", bloco))
        chama_auxiliar = bool(re.search(r"_autoteste_escolher_limiar\(", bloco))
        print(f"  {no.name:32s} pode_reprovar_ast={por_ast!s:5} pode_reprovar_texto={por_texto!s:5} "
              f"(via auxiliar: {chama_auxiliar})")


# ---------------------------------------------------------------- A2-04
def a2_04_e2_reabrir_nao_compara_nada():
    """e2_reabrir imprime o stdout de um subprocesso e nunca compara nem reprova.

    Reproduz o mesmo padrão com um subprocesso que FALHA, para mostrar que a saída
    continuaria parecendo uma linha de evidência normal.
    """
    cabecalho("A2-04 e2_reabrir com subprocesso que falha")
    for rotulo, codigo in (("subprocesso OK", "print(659)"),
                           ("subprocesso quebrado", "raise SystemExit('boom')")):
        saida = subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, capture_output=True, text=True)
        # mesma linha de print que ferramentas/verificar.py:87 produz
        print(f"  [{rotulo}] returncode={saida.returncode} → linha impressa por e2_reabrir seria:")
        print(f"      2.6 contagem em outro processo: {saida.stdout.strip()} {saida.stderr.strip()[-60:]}")


# ---------------------------------------------------------------- A2-05
def a2_05_exit_de_scripts_00_com_ollama_fora():
    """docs/evidencias/E6/ollama_desligado.txt anota 'exit=0' para execuções que falham.

    Reexecuta scripts/00_checar_ambiente.py apontando para uma porta morta (nenhum
    contato com o Ollama real) e mostra o código de saída verdadeiro.
    """
    cabecalho("A2-05 código de saída real de scripts/00 com o Ollama inalcançável")
    ambiente = {**os.environ, "OLLAMA_HOST": "http://localhost:11999", "PYTHONIOENCODING": "utf-8"}
    saida = subprocess.run([sys.executable, str(RAIZ / "scripts" / "00_checar_ambiente.py")],
                           cwd=RAIZ, capture_output=True, text=True, env=ambiente, timeout=120)
    ultimas = [l for l in saida.stdout.splitlines() if l.strip()][-2:]
    print(f"  últimas linhas: {ultimas}")
    print(f"  returncode real = {saida.returncode}")
    trecho = (EVID / "E6" / "ollama_desligado.txt").read_text(encoding="utf-8")
    print("  o que a evidência E6/ollama_desligado.txt anota:")
    for l in trecho.splitlines():
        if l.startswith("exit=") or "falharam" in l:
            print(f"    {l}")


# ---------------------------------------------------------------- A2-06
def a2_06_arquivos_citados_em_verificacao():
    """Todo caminho docs/evidencias/... citado em VERIFICACAO.md existe no disco?"""
    cabecalho("A2-06 arquivos de evidência citados em VERIFICACAO.md")
    texto = (RAIZ / "docs" / "VERIFICACAO.md").read_text(encoding="utf-8")
    citados = sorted(set(re.findall(r"(?:docs/)?evidencias/[\w./-]+", texto)))
    for caminho in citados:
        rel = caminho.split("evidencias/", 1)[1]
        alvo = EVID / rel
        print(f"  {caminho:70s} existe={alvo.exists()}")


# ---------------------------------------------------------------- A2-07
def a2_07_cobertura_do_e6_ollama_desligado_scripts():
    """Quais scripts o glob de e6_ollama_desligado_scripts alcança, e quais ficam de fora."""
    cabecalho("A2-07 cobertura do glob de e6_ollama_desligado_scripts")
    alvos = [*sorted((RAIZ / "scripts").glob("0[3-7]_*.py")), *sorted((RAIZ / "opcional").glob("*.py"))]
    todos = [*sorted((RAIZ / "scripts").glob("*.py")), *sorted((RAIZ / "opcional").glob("*.py"))]
    nomes_alvo = {p.name for p in alvos}
    print(f"  cobertos  : {sorted(nomes_alvo)}")
    print(f"  NÃO cobertos: {sorted(p.relative_to(RAIZ).as_posix() for p in todos if p.name not in nomes_alvo)}")
    for p in todos:
        tem = "cli_seguro" in p.read_text(encoding="utf-8")
        print(f"    {p.relative_to(RAIZ).as_posix():38s} usa rag.cli_seguro()={tem} coberto={p.name in nomes_alvo}")


# ---------------------------------------------------------------- A2-08
def a2_08_rotulos_de_evidencia_x_codigo_atual():
    """Os rótulos impressos hoje por e3/e4 batem com os rótulos gravados na evidência citada?"""
    cabecalho("A2-08 rótulos gravados na evidência × rótulos do código atual")
    codigo = (RAIZ / "ferramentas" / "verificar.py").read_text(encoding="utf-8")
    for rotulo in ("3.6 filtro ano>=2030", "3.6 filtro idioma=pt (sem artigos)",
                   "4.4a estágio 1 vazio (ano>=2030)", "4.4a estágio 1 vazio (idioma=pt)"):
        print(f"  {rotulo!r:55s} presente em verificar.py = {rotulo in codigo}")
    for nome in ("E3/verificacao_E3.txt", "E3/reverificacao_e3.txt",
                 "E4/reverificacao_e4.txt", "E4/reverificacao_e4_v2.txt"):
        texto = (EVID / nome).read_text(encoding="utf-8")
        marcas = [l.strip() for l in texto.splitlines() if l.startswith(("3.6", "4.4"))]
        print(f"  {nome}: {marcas}")


if __name__ == "__main__":
    a2_01_indice_atual_vs_evidencia_e2()
    a2_02_e9_numeros_confirma_numero_velho()
    a2_03_checagens_que_nunca_reprovam()
    a2_04_e2_reabrir_nao_compara_nada()
    a2_05_exit_de_scripts_00_com_ollama_fora()
    a2_06_arquivos_citados_em_verificacao()
    a2_07_cobertura_do_e6_ollama_desligado_scripts()
    a2_08_rotulos_de_evidencia_x_codigo_atual()
