"""LACUNA A2: as 8 checagens que chamam sys.exit reprovam quando deveriam?

Metodo: para cada checagem viavel em modo so-leitura, montar uma entrada que DEVERIA reprovar
e verificar se `sys.exit(1)` (ou 2) acontece. Nada do projeto e alterado: as entradas falsas
sao montadas num diretorio temporario e o modulo `verificar` aponta para la via monkeypatch.
"""
import shutil
import sys
import tempfile
from pathlib import Path

RAIZ = Path(r"D:\webinarioOllamaRAG")
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "ferramentas"))

import verificar  # noqa: E402


def exercitar(nome, funcao, esperado_reprova=True):
    """Descreve exercitar."""
    try:
        funcao()
        saiu = None
    except SystemExit as erro:
        saiu = erro.code
    ok = (saiu not in (None, 0)) if esperado_reprova else (saiu in (None, 0))
    print(f"  {nome:<46} sys.exit={saiu!s:<5} {'OK' if ok else 'FALHOU — nao reprovou'}")
    return ok


print("== e6_fontes com a regra de fontes quebrada ==")
original = verificar.rag.fontes_da_resposta
verificar.rag.fontes_da_resposta = lambda texto, resultados: [(1, resultados[0])] if resultados else []
try:
    exercitar("e6_fontes (fontes_da_resposta sempre [1])", verificar.e6_fontes)
finally:
    verificar.rag.fontes_da_resposta = original

print("== e9_numeros com medicoes.md citando um numero inexistente ==")
temporario = Path(tempfile.mkdtemp(prefix="lacuna_a2_"))
try:
    (temporario / "docs" / "evidencias" / "E7").mkdir(parents=True)
    (temporario / "docs" / "medicoes.md").write_text(
        "| SHAP | 999,9 s na última execução do notebook |\n", encoding="utf-8")
    (temporario / "docs" / "evidencias" / "E7" / "saidas_notebook.txt").write_text(
        "SHAP em 50s\n", encoding="utf-8")
    raiz_real = verificar.RAIZ
    verificar.RAIZ = temporario
    try:
        exercitar("e9_numeros (numero 999,9 sem confirmacao)", verificar.e9_numeros)
        (temporario / "docs" / "medicoes.md").write_text("sem nenhuma mencao\n", encoding="utf-8")
        exercitar("e9_numeros (zero mencoes = checagem quebrada)", verificar.e9_numeros)
    finally:
        verificar.RAIZ = raiz_real
finally:
    shutil.rmtree(temporario, ignore_errors=True)

print("== e7_saidas com um notebook sem os tempos obrigatorios ==")
temporario = Path(tempfile.mkdtemp(prefix="lacuna_a2_"))
try:
    (temporario / "webinario_rag.ipynb").write_text(
        '{"cells": [{"cell_type": "code", "source": ["print(1)"], "outputs": []}]}', encoding="utf-8")
    raiz_real = verificar.RAIZ
    verificar.RAIZ = temporario
    try:
        exercitar("e7_saidas (notebook sem saida e sem tempos)", verificar.e7_saidas)
    finally:
        verificar.RAIZ = raiz_real
finally:
    shutil.rmtree(temporario, ignore_errors=True)

print("== e7_duplicadas ja tem prova de reprovacao no proprio repositorio ==")
print("  e7_duplicadas_antes_v2 roda a checagem contra scripts/06 do commit ba814a0")
print("  e acha 'RESPOSTA_NAO_ENCONTRADA in ...' — a prova de que reprova esta versionada")

print("== nao exercitadas nesta rodada ==")
for nome, motivo in {
    "e4": "exigiria um corpus/indice diferente para o estagio 1 falhar — reindexar e proibido",
    "e4_limiar": "mesma razao: so reprova com distancias que exigem outro corpus",
    "e6_ollama_desligado_scripts": "ja reprova por construcao (roda os scripts com OLLAMA_HOST invalido)",
    "e7_duplicadas": "coberta por e7_duplicadas_antes_v2, ver acima",
}.items():
    print(f"  {nome:<30} {motivo}")
