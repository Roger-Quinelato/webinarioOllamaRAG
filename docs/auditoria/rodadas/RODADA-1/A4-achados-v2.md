# Eixo A4 — resposta à lacuna (RODADA-1)

**Data:** 2026-09-16 · Trata apenas a LACUNA A4 do [`cto-parecer-A2-A6.md`](cto-parecer-A2-A6.md). Os 14
achados de `A4-achados.md` foram confirmados e seguem como estão.

---

### A4-15 — A citação de fontes falha em 6 de 8 respostas com o modelo padrão (resposta à LACUNA A4)

- **severidade:** alta
- **categoria:** risco-ao-vivo
- **onde:** `rag.py:365` (fallback), `app.py:31` e `:40` (rótulo e marca "✅ citado"),
  `config.py:17` (`MODELO_CHAT = "qwen2.5:1.5b"`)
- **criterio:** 6.5, 8.7, 9.3
- **decisao-documentada:** `rag.py:359-365` justifica o fallback pelo caso "o modelo não citou nenhum",
  "para nunca ficar sem fontes". A decisão foi tomada quando o padrão era o `qwen2.5:3b`; a medição
  abaixo mostra que, com o 1.5b, esse caso deixou de ser exceção e virou a regra.
- **o-que-observei:** oito perguntas dentro da base, uma por vez, com `seed=42` e `k=4` — as seis áreas
  do corpus mais os dois artigos em português. Duas respostas citaram `[n]`; seis não citaram nada e
  caíram no fallback, que exibiu os quatro trechos como fonte. Nenhuma foi recusa.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/lacuna-a4-sonda.py
  ```
- **saida-obtida:**
  ```
  modelo: qwen2.5:1.5b | k: 4 | seed fixo: 42
  1. citou=NAO indices=[] fontes_exibidas=[1, 2, 3, 4] recusa=False (98.6s)
  4. citou=sim indices=[3, 2] fontes_exibidas=[3, 2] recusa=False (38.8s)
  8. citou=sim indices=[1, 2, 3] fontes_exibidas=[1, 2, 3] recusa=False (56.0s)

  respostas com pelo menos uma citacao valida: 2/8
  respostas em que o fallback listou todo o top-k: 6/8
  ```
- **por-que-importa:** é o número que faltava para decidir o critério 9.3. A demonstração do 6.5 — a
  tela distinguindo "trecho enviado" de "fonte citada" — funciona em **25%** das perguntas com o modelo
  que o ticket #19 tornou padrão. Nas outras 75%, o app afirma "Fontes (citadas 4 de 4)" e marca "✅
  citado" em tudo, o oposto do que os tickets #1, #3 e #4 construíram. Como é intermitente, o
  facilitador não tem como ensaiar: a mesma pergunta pode citar num dia e não citar no outro.
- **o que isto não decide:** a sonda não mediu o `qwen2.5:3b`. Comparar os dois é o que fecha 9.3, e
  exige uma rodada equivalente com o plano B — fora do escopo desta rodada, porque trocar de modelo
  custa 40–80 s de carga e degrada as outras medições.
- **confianca:** alta (8 amostras, uma medição por pergunta, seed fixo; o resultado é consistente com
  as duas respostas salvas em `resultados/com_sem_contexto.json` e com as duas células do notebook,
  todas sem citação, e com as capturas do T15, que citaram)
- **relacionado:** A1-08 (piloto, com o alcance já corrigido pelo CTO), A4-06, A3-02, A2-10
