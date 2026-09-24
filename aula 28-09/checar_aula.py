"""Checa as regras pedagógicas e de manutenção de aula 28-09/aula_rag_colab.ipynb (EDU-COLAB-05.1).

Rode depois de alterar o gerador:

    python "aula 28-09/gerar_aula_rag_colab.py"
    python "aula 28-09/checar_aula.py"

Só usa a biblioteca padrão. Sai com código 1 se alguma regra falhar.
"""

import ast
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

PASTA = Path(__file__).parent
NOVO = PASTA / "aula_rag_colab.ipynb"
NOTEBOOKS = PASTA.parent / "notebooks"
ANTIGO = NOTEBOOKS / "rag_com_seus_documentos.ipynb"

MEDIANA_MAXIMA = 8
LINHAS_MAXIMAS = 15
SECOES = [f"## {n}." for n in range(15)]  # §0 … §14, nesta ordem
PROIBIDO_NO_CODIGO = [  # nada de API externa, chave, Ollama ou formatos que a T4 não roda bem
    "api_key", "getpass", "openai", "google_api_key", "nvidia_api_key", "init_chat_model",
    "ollama", "bitsandbytes", "bfloat16", "userdata",
]
PROIBIDO_NO_TEXTO = ["🎓", "🔬", "🧪", "Aprofundando"]  # nada de trilha "avançada"

resultados = []


def regra(nome, ok, detalhe="", sempre=False):
    """Registra uma regra; o detalhe aparece quando ela falha (ou sempre, para métricas)."""
    resultados.append(ok)
    print(("✅ " if ok else "❌ ") + nome + (f" — {detalhe}" if detalhe and (sempre or not ok) else ""))


def fonte(celula):
    return "".join(celula["source"])


def sem_magias(codigo):
    """Troca linhas de magia do Colab (%pip, !cmd) por `pass` para o ast entender o resto."""
    return "\n".join("pass" if l.lstrip().startswith(("%", "!")) else l for l in codigo.splitlines())


def regenerar(gerador, destino):
    """Roda o gerador e diz se o .ipynb versionado ficou idêntico (ninguém editou à mão)."""
    antes = destino.read_bytes()
    subprocess.run([sys.executable, str(gerador)], check=True, capture_output=True)
    return destino.read_bytes() == antes


# 1. O .ipynb é artefato gerado
regra("notebook novo idêntico ao que o gerador produz",
      regenerar(PASTA / "gerar_aula_rag_colab.py", NOVO),
      'rode `python "aula 28-09/gerar_aula_rag_colab.py"` e versione o resultado')
regra("notebook antigo intacto (idêntico ao seu gerador)",
      regenerar(NOTEBOOKS / "gerar_notebook_publico.py", ANTIGO))

nb = json.loads(NOVO.read_text(encoding="utf-8"))
celulas = nb["cells"]
codigos = [fonte(c) for c in celulas if c["cell_type"] == "code"]
textos = [fonte(c) for c in celulas if c["cell_type"] == "markdown"]

# 2. Estrutura do notebook
regra("nbformat 4 com metadados de GPU para o Colab",
      nb.get("nbformat") == 4 and nb["metadata"].get("accelerator") == "GPU"
      and nb["metadata"].get("colab", {}).get("gpuType") == "T4")

posicoes = [next((i for i, t in enumerate(textos) if t.lstrip().startswith(s)), None) for s in SECOES]
faltando = [SECOES[i] for i, p in enumerate(posicoes) if p is None]
regra("as 15 seções (§0–§14) existem e estão em ordem",
      not faltando and posicoes == sorted(posicoes), f"faltando: {faltando}" if faltando else "")

sem_texto_antes = [c["id"] for i, c in enumerate(celulas)
                   if c["cell_type"] == "code" and (i == 0 or celulas[i - 1]["cell_type"] != "markdown")]
regra("toda célula de código vem depois de uma célula de texto", not sem_texto_antes, str(sem_texto_antes))

# 3. Uma célula = uma ideia
erros_sintaxe = []
for c in celulas:
    if c["cell_type"] == "code":
        try:
            ast.parse(sem_magias(fonte(c)))
        except SyntaxError as erro:
            erros_sintaxe.append(f"{c['id']}: {erro.msg} (linha {erro.lineno})")
regra("todas as células de código são Python válido", not erros_sintaxe, "; ".join(erros_sintaxe))

linhas = {c["id"]: len([l for l in fonte(c).splitlines() if l.strip()])
          for c in celulas if c["cell_type"] == "code"}
mediana = statistics.median(linhas.values())
grandes = {i: n for i, n in linhas.items() if n > LINHAS_MAXIMAS}
regra(f"mediana de linhas por célula de código ≤ {MEDIANA_MAXIMA}", mediana <= MEDIANA_MAXIMA, f"mediana = {mediana:g}", sempre=True)
regra(f"nenhuma célula de código com mais de {LINHAS_MAXIMAS} linhas", not grandes,
      str(grandes) if grandes else f"máximo = {max(linhas.values())}", sempre=True)

# 4. Nada de API externa nem trilha avançada
achados = sorted({p for p in PROIBIDO_NO_CODIGO for c in codigos if p in c.lower()})
regra("código sem API key, provedor externo, Ollama, bitsandbytes ou bf16", not achados, str(achados))
achados = sorted({p for p in PROIBIDO_NO_TEXTO for t in textos if p in t})
titulos_avancados = [l for t in textos for l in t.splitlines()
                     if l.startswith("#") and re.search(r"avançad", l, re.IGNORECASE)]
regra("sem blocos de trilha avançada (🎓 🔬 🧪, títulos 'avançado')", not achados and not titulos_avancados,
      str(achados + titulos_avancados))

print(f"\n{len(celulas)} células ({len(codigos)} de código) · mediana {mediana:g} · máximo {max(linhas.values())}")
if not all(resultados):
    sys.exit(1)
print("Tudo certo.")
