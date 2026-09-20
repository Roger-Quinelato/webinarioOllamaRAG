"""Validação independente do CTO sobre os achados A1 — entradas diferentes das usadas pelo auditor."""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(r"D:\webinarioOllamaRAG")
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402
import rag  # noqa: E402

R4 = [{"arquivo": f"a{i}.pdf", "pagina": i} for i in range(1, 5)]
recusa = config.RESPOSTA_NAO_ENCONTRADA

print("== CTO/A1-01 frase realista de preambulo, diferente da usada pelo auditor ==")
for texto in (f"Com base nos trechos fornecidos: {recusa}",
              f"Resposta: {recusa}",
              f"{recusa}",
              f"  {recusa}"):
    print(f"  eh_recusa={rag.eh_recusa(texto)!s:<5} fontes={[i for i, _ in rag.fontes_da_resposta(texto, R4)]} <- {texto[:45]!r}")

print("== CTO/A1-02 citacao mista valida+invalida vs so invalida ==")
for texto in ("Segundo [2] e [9].", "Segundo [9].", "Segundo [0].", "Sem citacao alguma."):
    print(f"  indices_citados={rag.indices_citados(texto, 4)} fontes={[i for i, _ in rag.fontes_da_resposta(texto, R4)]} <- {texto!r}")

print("== CTO/A1-03 ano nao numerico no CSV real ==")
csv = RAIZ / "docs" / "auditoria" / "rodadas" / "RODADA-1" / "_cto_metadados_temp.csv"
csv.write_text("arquivo,titulo,autores,ano,veiculo,tema,idioma,resumo\n"
               "x.pdf,T,A,vinte e vinte,V,survey,en,R\n", encoding="utf-8")
try:
    rag.carregar_metadados(csv)
    print("  carregar_metadados aceitou o valor nao numerico")
except ValueError as erro:
    print(f"  carregar_metadados levantou ValueError cru: {erro}")
finally:
    csv.unlink()

print("== CTO/A1-04 regex do abstract: qual ramo casa ==")
pagina = "Titulo\nAbstract\nTexto do abstract aqui.\nKeywords: rag, retrieval\nResto."
print(f"  com quebras: {rag.extrair_abstract(pagina)!r}")
print(f"  normalizado: {rag.extrair_abstract(rag.limpar_texto(pagina))[:70]!r}")

print("== CTO/A1-05 aviso na indexacao quando falta resumo ==")
fonte = (RAIZ / "rag.py").read_text(encoding="utf-8")
print(f"  'resumo' aparece em aviso/print dentro de gerar_chunks? "
      f"{'print' in fonte.split('def gerar_chunks')[1].split('def ')[0]}")
script01 = (RAIZ / "scripts" / "01_preparar_corpus.py").read_text(encoding="utf-8")
print(f"  scripts/01 avisa 'preencha o resumo a mao'? {'preencha o resumo' in script01}")

print("== CTO/A1-07 sobreposicao: existe caso com sobreposicao zero ou palavra cortada? ==")
piores = []
for n in (120, 260, 400, 900):
    texto = " ".join(f"p{i}" for i in range(n))
    partes = rag.dividir_texto(texto)
    for a, b in zip(partes, partes[1:]):
        chave = b[:30]
        piores.append(len(a) - a.find(chave) if chave in a else 0)
print(f"  sobreposicoes observadas: min={min(piores)} max={max(piores)} zeros={piores.count(0)} "
      f"(config={config.SOBREPOSICAO})")
palavra_cortada = any(not p.endswith(" ") and not p[-1].isdigit() for p in rag.dividir_texto(" ".join(f"p{i}" for i in range(400))))
print(f"  alguma parte termina no meio de uma palavra? {palavra_cortada}")

print("== CTO/LACUNA _erro_ollama: mensagem para erro que NAO e de conexao ==")
erro_http = rag.ollama.ResponseError("internal server error", 500)
print(f"  status 500 -> {rag._erro_ollama(erro_http, 'qwen2.5:1.5b')}")
erro_404 = rag.ollama.ResponseError("model not found", 404)
print(f"  status 404 -> {rag._erro_ollama(erro_404, 'qwen2.5:1.5b')}")

print("== CTO/LACUNA determinismo com seed=42 ==")
print(f"  _opcoes() = {rag._opcoes()}")
try:
    a = rag.gerar_texto("Responda apenas: 1+1=", max_tokens=10)
    b = rag.gerar_texto("Responda apenas: 1+1=", max_tokens=10)
    print(f"  duas chamadas iguais -> identicas={a == b} | {a[:40]!r} vs {b[:40]!r}")
except rag.OllamaIndisponivel as erro:
    print(f"  Ollama indisponivel: {erro}")

print("== CTO/A1-00 estado atual do ambiente ==")
saida = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True, cwd=RAIZ)
print(f"  pip check -> exit={saida.returncode} {saida.stdout.strip()[:80]!r}")
