import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

RAIZ = Path(__file__).resolve().parents[1]
offline = "--offline" in sys.argv
notebook = nbformat.read(RAIZ / "webinario_rag.ipynb", as_version=4)
caminho = RAIZ / "webinario_rag.ipynb"
if offline:
    caminho = RAIZ / "docs" / "evidencias" / "E7" / "webinario_rag_offline.ipynb"
    configuracao = next(c for c in notebook.cells if c.cell_type == "code")
    for chave in ("LLM_AO_VIVO", "SHAP_AO_VIVO"):
        configuracao.source = configuracao.source.replace(f"{chave} = True", f"{chave} = False")
cliente = NotebookClient(notebook, timeout=3600, kernel_name="webinario-rag",
                         resources={"metadata": {"path": str(RAIZ)}})

inicio = time.perf_counter()
try:
    cliente.execute()
except CellExecutionError as erro:
    print(f"ERRO DE EXECUÇÃO: {str(erro).splitlines()[-1] if str(erro) else erro!r}")
finally:
    nbformat.write(notebook, caminho)
duracao = time.perf_counter() - inicio

codigo = [c for c in notebook.cells if c.cell_type == "code"]
erros = [(i, o) for i, c in enumerate(codigo) for o in c.get("outputs", []) if o.get("output_type") == "error"]
sem_saida = [i for i, c in enumerate(codigo) if not c.get("outputs")]
print(f"células de código: {len(codigo)} | executadas: {sum(1 for c in codigo if c.get('execution_count'))} "
      f"| com erro: {len(erros)} | sem saída: {sem_saida} | tempo total: {duracao:.0f}s")
for indice, celula in enumerate(codigo):
    tipos = sorted({o.get("output_type") for o in celula.get("outputs", [])})
    primeira_linha = celula.source.splitlines()[0][:70] if celula.source else ""
    print(f"  [{celula.get('execution_count')}] {primeira_linha!r} → {tipos}")
sys.exit(1 if erros else 0)
