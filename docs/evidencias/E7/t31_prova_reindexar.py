"""Prova que a celula de indexacao do notebook nao reindexa com REINDEXAR = False.

Extrai o codigo da propria celula do webinario_rag.ipynb (nao uma copia), troca a colecao real
por uma duble com contagem divergente e faz rag.indexar explodir se for chamado. Se a condicao
antiga (`or`) voltar, o teste falha barulhento em vez de gastar 23,7 min reindexando.

Uso: .venv/Scripts/python docs/evidencias/E7/t31_prova_reindexar.py
"""
import io
import json
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import rag  # noqa: E402

CHUNKS_ESPERADOS = 659   # o que os PDFs do corpus geram hoje
VETORES_DEFASADOS = 600  # contagem divergente de proposito, para acionar o ramo do aviso
MARCA_FIM_DO_TRECHO = "amostra = colecao.get"


def falhar(mensagem):
    """Falha valor do fluxo."""
    print(f"RESULTADO: FALHOU -- {mensagem}")
    sys.exit(1)


fonte_completa = None
for celula in json.loads((RAIZ / "webinario_rag.ipynb").read_text(encoding="utf-8"))["cells"]:
    texto = "".join(celula["source"])
    if celula["cell_type"] == "code" and "rag.indexar(chunks)" in texto:
        fonte_completa = texto
        break

# hazard: o recorte e o seletor sao acoplados ao texto da celula. Sem estas guardas, uma mudanca de
# forma do bloco faria o caso 1 "passar" por nao levantar excecao, sem ter exercitado nada.
if not fonte_completa:
    falhar("celula de indexacao nao encontrada no notebook")
if MARCA_FIM_DO_TRECHO not in fonte_completa:
    falhar(f"a celula mudou de forma: {MARCA_FIM_DO_TRECHO!r} nao encontrado")
fonte = fonte_completa.split(MARCA_FIM_DO_TRECHO)[0]
for trecho in ("if REINDEXAR:", "elif colecao.count() != len(chunks):", "rag.indexar(chunks)"):
    if trecho not in fonte:
        falhar(f"a celula mudou de forma: {trecho!r} nao esta no trecho sob teste")

print("--- codigo sob teste, extraido de webinario_rag.ipynb ---")
print(fonte)


class ColecaoDuble:
    """Representa Colecao Duble."""
    def __init__(self, quantos):
        """Inicializa instância com dependências e parâmetros."""
        self._quantos = quantos

    def count(self):
        """Descreve count."""
        return self._quantos


class IndexarChamado(Exception):
    """rag.indexar() foi chamado -- a celula decidiu reindexar. Herda de Exception."""


def indexar_proibido(*_, **__):
    """Indexa proibido."""
    raise IndexarChamado("rag.indexar() FOI CHAMADO: a celula decidiu reindexar")


def rodar(reindexar):
    """Executa o trecho da celula e devolve (chamou_indexar, saida_impressa)."""
    escopo = {"rag": rag, "time": time, "REINDEXAR": reindexar, "chunks": list(range(CHUNKS_ESPERADOS))}
    capturada = io.StringIO()
    try:
        with redirect_stdout(capturada):
            exec(compile(fonte, "celula", "exec"), escopo)
        return False, capturada.getvalue()
    except IndexarChamado:
        return True, capturada.getvalue()


indexar_original, abrir_original = rag.indexar, rag.abrir_colecao
try:
    rag.indexar = indexar_proibido
    rag.abrir_colecao = lambda *a, **k: ColecaoDuble(VETORES_DEFASADOS)

    print(f"--- caso 1: REINDEXAR = False com contagem divergente "
          f"({VETORES_DEFASADOS} x {CHUNKS_ESPERADOS}) ---")
    chamou, saida = rodar(reindexar=False)
    print(saida, end="")
    if chamou:
        falhar("reindexou com REINDEXAR = False")
    if "[AVISO]" not in saida:
        falhar("nao reindexou, mas tambem nao avisou: o ramo do aviso nao rodou")
    if "scripts/02_indexar.py" not in saida:
        falhar("o aviso nao diz o que fazer (nao nomeia scripts/02_indexar.py)")
    print("RESULTADO: nao reindexou e avisou, nomeando scripts/02_indexar.py")

    print()
    print("--- caso 2: REINDEXAR = True e a mesma divergencia (a chave manda) ---")
    chamou, saida = rodar(reindexar=True)
    print(saida, end="")
    if not chamou:
        falhar("REINDEXAR = True deveria ter chamado rag.indexar()")
    print("RESULTADO: chamou rag.indexar(), como o criterio pede")

    print()
    print("--- caso 3: a condicao ANTIGA, para mostrar o que ela fazia ---")
    fonte_antiga = fonte.replace("if REINDEXAR:", "if REINDEXAR or colecao.count() != len(chunks):")
    fonte_antiga = fonte_antiga.split("elif colecao.count()")[0]
    escopo = {"rag": rag, "time": time, "REINDEXAR": False,
              "chunks": list(range(CHUNKS_ESPERADOS))}
    try:
        with redirect_stdout(io.StringIO()):
            exec(compile(fonte_antiga, "celula-antiga", "exec"), escopo)
        falhar("a condicao antiga deveria ter reindexado")
    except IndexarChamado:
        print("RESULTADO: com REINDEXAR = False, a versao antiga chamou rag.indexar()")
finally:
    rag.indexar, rag.abrir_colecao = indexar_original, abrir_original

print()
print("Os tres casos passaram. Nenhuma reindexacao real aconteceu: rag.indexar foi substituido")
print("por uma funcao que so levanta IndexarChamado, e a colecao usada e uma duble em memoria.")
