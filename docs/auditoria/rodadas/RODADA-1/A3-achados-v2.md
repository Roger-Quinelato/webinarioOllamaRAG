# Eixo A3 — resposta à devolução (RODADA-1)

**Data:** 2026-09-16 · Trata apenas [`devolucoes/A3-11.md`](devolucoes/A3-11.md). Os outros 13 achados
de `A3-achados.md` foram confirmados e seguem como estão.

---

### A3-11 — corrigido

- **resposta-a-devolucao:** corrigido
- **o que eu tinha errado:** reportei como descoberta nova um defeito que já tem ticket aberto (#24), e
  o prompt do eixo pedia explicitamente para marcá-lo como relacionado em vez de abrir achado novo.

### A3-11 (revisado) — Defeito conhecido confirmado: `scripts/01` e `02` sem `cli_seguro()`, e o que isso custa na aula

- **severidade:** média
- **categoria:** risco-ao-vivo
- **onde:** `scripts/01_preparar_corpus.py` (nenhum `with rag.cli_seguro():`),
  `scripts/02_indexar.py` (idem), `ferramentas/verificar.py:253` (`glob("0[3-7]_*.py")`)
- **criterio:** 6.7, 7.5
- **decisao-documentada:** `rag.py:46-47` explica que `cli_seguro` existe como "ponto único de saída
  amigável para os scripts de CLI", e `verificar.py:249-252` registra o hazard de testar só `rag.py`.
  Nenhum dos dois comentários justifica excluir `01` e `02`; a exclusão está no `glob`, sem nota.
- **o-que-observei:** confirmado por leitura: os dois scripts chamam o Ollama (`resumir_abstract` no
  `01`, `gerar_embeddings` e `extrair_metadados_llm` no `02`) sem nenhum tratamento, e a checagem que
  deveria pegar isso os exclui por construção.
- **o que a issue #24 não cobre — ângulo didático:** o `02` é o script do **bloco 2 do cronograma**, o
  mais longo da aula (18 minutos). Se o Ollama cair durante a indexação ao vivo, o que a turma vê é um
  traceback de `httpx.ConnectError` depois de minutos de barra de progresso. Conferi o
  `docs/roteiro_facilitador.md`: o bloco 2 tem plano B para **lentidão** ("não reindexar; com o modelo
  frio, `LLM_AO_VIVO = False`"), mas nenhuma linha para **Ollama fora do ar** nesse momento. O mesmo
  buraco aparece nas 8 células do notebook que levantei em A3-08, e as duas coisas se sobrepõem: as
  células do bloco 2 são exatamente as que o `scripts/02` espelha.
- **como-reproduzir:**
  ```bash
  grep -c "cli_seguro" scripts/01_preparar_corpus.py scripts/02_indexar.py
  grep -n "Ollama" docs/roteiro_facilitador.md
  ```
- **saida-obtida:** `scripts/01_preparar_corpus.py:0`, `scripts/02_indexar.py:0`; no roteiro, nenhuma
  ocorrência de plano B para Ollama indisponível no bloco 2.
- **por-que-importa:** o critério 6.7 existe para que o erro apareça como mensagem, não como traceback.
  Hoje ele está ✅ com dois scripts fora da cobertura, e o roteiro não dá ao facilitador o que dizer se
  isso acontecer no bloco mais longo da aula.
- **confianca:** alta
- **relacionado:** issue #24 (ticket já aberto para a correção em si), A3-08 (as 8 células do notebook
  sem chave), A2-07 (a checagem que exclui os dois scripts)
