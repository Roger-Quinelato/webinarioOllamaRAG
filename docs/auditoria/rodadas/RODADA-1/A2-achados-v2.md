# Eixo A2 — resposta à devolução e à lacuna (RODADA-1)

**Data:** 2026-09-16 · Trata apenas [`devolucoes/A2-05.md`](devolucoes/A2-05.md) e a LACUNA A2 do
[`cto-parecer-A2-A6.md`](cto-parecer-A2-A6.md). Os outros 15 achados de `A2-achados.md` foram
confirmados e seguem como estão.

---

### A2-05 — corrigido

- **resposta-a-devolucao:** corrigido
- **o que eu tinha errado:** enumerei célula por célula os números defasados de `docs/medicoes.md`,
  arquivo que não é do meu escopo e que o eixo A5 já cobre em sete achados mais específicos.

### A2-05 (revisado) — O critério 9.1 está ✅ apoiado em evidência que não sustenta mais os números

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:230` (critério 9.1, ✅), `ferramentas/verificar.py:470-493` (`e9_numeros`)
- **criterio:** 9.1
- **decisao-documentada:** `verificar.py:474-479` registra o hazard de que a checagem passaria calada se
  o regex parasse de casar, e trata "zero menções" como falha. A decisão cobre o caso de o **texto**
  mudar; não cobre o caso de o **número** estar certo segundo um arquivo histórico e errado segundo a
  execução atual, que é o que acontece aqui.
- **o-que-observei:** o ✅ de 9.1 se apoia em `docs/medicoes.md`, cujos números o eixo A5 mostrou
  estarem defasados em pelo menos sete células (A5-01 a A5-07). A única checagem automatizada que
  vigia esses números, `e9_numeros`, cobre apenas os que aparecem com a frase literal "na última
  execução do notebook" — três ocorrências — e confere contra `E7/saidas_notebook.txt`, que é
  append-only (A2-06). Nenhum dos sete achados de A5 está no alcance dela.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python ferramentas/verificar.py e9_numeros
  grep -c "na última execução do notebook" docs/medicoes.md
  ```
- **saida-obtida:** `e9_numeros` sai com 0; a contagem de menções é 3, contra ~30 células numéricas no
  documento.
- **por-que-importa:** um ✅ de E9 significa "os tempos desta máquina estão publicados e conferidos". O
  que existe hoje é "três números são conferidos contra um arquivo que guarda todo o histórico". O
  critério passa sem que a maior parte do que ele promete seja verificada.
- **confianca:** alta
- **relacionado:** A5-01, A5-02, A5-03, A5-04, A5-05, A5-06, A5-07 (os números em si, no eixo dono);
  A2-06 (a limitação do arquivo append-only)

### LACUNA A2 — respondida: 4 das 8 checagens que reprovam foram exercitadas contra entrada que deveria reprovar

- **severidade:** — (investigação pedida pelo CTO, sem achado novo)
- **onde:** `ferramentas/verificar.py`
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/lacuna-a2-sonda.py
  ```
- **saida-obtida:**
  ```
  e6_fontes (fontes_da_resposta sempre [1])      sys.exit=1     OK
  e9_numeros (numero 999,9 sem confirmacao)      sys.exit=1     OK
  e9_numeros (zero mencoes = checagem quebrada)  sys.exit=1     OK
  e7_saidas (notebook sem saida e sem tempos)    sys.exit=1     OK
  ```
- **método:** as entradas falsas foram montadas em diretório temporário e o módulo `verificar` apontado
  para lá por monkeypatch de `RAIZ`; nada do projeto foi alterado. Para `e6_fontes`, substituí
  `rag.fontes_da_resposta` por uma versão quebrada e restaurei em `finally`.
- **resultado:** as quatro exercitadas reprovam pelo motivo certo, inclusive os dois ramos de
  `e9_numeros`. Das outras quatro: `e7_duplicadas` já tem prova de reprovação versionada
  (`e7_duplicadas_antes_v2`, que a roda contra o `scripts/06` do commit `ba814a0` e acha a cópia de
  lógica); `e6_ollama_desligado_scripts` reprova por construção (roda os scripts com `OLLAMA_HOST`
  inválido); `e4` e `e4_limiar` **não foram exercitadas** porque só reprovam com distâncias que exigem
  outro corpus, e reindexar está proibido nesta rodada.
- **conclusão:** a lacuna se fecha para 6 das 8. Fica aberto, e vai para o backlog, o único buraco
  real: as duas checagens do estágio 1 nunca foram vistas reprovando, e são justamente as que guardam o
  achado 4.4.
