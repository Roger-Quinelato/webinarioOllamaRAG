"""Sonda de casos de borda do eixo A1 — funcoes puras de rag.py, sem Ollama e sem ChromaDB."""
import sys
from pathlib import Path

RAIZ = Path(r"D:\webinarioOllamaRAG")
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402
import rag  # noqa: E402

R3 = [{"arquivo": f"artigo{i}.pdf", "pagina": i} for i in range(1, 4)]
recusa = config.RESPOSTA_NAO_ENCONTRADA

print("== A1-01 eh_recusa: recusa no FIM do texto ==")
texto_fim = f"Os trechos falam de outra coisa. {recusa}"
print(f"  eh_recusa={rag.eh_recusa(texto_fim)!r} fontes={[i for i, _ in rag.fontes_da_resposta(texto_fim, R3)]}")
texto_meio = f"{recusa} Mas segundo [2], o Ragas mede fidelidade."
print(f"  recusa+continuacao: eh_recusa={rag.eh_recusa(texto_meio)!r} "
      f"fontes={[i for i, _ in rag.fontes_da_resposta(texto_meio, R3)]}")

print("== A1-02 indices_citados: citacao fora do intervalo ==")
fora = "Segundo [7] e [9], nada."
print(f"  indices_citados={rag.indices_citados(fora, 3)} "
      f"fontes={[i for i, _ in rag.fontes_da_resposta(fora, R3)]} (fallback lista todos)")

print("== A1-03 validar_metadados: campo ano ==")
linhas_ok = [{"arquivo": "x.pdf", "tema": "survey", "idioma": "en", "ano": 2020}]
print(f"  ano int 2020 -> erros={rag.validar_metadados(linhas_ok, config.COLUNAS_METADADOS, RAIZ / 'nao_existe')}")
linhas_ruins = [{"arquivo": "x.pdf", "tema": "survey", "idioma": "en", "ano": -2020}]
print(f"  ano -2020 -> erros={[e for e in rag.validar_metadados(linhas_ruins, config.COLUNAS_METADADOS, RAIZ / 'nao_existe') if 'ano' in e]}")
csv_falso = RAIZ / "docs" / "evidencias" / "E1" / "nao_existe.csv"
print(f"  carregar_metadados faz int(linha['ano']) antes de validar: {csv_falso.exists()=} (ver rag.py:71)")

print("== A1-04 extrair_abstract com texto ja normalizado ==")
pagina = ("Titulo do artigo\nAutores\nAbstract\nEste artigo apresenta um metodo novo de recuperacao.\n"
          "1 Introduction\nO restante do artigo descreve o metodo em detalhe e segue por muitas paginas.")
bruto = rag.extrair_abstract(pagina)
limpo = rag.extrair_abstract(rag.limpar_texto(pagina))
print(f"  com quebras de linha: {len(bruto)} caracteres -> {bruto[:80]!r}")
print(f"  ja passado por limpar_texto: {len(limpo)} caracteres -> {limpo[:80]!r}")

print("== A1-05 gerar_chunks: artigo sem resumo ==")
print("  rag.py:162 `if meta['resumo']:` — artigo com resumo vazio nao gera chunk tipo_chunk=resumo")
print("  consequencia: esse artigo fica invisivel ao estagio 1 de buscar_dois_estagios, sem aviso")

print("== A1-06 dividir_texto: bordas ==")
print(f"  vazio -> {rag.dividir_texto('')}")
print(f"  menor que o chunk -> {rag.dividir_texto('abc')}")
texto = " ".join(f"palavra{i}" for i in range(400))
partes = rag.dividir_texto(texto)
sobrepostas = []
for a, b in zip(partes, partes[1:]):
    inicio_b = b[:40]
    sobrepostas.append(len(a) - a.find(inicio_b) if inicio_b in a else 0)
print(f"  {len(partes)} partes, tamanhos={[len(p) for p in partes]}, sobreposicao real={sobrepostas} "
      f"(config.SOBREPOSICAO={config.SOBREPOSICAO})")

print("== A1-07 combinar_filtros ==")
print(f"  nenhum -> {rag.combinar_filtros(None, None)}")
print(f"  um -> {rag.combinar_filtros({'ano': 2020}, None)}")
print(f"  dois -> {rag.combinar_filtros({'tipo_chunk': 'pagina'}, {'ano': 2020})}")
print(f"  conflito tipo_chunk -> {rag.combinar_filtros({'tipo_chunk': 'pagina'}, {'tipo_chunk': 'resumo'})}")

print("== A1-08 montar_prompt sem resultados ==")
print(f"  {rag.montar_prompt('pergunta?', [])!r}")
print(f"  montar_mensagens(p, []) papeis={[m['role'] for m in rag.montar_mensagens('p', [])]}")
print(f"  montar_mensagens(p, None) papeis={[m['role'] for m in rag.montar_mensagens('p', None)]}")

print("== A1-09 formatar_fontes com indices ==")
print(f"  {rag.formatar_fontes(R3, [2, 5, 9])!r}")

print("== A1-10 margem do limiar do estagio 1 ==")
print(f"  config.DISTANCIA_MAXIMA_ESTAGIO_1={config.DISTANCIA_MAXIMA_ESTAGIO_1}")
print("  T06 (corpus 6 artigos): dentro max 0.5435 | fora min 0.6784 -> folga acima do limiar 0.0784")
print("  T12 (corpus 8 artigos): intervalo seguro relatado (0.5435, 0.6566) -> folga acima do limiar 0.0566")
