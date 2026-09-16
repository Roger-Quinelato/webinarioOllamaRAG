"""Sonda do eixo A5 (RODADA-1) — só leitura.

1) Confere se todo link relativo dos documentos do escopo A5 aponta para um arquivo existente.
2) Confere se os comandos citados nas tabelas de comandos do README.md e do CLAUDE.md
   correspondem a arquivos existentes e, no caso de `verificar.py <sub>`, a uma função pública
   realmente definida em ferramentas/verificar.py.

Uso: .venv/Scripts/python.exe docs/auditoria/rodadas/RODADA-1/A5-sonda.py
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
ESCOPO = [
    RAIZ / "README.md",
    RAIZ / "CLAUDE.md",
    RAIZ / "docs" / "medicoes.md",
    RAIZ / "docs" / "troubleshooting.md",
    RAIZ / "docs" / "ESTADO_ATUAL.md",
]

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

print("== 1) links relativos quebrados ==")
quebrados = 0
for doc in ESCOPO:
    texto = doc.read_text(encoding="utf-8")
    for linha_num, linha in enumerate(texto.splitlines(), start=1):
        for alvo in LINK.findall(linha):
            if alvo.startswith(("http://", "https://", "mailto:", "#")):
                continue
            caminho = (doc.parent / alvo.split("#")[0]).resolve()
            if not caminho.exists():
                quebrados += 1
                print(f"  QUEBRADO {doc.relative_to(RAIZ)}:{linha_num} -> {alvo}")
print(f"  total de links relativos quebrados: {quebrados}")

print()
print("== 2) subcomandos de verificar.py documentados x definidos ==")
fonte = (RAIZ / "ferramentas" / "verificar.py").read_text(encoding="utf-8")
definidos = {n for n in re.findall(r"^def ([a-z0-9_]+)\(", fonte, re.M) if not n.startswith("_")}
claude = (RAIZ / "CLAUDE.md").read_text(encoding="utf-8")
linha_tabela = next(l for l in claude.splitlines() if "e7_duplicadas e e7_estrutura" in l)
documentados = set(re.findall(r"\b(e\d[a-z0-9_]*)\b", linha_tabela))
print(f"  definidos  ({len(definidos)}): {sorted(definidos)}")
print(f"  documentados ({len(documentados)}) em CLAUDE.md: {sorted(documentados)}")
print(f"  definidos e NAO documentados: {sorted(definidos - documentados)}")
print(f"  documentados e NAO definidos: {sorted(documentados - definidos)}")

print()
print("== 3) arquivos citados nas tabelas de comandos ==")
for alvo in ["scripts/00_checar_ambiente.py", "scripts/02_indexar.py", "app.py",
             "ferramentas/rodar_scripts.sh", "ferramentas/construir_notebook.py",
             "ferramentas/executar_notebook.py", "ferramentas/testar_app.py",
             "ferramentas/verificar.py", "ferramentas/medir.py",
             "ferramentas/gerar_plano_v11.py", "requirements-dev.txt", "requirements.lock"]:
    print(f"  {'OK   ' if (RAIZ / alvo).exists() else 'FALTA'} {alvo}")

print()
print("== 4) gerar_plano_v11.py: origem do .docx v1.0 ==")
origem_repo = list(RAIZ.glob("Plano_Aula_2-*v1.0.docx")) + list((RAIZ / "docs").glob("Plano_Aula_2-*v1.0.docx"))
print(f"  copias do v1.0 dentro do repositorio: {len(origem_repo)}")
downloads = sorted((Path.home() / "Downloads").glob("Plano_Aula_2-*v1.0.docx"))
print(f"  copias do v1.0 em ~/Downloads (fora do repo): {len(downloads)}")
for d in downloads:
    print(f"    {d.name}")
