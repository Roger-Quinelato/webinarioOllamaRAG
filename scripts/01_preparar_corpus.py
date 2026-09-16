import argparse
import csv
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import rag  # noqa: E402

parser = argparse.ArgumentParser(description="Baixa os artigos, valida o metadados.csv e gera os resumos com o LLM.")
parser.add_argument("--regerar-resumos", action="store_true", help="gera de novo mesmo os resumos já preenchidos")
args = parser.parse_args()

config.PASTA_ARTIGOS.mkdir(parents=True, exist_ok=True)
print("1) Artigos")
for nome, url in config.ARTIGOS_CORPUS.items():
    destino = config.PASTA_ARTIGOS / nome
    if not destino.exists():
        print(f"   baixando {nome} de {url}")
        urllib.request.urlretrieve(url, destino)
        # why: o arXiv bloqueia downloads em rajada.
        time.sleep(3)

total_paginas = 0
for pdf in sorted(config.PASTA_ARTIGOS.glob("*.pdf")):
    paginas = rag.extrair_paginas(pdf, limpar=False)
    vazias = [i for i, p in enumerate(paginas, start=1) if len(p.strip()) < 30]
    total_paginas += len(paginas)
    print(f"   {pdf.name:<28} {len(paginas):>3} páginas {sum(map(len, paginas)):>7} caracteres  "
          f"páginas sem texto: {vazias or 0}")
print(f"   total: {total_paginas} páginas")

print("\n2) metadados.csv")
with open(config.ARQUIVO_METADADOS, encoding="utf-8", newline="") as arquivo:
    cabecalho = next(csv.reader(arquivo))
linhas = rag.carregar_metadados()
erros = rag.validar_metadados(linhas, cabecalho)
for erro in erros:
    print(f"   ERRO: {erro}")
if erros:
    sys.exit(1)
print(f"   cabeçalho: {cabecalho}")
print(f"   {len(linhas)} linhas válidas (arquivo ↔ PDF, tema, idioma, ano)")

print("\n3) Resumos gerados pelo LLM a partir do abstract (no idioma do artigo)")
alterou = False
for linha in linhas:
    if linha["resumo"] and not args.regerar_resumos:
        print(f"   {linha['arquivo']}: já preenchido")
        continue
    primeira_pagina = rag.extrair_paginas(config.PASTA_ARTIGOS / linha["arquivo"], limpar=False)[0]
    abstract = rag.extrair_abstract(primeira_pagina)
    if not abstract:
        print(f"   {linha['arquivo']}: abstract não encontrado na 1ª página; preencha o resumo à mão")
        continue
    inicio = time.perf_counter()
    linha["resumo"] = rag.resumir_abstract(abstract, linha["idioma"])
    print(f"   {linha['arquivo']} ({time.perf_counter() - inicio:.1f}s): {linha['resumo']}")
    alterou = True
if alterou:
    rag.salvar_metadados(linhas)
    print("   metadados.csv atualizado")
