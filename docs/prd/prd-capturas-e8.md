# PRD — Consolidação das issues de captura de tela do Streamlit (E8)

- **Data:** 2026-09-16
- **Autor da decisão:** agente (delegada pelo autor)
- **Issues envolvidas:** [#15](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/15), [#25](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/25)
- **Tickets do consolidado absorvidos:** T40, T41 (`docs/auditoria/rodadas/RODADA-1/consolidado.md`)

## Problema

Duas issues abertas pedem a mesma entrega — capturas de tela reais do `app.py` para os critérios de E8
que declaram "captura" como método de verificação:

- **#15 (T15)** "Capturas reais 8.2/8.4/8.5/8.6/8.7/8.8": cenários isolados via
  `ferramentas/capturar_app.py`, 8+ PNGs em `docs/evidencias/E8/capturas/` mais um `capturas.txt`
  descrevendo cada imagem.
- **#25 (T13)** "Capturar screenshots reais do Streamlit (8.2, 8.4, 8.5, 8.7)": mesma entrega,
  restrita a 4 critérios.

O consolidado da RODADA-1 acrescentou dois tickets sobre o mesmo assunto:

- **T40** — refazer as capturas de E8 com o slider chegando ao backend (8.2, 8.4, 8.5, 8.6, 8.7, 8.8).
- **T41** — versionar as capturas de E8 (8.2–8.8).

Quatro registros para um único trabalho. Pior: a tentativa já feita produziu evidência **inválida**, e
esse diagnóstico está descrito na auditoria, não nas issues.

## O que a auditoria mostrou

O eixo A4 da RODADA-1 (achados A4-01, A4-02, A4-10, A4-11, A4-12, confirmados pelo CTO abrindo as
próprias imagens) encontrou:

- `ferramentas/capturar_evidencias_e8.py:32-43` (`_definir_slider`) escreve no `<input type="range">`
  pelo setter nativo e dispara `input`/`change`. O slider **se move na tela**, mas o Streamlit só manda
  o valor ao backend no `onFinalChange` (soltar o mouse), que um evento sintético não dispara.
- Consequência: `8.4a_k2.png` e `8.4b_k6.png` mostram o slider em 2 e em 6, mas as duas trazem a
  legenda `k = 4` e o expander `Fontes (citadas 1 de 4)`. São duas fotos do mesmo k. A discrepância é
  invisível para quem só olhar a barra lateral.
- `8.2b_streaming_em_curso.png` mostra a bolha do assistente vazia: 8.2 não tem hoje evidência válida
  de streaming.
- Nenhuma das capturas está versionada (`git ls-files docs/evidencias/E8/` devolve só texto), enquanto
  seis critérios de E8 declaram "captura" como método.

Esse diagnóstico é o ativo mais valioso que existe sobre o assunto: ele diz **por que** a próxima
tentativa precisa ser diferente.

## Decisão

**Manter #15 como a issue guarda-chuva, fechar #25 como duplicata e absorver T40 e T41 em #15 como
critérios de aceite.** Nenhuma issue nova é aberta para capturas de E8.

Razões:

1. **#15 e #25 pedem a mesma entrega.** #15 é mais antiga e tem escopo maior: inclui 8.6 (alternância
   simples × dois estágios) e 8.8 (Ollama indisponível), que #25 não lista. Manter a de escopo maior
   evita fechar um critério e deixar outro órfão.
2. **Fechar as duas e abrir uma terceira perderia o diagnóstico.** O histórico de #15 é onde a
   próxima tentativa começa; uma issue nova nasceria sem ele.
3. **Mantê-las separadas duplicaria o trabalho.** Duas issues abertas sobre o mesmo PNG levam a duas
   execuções do mesmo cenário, com risco de evidência divergente para o mesmo critério.
4. **T40 e T41 descrevem exatamente o escopo de #15 depois do diagnóstico** — refazer as capturas com o
   valor chegando ao backend, e versioná-las. São critérios de aceite dentro dela, não tickets novos:
   quem pegar #15 não tem como entregar sem cumprir os dois.

## Efeito nas issues

- **#25** — comentada com o diagnóstico A4-01 e fechada apontando para #15. Label `duplicate`.
- **#15** — comentada com o diagnóstico completo; corpo ganha, como critérios de aceite, o que T40 e
  T41 exigiam: o valor do slider tem de chegar ao backend (conferir a legenda `k = N` da resposta, não
  só o thumb do slider), a captura de streaming precisa mostrar texto parcial de fato, e os PNGs têm de
  estar versionados no git.

## Critérios de aceite de #15 depois desta decisão

- [ ] 8+ PNGs em `docs/evidencias/E8/capturas/` cobrindo os 6 cenários (8.2, 8.4, 8.5, 8.6, 8.7, 8.8)
- [ ] `capturas.txt` documenta cada imagem (timestamp, parâmetros, o que prova)
- [ ] Em 8.4, as duas capturas mostram **`k` diferente na legenda da resposta** (`k = N`), não só no
      slider — o valor chegou ao backend (fecha T40)
- [ ] Em 8.2, a captura de streaming mostra texto parcial visível na bolha do assistente (fecha A4-02)
- [ ] Os PNGs estão versionados: `git ls-files docs/evidencias/E8/capturas/` lista os arquivos
      (fecha T41)
- [ ] `docs/VERIFICACAO.md`, critérios 8.2/8.4/8.5/8.6/8.7/8.8, apontam para as capturas novas

## O que esta decisão não faz

Não refaz as capturas nem altera status de critério nenhum de E8. É só consolidação de registro: o
trabalho segue pendente em #15, agora com o diagnóstico e os critérios de aceite no lugar certo.
