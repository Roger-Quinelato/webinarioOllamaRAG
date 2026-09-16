# Eixo A4 — Aplicação Streamlit — achados (RODADA-1)

**Escopo:** `app.py`, `ferramentas/testar_app.py`, `ferramentas/capturar_app.py`,
`ferramentas/capturar_evidencias_e8.py`, `docs/evidencias/E8/**`
**Data:** 2026-09-16 · **HEAD:** `eec1ecc` (branch `chore/agent-skills-setup`) · **Modo:** só leitura

**Pergunta central:** os critérios 8.1 a 8.8 se sustentam no app real, com evidência do que a tela mostra?

O que foi executado ao vivo nesta auditoria (uso exclusivo do Ollama, um comando de cada vez, nada
reindexado, notebook não executado):

| Comando | Duração | Saída |
|---|---|---|
| `.venv/Scripts/python ferramentas/testar_app.py` | ~8 min | `A4-sonda.txt`, bloco 1 |
| `A4-sonda.py apptest` (rerender, filtro vazio, Ollama caindo no meio, Limpar conversa) | ~2 min | `A4-sonda.txt`, bloco 2 |
| `A4-sonda.py selectbox` ×3 (`MODELO_CHAT` = 3b, 1.5b, llama3.2:3b) | ~3 min | `A4-sonda.txt`, bloco 3 |
| `A4-sonda.py ollama-off` (`OLLAMA_HOST=http://localhost:1`) | ~30 s | `A4-sonda.txt`, bloco 4 |
| `A4-sonda.py slider` (Playwright/msedge, porta 8502, derrubada ao fim) | ~4 min | `A4-sonda.txt`, bloco 5 |

Sonda versionada em [`A4-sonda.py`](A4-sonda.py); saída bruta em [`A4-sonda.txt`](A4-sonda.txt).
Os 8 PNGs de `docs/evidencias/E8/capturas/` (trabalho não commitado do ticket #15) foram abertos e
inspecionados um a um.

---

### A4-01 — As capturas `8.4a_k2` e `8.4b_k6` foram tiradas com k = 4 nas duas: o slider da sonda de captura não chega ao backend do Streamlit

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `ferramentas/capturar_evidencias_e8.py:32-43` (`_definir_slider`), `:90-100` (cenário 8.4),
  `docs/evidencias/E8/capturas/8.4a_k2.png`, `docs/evidencias/E8/capturas/8.4b_k6.png`
- **criterio:** 8.4
- **o-que-observei:** `_definir_slider` escreve no `<input type="range">` com o setter nativo e dispara
  `input`/`change`. Isso move o slider na tela (o rótulo do thumb muda para 2 e para 6 nas duas
  capturas), mas o Streamlit só envia o valor ao backend no `onFinalChange` (soltar o mouse), que um
  evento sintético não dispara. Resultado: as duas capturas mostram a legenda
  `Caminho usado: busca simples · k = 4 · modelo qwen2.5:1.5b` e o expander
  `Fontes (citadas 1 de 4) — busca simples`. O texto da resposta em `8.4b_k6.png` é idêntico, palavra
  por palavra, ao de `8.2c_resposta_completa.png`, que foi tirada antes de qualquer mexida no slider —
  ou seja, a mesma pergunta foi reenviada três vezes com o mesmo k = 4.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A4-sonda.py slider
  ```
  (importa o `_definir_slider` do próprio `capturar_evidencias_e8.py`, aplica k=6 e depois k=2 num app
  real na porta 8502 e lê a legenda que o backend escreveu)
- **saida-obtida:**
  ```
  SUBSTITUIR_SLIDER
  ```
  E, lido diretamente das capturas (barra lateral × legenda da resposta):
  ```
  8.4a_k2.png : slider na tela = 2 | legenda = "… k = 4 …" | expander = "Fontes (citadas 1 de 4)"
  8.4b_k6.png : slider na tela = 6 | legenda = "… k = 4 …" | expander = "Fontes (citadas 1 de 4)"
  ```
- **por-que-importa:** essas duas capturas são exatamente a evidência que o ticket #15/#25 pretende
  commitar para fechar o critério 8.4 ("captura com k diferentes"). Elas provam o contrário do que
  afirmam: são duas fotos do mesmo k. Pior, a discrepância é invisível a olho nu para quem só olhar a
  barra lateral — é preciso ler a legenda da resposta.
- **confianca:** alta
- **relacionado:** A4-04, A4-11

### A4-02 — A captura `8.2b_streaming_em_curso` mostra a bolha do assistente vazia; 8.2 não tem hoje nenhuma evidência válida de streaming

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `ferramentas/capturar_evidencias_e8.py:83-85` (`pagina.wait_for_timeout(1500)`),
  `docs/evidencias/E8/capturas/8.2b_streaming_em_curso.png`, `docs/evidencias/E8/ui_navegador.txt:10-27`
- **criterio:** 8.2
- **o-que-observei:** a captura descrita como "Logo após enviar — resposta ainda em streaming" mostra a
  pergunta do usuário e, abaixo, o avatar do assistente **sem nenhum texto e sem a legenda
  "Caminho usado"** — a espera é um `wait_for_timeout(1500)` fixo, e 1,5 s não chega nem para a busca
  vetorial terminar nesta máquina. Não há como distinguir essa imagem de um app travado. As outras duas
  vias de evidência de 8.2 também não sustentam o critério hoje: o `AppTest` de
  `ferramentas/testar_app.py` consome `st.write_stream` de uma vez e não observa streaming nenhum (ele
  só imprime o tempo total, linha 39), e `docs/evidencias/E8/ui_navegador.txt` é de 2026-09-14, com
  `qwen2.5:3b`, corpus de 6 artigos e rótulo de expander `Fontes (4) — busca simples`, formato que o
  app não produz desde o T04.
- **como-reproduzir:** abrir `docs/evidencias/E8/capturas/8.2b_streaming_em_curso.png`; e
  ```bash
  grep -n "Fontes (4)" docs/evidencias/E8/ui_navegador.txt
  grep -n "wait_for_timeout(1500)" ferramentas/capturar_evidencias_e8.py
  ```
- **saida-obtida:**
  ```
  docs/evidencias/E8/ui_navegador.txt:34:Fontes (4) — busca simples
  ferramentas/capturar_evidencias_e8.py:84:            pagina.wait_for_timeout(1500)
  ```
  Conteúdo visível de `8.2b_streaming_em_curso.png`: título, legenda do webinário, bolha do usuário
  com a pergunta, avatar do assistente isolado, área de resposta em branco.
- **por-que-importa:** 8.2 ("Pergunta enviada gera resposta em streaming") é o critério cuja verificação
  declarada é "teste no navegador com captura de tela". Hoje não existe captura que mostre texto
  crescendo, o teste automatizado é cego para streaming por construção, e o único registro textual de
  streaming descreve uma UI e um modelo que não são mais os do projeto.
- **confianca:** alta
- **relacionado:** A4-04, A4-05, A4-14

### A4-03 — A captura `8.6_modo_dois_estagios` não mostra nenhuma indicação de UI do caminho usado

- **severidade:** média
- **categoria:** evidencia
- **onde:** `ferramentas/capturar_evidencias_e8.py:102-109`,
  `docs/evidencias/E8/capturas/8.6_modo_dois_estagios.png`
- **criterio:** 8.6
- **o-que-observei:** o critério 8.6 pede "captura **+ indicação na UI**". A captura mostra apenas o
  rádio "Dois estágios" marcado na barra lateral e o miolo de um expander já aberto, com os trechos
  `[3]` e `[4]`. Não aparece nenhuma das três indicações que o app produz para o caminho: a legenda
  `Caminho usado: dois estágios` (`app.py:92`), a linha
  `Estágio 1 — artigos escolhidos pelos resumos:` (`app.py:33-34`) nem o rótulo do expander
  `Fontes (citadas X de Y) — dois estágios` (`app.py:31`). O script abre o expander
  (`:107`) e só depois captura, o que empurra o cabeçalho para fora do enquadramento. A captura
  `8.5_filtro_tema_limitacoes.png`, tirada 10 s depois, mostra o mesmo miolo com as mesmas distâncias
  (0.3776 e 0.3808), diferindo apenas pelo chip `limitacoes` na barra lateral.
- **como-reproduzir:** abrir as duas capturas lado a lado e procurar as strings "Caminho usado",
  "Estágio 1" ou "Fontes (citadas" na imagem.
- **saida-obtida:**
  ```
  8.6_modo_dois_estagios.png : visíveis = rádio "Dois estágios", trechos [3] e [4] (limitacoes, en)
                               ausentes = "Caminho usado…", "Estágio 1 — artigos escolhidos…",
                                          "Fontes (citadas X de Y) — dois estágios"
  ```
- **por-que-importa:** é a única captura proposta para 8.6, e o que ela demonstra ("marquei um rádio")
  não é o que o critério pede (que a UI indique que o caminho mudou). Quem replicar em casa não
  consegue conferir contra ela.
- **confianca:** alta
- **relacionado:** A4-07, A4-12

### A4-04 — Nenhuma captura de tela está versionada; seis dos oito critérios de E8 declaram "captura" como método de verificação

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:214-222` (critérios 8.2, 8.4, 8.5, 8.6, 8.7, 8.8 e a linha
  "**Evidência:** `docs/evidencias/E8/` (capturas + log)"), `docs/evidencias/E8/`
- **criterio:** 8.2, 8.4, 8.5, 8.6, 8.7, 8.8
- **o-que-observei:** o repositório não tem nenhum `.png` versionado. `docs/evidencias/E8/` versiona
  cinco arquivos de texto. Os 8 PNGs existem só na árvore de trabalho, como `??` no `git status`, junto
  com o script que os gera (`ferramentas/capturar_evidencias_e8.py`, também não commitado). Ou seja: a
  linha "Evidência: capturas + log" do `VERIFICACAO.md` não é verdadeira para nada que esteja no
  repositório, e nem o gerador das capturas é reproduzível a partir dele.
- **como-reproduzir:**
  ```bash
  git ls-files docs/evidencias/E8
  git ls-files "*.png"
  git status --short
  ```
- **saida-obtida:**
  ```
  docs/evidencias/E8/apptest.txt
  docs/evidencias/E8/streamlit_servidor.log
  docs/evidencias/E8/t04_fontes_citadas_app.txt
  docs/evidencias/E8/ui_navegador.txt
  docs/evidencias/E8/ui_ollama_desligado.txt
  (git ls-files "*.png" → 0 linhas)
   M ferramentas/capturar_app.py
  ?? docs/evidencias/E8/capturas/
  ?? ferramentas/capturar_evidencias_e8.py
  ```
- **por-que-importa:** é o achado central do eixo. O comportamento do app se sustenta (ver o que o
  AppTest e a sonda confirmam abaixo), mas a **forma de evidência que os critérios exigem** não existe
  no repositório, e as candidatas a preenchê-la têm os problemas de A4-01, A4-02 e A4-03. Quem clonar o
  repositório hoje não consegue conferir nenhum dos seis critérios pela evidência prometida.
- **confianca:** alta
- **relacionado:** A4-01, A4-02, A4-03, A4-10

### A4-05 — `testar_app.py` só reprova em 3 dos ~9 pontos que verifica: 8.1, 8.2, 8.3, 8.7 e o caso de recusa apenas imprimem

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `ferramentas/testar_app.py:25-28` (`falhar`), chamadas em `:58-59`, `:69-70`, `:80-82`;
  prints sem asserção em `:32` (8.1), `:39-43` (8.2/8.4 primeira rodada), `:54-55` (8.3), `:83-91`
  (8.7/T04), `:99-101` (recusa), `:103` (exceções finais). `ferramentas/verificar.py` não tem nenhuma
  checagem de E8 (as 15 existentes vão de `e1_resumos` a `e9_numeros`).
- **criterio:** 8.1, 8.2, 8.3, 8.7
- **decisao-documentada:** o `hazard:` de `ferramentas/testar_app.py:10-12` registra a decisão do T16/#16:
  "Cada rodada abaixo muda só uma variável por vez, **com um assert que sai com 1 (mensagem clara) em
  caso de falha, em vez de só imprimir**." A decisão foi aplicada apenas às três rodadas isoladas
  (`:58`, `:69`, `:80`), que cobrem 8.4, 8.6 e 8.5. Os demais critérios da mesma suíte ficaram no regime
  antigo de "só imprimir", que é justamente o que o comentário diz ter sido abandonado — a decisão
  documentada não cobre 8.1, 8.2, 8.3, 8.7 nem a recusa.
- **o-que-observei:** uma regressão em qualquer um desses pontos (app subindo com exceção, histórico
  perdendo mensagens, expander sem arquivo/página/trecho/resumo, recusa voltando a listar fontes) faz o
  script imprimir o valor errado e sair com **0**. `verificar.py` não tem entrada para E8, então não há
  segunda rede.
- **como-reproduzir:**
  ```bash
  grep -n "falhar(" ferramentas/testar_app.py
  grep -n "^def e" ferramentas/verificar.py
  ```
- **saida-obtida:**
  ```
  ferramentas/testar_app.py:25:def falhar(rotulo, motivo):
  ferramentas/testar_app.py:59:    falhar("8.4 (só k)", …)
  ferramentas/testar_app.py:70:    falhar("8.6 (só modo)", …)
  ferramentas/testar_app.py:81:    falhar("8.5 (só filtro)", …)
  ferramentas/verificar.py: e1_resumos e2 e2_sobreposicao e2_reabrir e3 e4 e4_limiar
                            e6_ollama_desligado e6_ollama_desligado_scripts e6_fontes
                            e7_duplicadas e7_duplicadas_antes_v2 e7_estrutura e7_saidas e9_numeros
  ```
- **por-que-importa:** é o mesmo defeito que o ticket #2 (T02) corrigiu em `e7_duplicadas` ("nunca falha,
  só imprime") e que o `/code-review` do #10 corrigiu em `e9_numeros`. Aqui ele continua vivo no único
  teste automatizado de E8, e são justamente os critérios sem asserção (8.2, 8.7) os que mais mexeram
  desde o T04.
- **confianca:** alta
- **relacionado:** A4-06

### A4-06 — Quando o `qwen2.5:1.5b` não cita nada, a tela afirma que citou tudo: "Fontes (citadas 4 de 4)" com "✅ citado" em todos os trechos

- **severidade:** alta
- **categoria:** risco-ao-vivo
- **onde:** `app.py:31` (rótulo do expander), `app.py:40` (marca "✅ citado"), `app.py:100`
  (`busca["citadas"]`), alimentados pelo fallback de `rag.py:365`
- **criterio:** 8.7, 6.5
- **decisao-documentada:** o `hazard:` de `app.py:24-26` registra a intenção do T04: "marcar todo o
  top-k como 'Fontes' sem distinguir o que a resposta citou de fato mistura o que entrou no prompt com
  o que foi usado". O fallback de `rag.py:359-365` também é decisão registrada ("se o modelo não citou
  nenhum, cai para os recuperados, para nunca ficar sem fontes"). O que nenhuma das duas cobre é a
  composição delas na tela: quando o fallback dispara, `citadas == todos os índices`, e a UI passa a
  **afirmar positivamente** ("citadas 4 de 4", "✅ citado" em cada linha) exatamente a mistura que o
  `hazard:` de `app.py:24-26` existe para evitar. O fallback em `rag.py` é silencioso; em `app.py` ele
  vira uma afirmação visível e falsa.
- **o-que-observei:** medi 4 respostas positivas hoje, em duas execuções independentes, e o fallback
  disparou nas 4 — em todas a tela marcou 100% dos trechos como citados, sem que a resposta contivesse
  um único `[n]`. Não é determinístico: na execução versionada em `docs/evidencias/E8/apptest.txt`
  (mesma suíte, mesmas perguntas, mesmo `seed=42`/`temperature=0.1`, 2026-09-16 00:16) a **mesma**
  pergunta com o **mesmo** k produziu `citadas: [1]` ("citadas 1 de 2"), enquanto na minha execução das
  04:27 produziu `citadas: [1, 2]` ("citadas 2 de 2"). Isto confirma o efeito descrito no achado A1-08
  e **refuta a forma forte dele**: o 1.5b emite `[n]` às vezes (a captura `8.2c_resposta_completa.png`
  mostra "citadas 1 de 4"). O problema não é "nunca cita", é "cita de forma instável, e quando não cita
  a tela mente".
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python ferramentas/testar_app.py
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A4-sonda.py apptest
  ```
- **saida-obtida:**
  ```
  # testar_app.py, 2026-09-16 04:27 (esta auditoria)
  8.4 k=2 → expanders: ['Fontes (citadas 2 de 2) — busca simples'] | citadas: [1, 2]
  8.4 k=5 → fontes na última resposta: 5 | citadas: [1, 2, 3, 4, 5]
  8.7/T04 rótulo do último expander: 'Fontes (citadas 5 de 5) — dois estágios'
  T04 trechos citados marcados '✅ citado': ['[1] Lost in the Middle…', '[2] Lost in the Middle…',
     '[3] Lost in the Middle…', '[4] Lost in the Middle…', '[5] Lost in the Middle…']

  # A4-sonda.py apptest, 2026-09-16 04:35
  respondida em 48s | citadas=[1, 2, 3, 4] de 4
  resposta[:160]='O artigo Lost in the Middle descobriu que as linguagens de modelo atuais não são
                  robustas em relação à utilização de informações em contextos longos de entrada.'

  # docs/evidencias/E8/apptest.txt, versionado, 2026-09-16 00:16 — MESMA pergunta, MESMO k
  8.4 k=2 → expanders: ['Fontes (citadas 1 de 2) — busca simples'] | citadas: [1]
  ```
- **por-que-importa:** o bloco 7 do roteiro (`docs/roteiro_facilitador.md:99`) manda abrir o expander de
  fontes ao vivo, e a marcação "✅ citado" é o resultado visível dos tickets #1/#3/#4. Na configuração
  padrão de hoje (`config.py:17`, `qwen2.5:1.5b` desde o #19), a demonstração mais provável é uma
  resposta sem nenhuma citação em que o app afirma que as quatro fontes foram citadas — o oposto da
  lição de rastreabilidade que o bloco quer passar. Além disso, a instabilidade entre execuções faz com
  que a evidência de 8.7 mude de conteúdo a cada rodada sem que nada tenha mudado no código.
- **confianca:** alta
- **relacionado:** A1-08 (eixo A1, dono de `rag.py`), A4-05

### A4-07 — A legenda "Caminho usado · k · modelo" some em qualquer rerender; o histórico não guarda k nem modelo

- **severidade:** média
- **categoria:** didatico
- **onde:** `app.py:92` (`st.caption`, dentro do bloco `if pergunta:`), `app.py:73-77` (laço que
  rerenderiza o histórico, sem legenda), `app.py:102` (`**busca` salvo em `session_state`, sem `k` nem
  `modelo`)
- **criterio:** 8.3, 8.4, 8.6
- **o-que-observei:** a legenda é emitida só no ramo que processa uma pergunta nova. Como o Streamlit
  reexecuta o script inteiro a cada interação de widget, mover o slider de k, trocar o rádio de busca,
  marcar um filtro ou trocar o modelo apaga a legenda de **todas** as respostas já na tela. Confirmado
  na sonda: logo após responder havia 1 legenda; depois de um único `set_value` no slider e um rerun,
  0 legendas, com o histórico intacto (2 mensagens) e o expander ainda lá. O `caminho` sobrevive porque
  está duplicado no rótulo do expander (`app.py:31`); **k e modelo não sobrevivem em lugar nenhum**.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A4-sonda.py apptest
  ```
- **saida-obtida:**
  ```
  == A4-S2 pergunta padrao (Simples, k=4, sem filtro) ==
    [logo apos responder] legendas 'Caminho usado' visiveis:
        ['Caminho usado: busca simples · k = 4 · modelo qwen2.5:1.5b']
    [logo apos responder] expanders: ['Fontes (citadas 4 de 4) — busca simples']

  == A4-S3 rerender do historico: mexe no slider k e roda de novo, sem perguntar ==
    [apos rerun] legendas 'Caminho usado' visiveis: []
    [apos rerun] expanders: ['Fontes (citadas 4 de 4) — busca simples']
    mensagens no historico: 2
  ```
- **por-que-importa:** o passo 4 do bloco 7 do roteiro (`docs/roteiro_facilitador.md:98`) é
  "Mudar o k, filtrar por tema, alternar simples × dois estágios". A comparação que esse passo quer
  mostrar depende de ver a resposta antiga e a nova lado a lado com seus parâmetros — e é exatamente o
  ato de mudar o parâmetro que apaga a legenda da resposta anterior. Também é o motivo de a captura
  `8.6_modo_dois_estagios.png` (A4-03) não ter legenda nenhuma.
- **confianca:** alta
- **relacionado:** A4-03, A4-08

### A4-08 — O seletor de modelo duplica a opção quando `MODELO_CHAT` vem do ambiente igual ao plano B

- **severidade:** média
- **categoria:** correcao
- **onde:** `app.py:52` (`st.selectbox("Modelo de chat", [config.MODELO_CHAT, config.MODELO_CHAT_PLANO_B])`),
  `config.py:17-18`
- **criterio:** 8.1
- **decisao-documentada:** `docs/roteiro_facilitador.md:103` registra a decisão do autor no ticket #14:
  "o seletor de modelo (`st.selectbox("Modelo de chat", ...)`) e o botão 'Limpar conversa' **ficam no
  app**, contra a recomendação do ticket de tirar o seletor — o autor prefere poder trocar de modelo ao
  vivo na demo". A decisão é sobre **manter** o seletor; ela não trata da lista de opções, que é
  montada com o plano B fixo em código e por isso colide com `MODELO_CHAT` sempre que os dois coincidem.
- **o-que-observei:** a lista é `[config.MODELO_CHAT, config.MODELO_CHAT_PLANO_B]`, e
  `MODELO_CHAT_PLANO_B` é uma constante literal (`"qwen2.5:3b"`), não uma função do modelo ativo. Com
  `MODELO_CHAT=qwen2.5:3b` — que é o que o `README.md:5` descreve como padrão e o que qualquer um fará
  para testar o 3b antes do ensaio de 21/09 — o seletor fica com duas opções idênticas e o `1.5b`
  desaparece da UI, ou seja, o plano B fica inalcançável ao vivo justamente no cenário em que ele seria
  necessário (máquina não aguentando o 3b). Não há exceção: o app sobe normalmente.
- **como-reproduzir:**
  ```bash
  MODELO_CHAT=qwen2.5:3b   .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A4-sonda.py selectbox
  MODELO_CHAT=qwen2.5:1.5b .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A4-sonda.py selectbox
  MODELO_CHAT=llama3.2:3b  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A4-sonda.py selectbox
  ```
- **saida-obtida:**
  ```
  MODELO_CHAT='qwen2.5:3b'    opcoes do seletor: ['qwen2.5:3b', 'qwen2.5:3b']    opcoes distintas: 1 de 2
  MODELO_CHAT='qwen2.5:1.5b'  opcoes do seletor: ['qwen2.5:1.5b', 'qwen2.5:3b']  opcoes distintas: 2 de 2
  MODELO_CHAT='llama3.2:3b'   opcoes do seletor: ['llama3.2:3b', 'qwen2.5:3b']   opcoes distintas: 2 de 2
  ```
- **por-que-importa:** o critério 9.3 está ⏸️ esperando a decisão do modelo ao vivo no ensaio de 21/09,
  e a forma natural de testar é `MODELO_CHAT=qwen2.5:3b`. Nessa configuração o seletor — que o autor
  fez questão de manter para poder trocar ao vivo — deixa de oferecer o outro modelo. O terceiro caso
  mostra que o plano B também não acompanha um modelo qualquer definido pelo ambiente.
- **confianca:** alta
- **relacionado:** A4-07

### A4-09 — Com os modelos frios, a primeira resposta do bloco Streamlit levou 310 s; com modelo quente, 44–54 s

- **severidade:** média
- **categoria:** risco-ao-vivo
- **onde:** `ferramentas/testar_app.py:37-39`, `docs/evidencias/E8/apptest.txt:4`,
  `docs/roteiro_facilitador.md:100` ("No máximo 4 perguntas neste bloco")
- **criterio:** 8.2, 9.4
- **o-que-observei:** rodei a mesma suíte que produziu `docs/evidencias/E8/apptest.txt`, com o servidor
  Ollama de pé mas sem nenhum modelo carregado. A primeira pergunta levou **310 s**; as três seguintes,
  na mesma sessão, 54 s, 32 s e 12 s. A execução versionada (00:16, modelos já quentes de execuções
  anteriores) registra 44 s para a mesma primeira pergunta. A diferença é a carga do `bge-m3` e do
  `qwen2.5:1.5b` na hora do primeiro uso. A segunda medição, com os modelos quentes, confirma que os
  310 s são de carga fria e não de degradação permanente: na sonda subsequente a mesma classe de
  pergunta respondeu em 48 s.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python ferramentas/testar_app.py
  ```
- **saida-obtida:**
  ```
  # 2026-09-16 04:27, modelos frios (esta auditoria)
  8.2 pergunta 1 respondida em 310s | exceção: False | erros: []
      pergunta 2 (só k) respondida em 54s
      pergunta 3 (só modo) respondida em 32s
      pergunta 4 (só filtro) respondida em 12s
  # docs/evidencias/E8/apptest.txt, 2026-09-16 00:16, modelos quentes
  8.2 pergunta 1 respondida em 44s
  ```
- **por-que-importa:** o bloco 7 tem 15 min no cronograma. Se o Streamlit for aberto sem que o `bge-m3`
  e o modelo de chat já estejam carregados, a primeira pergunta pode consumir um terço do bloco na
  frente da turma. O roteiro já manda aquecer com `scripts/07_ollama.py` (`:11`), mas esse passo aquece
  o modelo de chat, e a primeira operação do app é um embedding com `bge-m3`. O número publicado em
  `docs/medicoes.md` para o app é o de modelo quente.
- **confianca:** média (duas medições, uma fria e uma quente; a fria não foi repetida porque exigiria
  descarregar os modelos do Ollama, o que afetaria as outras verificações da rodada)
- **relacionado:** A5 (números de `docs/medicoes.md`)

### A4-10 — A execução que gerou as capturas não terminou, e nada no script torna isso visível

- **severidade:** baixa
- **categoria:** evidencia
- **onde:** `ferramentas/capturar_evidencias_e8.py:154-165` (o `capturas.txt` só é escrito depois dos
  dois cenários), `:138-151` (cenário 8.8), `docs/evidencias/E8/capturas/`
- **criterio:** 8.8
- **o-que-observei:** a pasta tem 8 PNGs e nem `8.8_ollama_indisponivel.png` nem `capturas.txt`. O
  `capturas.txt` é o único lugar que diria qual PNG prova qual critério; sem ele, as capturas são
  imagens soltas com nome de arquivo como única legenda. Como `_capturar` escreve cada PNG na hora
  (`:64-68`) e o índice só no fim (`:161-164`), uma execução interrompida deixa exatamente este
  estado — parcial e indistinguível de um conjunto completo para quem só olhar a pasta.
- **como-reproduzir:**
  ```bash
  ls docs/evidencias/E8/capturas/
  ```
- **saida-obtida:**
  ```
  8.2a_antes_de_perguntar.png     8.4a_k2.png   8.5_filtro_tema_limitacoes.png
  8.2b_streaming_em_curso.png     8.4b_k6.png   8.6_modo_dois_estagios.png
  8.2c_resposta_completa.png                    8.7_expander_citado.png
  (sem 8.8_ollama_indisponivel.png, sem capturas.txt)
  ```
- **por-que-importa:** 8.8 é o único critério de E8 cujo comportamento eu confirmei estar correto e
  cuja captura simplesmente não existe (ver "O que se sustenta"). E sem `capturas.txt` o conjunto não
  se auto-documenta, o que é o que permitiu os erros de A4-01 e A4-03 passarem despercebidos.
- **confianca:** alta
- **relacionado:** A4-04

### A4-11 — `_esperar_resposta` pode liberar a captura antes de a resposta terminar

- **severidade:** baixa
- **categoria:** correcao
- **onde:** `ferramentas/capturar_evidencias_e8.py:46` (`_CONTAGEM_JS`), `:49-56` (`_perguntar`),
  `:59-61` (`_esperar_resposta`), `docs/evidencias/E8/capturas/8.4a_k2.png`
- **criterio:** 8.4
- **decisao-documentada:** o `why:` de `capturar_evidencias_e8.py:50-52` explica a escolha:
  "`wait_for_selector("text=Fontes (citadas")` casaria com o expander de uma resposta ANTERIOR (já
  presente no histórico) em vez de esperar a nova — por isso conta quantos existem antes de perguntar e
  espera esse número aumentar, não só 'existir'". A decisão resolve o caso de um rótulo antigo
  **estático**, mas não o caso em que a contagem sobe sem que uma resposta nova tenha terminado: durante
  o rerun o Streamlit pode manter o nó antigo e montar o novo em paralelo, e a condição `> antes` já é
  satisfeita.
- **o-que-observei:** `8.4a_k2.png` mostra **dois** rótulos idênticos `Fontes (citadas 1 de 4) — busca
  simples` empilhados e, abaixo deles, uma resposta ainda em streaming (texto truncado em "Quais
  problemas aparecem quando"). Ou seja, a captura foi disparada quando a contagem subiu de 1 para 2 por
  duplicação de nó, não porque a resposta seguinte tivesse ficado pronta.
- **como-reproduzir:** abrir `docs/evidencias/E8/capturas/8.4a_k2.png`.
- **saida-obtida:**
  ```
  8.4a_k2.png : dois expanders "Fontes (citadas 1 de 4) — busca simples" consecutivos
                + bolha do assistente com texto parcial "Quais problemas aparecem quando"
                + legenda "Caminho usado: busca simples · k = 4 · modelo qwen2.5:1.5b"
  ```
- **por-que-importa:** é a mecânica que torna as capturas não confiáveis mesmo depois de corrigido o
  problema do slider (A4-01): a espera pode terminar cedo e fotografar um estado intermediário.
- **confianca:** média (o comportamento é inferido da imagem; não reproduzi a duplicação de nó
  instrumentando o DOM)
- **relacionado:** A4-01, A4-02

### A4-12 — `full_page=True` não captura a rolagem interna do Streamlit; 8.5, 8.6 e 8.7 saem cortadas

- **severidade:** baixa
- **categoria:** evidencia
- **onde:** `ferramentas/capturar_evidencias_e8.py:65-66` (`pagina.screenshot(..., full_page=True)`),
  `ferramentas/capturar_app.py:54`
- **criterio:** 8.5, 8.6, 8.7
- **o-que-observei:** os 8 PNGs têm todos a altura do viewport (900 px), inclusive os marcados
  `full_page=True`. O Streamlit rola o conteúdo num contêiner interno, não no `body`, então o
  `full_page` do Playwright não estende nada. Nas três capturas com o expander aberto (8.5, 8.6, 8.7) o
  enquadramento cai no meio da lista de trechos: não aparece a pergunta, nem a resposta, nem o cabeçalho
  do expander com o contador.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python -c "from PIL import Image; import glob; [print(f, Image.open(f).size) for f in sorted(glob.glob('docs/evidencias/E8/capturas/*.png'))]"
  ```
- **saida-obtida:** todos os arquivos com 1440×900, o mesmo tamanho do `viewport` declarado em
  `capturar_evidencias_e8.py:76`, apesar de `full_page=True`.
- **por-que-importa:** amplifica A4-03: mesmo quando o app mostra a indicação certa, a captura pode não
  pegá-la. Uma evidência de tela precisa enquadrar a afirmação que ela sustenta.
- **confianca:** média (a medida do tamanho dos PNGs é direta; a explicação pelo contêiner de rolagem é
  inferência a partir do conteúdo recortado das três imagens)
- **relacionado:** A4-03

### A4-13 — O parâmetro `interagir` de `capturar_app.py` é código morto: o ticket para o qual ele foi criado não o usa

- **severidade:** baixa
- **categoria:** correcao
- **onde:** `ferramentas/capturar_app.py:38-40` (comentário `why:`), `:41` (assinatura), `:52-53` (uso),
  `ferramentas/capturar_evidencias_e8.py:16` (importa só `subir_app`), `:71-81` e `:141-145`
- **criterio:** —
- **decisao-documentada:** o `why:` de `capturar_app.py:38-40` diz: "`interagir` existe para T15
  (capturas reais 8.2/8.4/8.5/8.6/8.7/8.8), que precisa mexer em sliders/filtros/chat antes do PNG —
  sem isso, `capturar_app.py` só serviria para a tela inicial e **T15 duplicaria
  `subir_app()`/o boilerplate do Playwright**". O T15 foi escrito e duplicou o boilerplate assim mesmo:
  `capturar_evidencias_e8.py` importa apenas `subir_app` e reimplementa `sync_playwright()`,
  `launch(channel="msedge")`, `new_page(viewport=…)`, `goto`, `wait_for_selector` e `screenshot` duas
  vezes (cenários principais e cenário 8.8). A justificativa registrada, portanto, não se realizou.
- **o-que-observei:** `interagir` não tem nenhum chamador. O único uso de `capturar()` é o `__main__` do
  próprio arquivo (`:65`), que não passa o parâmetro.
- **como-reproduzir:**
  ```bash
  grep -rn "interagir" --include=*.py .
  ```
- **saida-obtida:**
  ```
  ferramentas/capturar_app.py:38:# why: `interagir` existe para T15 …
  ferramentas/capturar_app.py:41:def capturar(caminho_png, porta=PORTA, timeout_ms=60000, interagir=None):
  ferramentas/capturar_app.py:52:            if interagir:
  ferramentas/capturar_app.py:53:                interagir(pagina)
  (nenhum chamador passa `interagir`)
  ```
- **por-que-importa:** ruído pequeno, mas é um `why:` que descreve um mundo que não aconteceu — e este
  repositório trata os `why:` como fonte de decisão registrada, inclusive nesta auditoria.
- **confianca:** alta

### A4-14 — A única evidência de navegador de 8.7 descreve uma UI que o app não produz mais

- **severidade:** baixa
- **categoria:** documentacao
- **onde:** `docs/evidencias/E8/ui_navegador.txt:29-41`, `app.py:31`
- **criterio:** 8.7
- **o-que-observei:** o arquivo (2026-09-14) documenta o expander como `Fontes (4) — busca simples` e
  lista 4 trechos sem nenhuma marcação de citação. Desde o T04 (2026-09-15) o rótulo é
  `Fontes (citadas X de Y) — <caminho>` e cada trecho citado leva "✅ citado". O arquivo também é de
  `qwen2.5:3b` e do corpus de 6 artigos (distância 0.3150 para `liu2023_lost_middle.pdf` p.1, contra
  0.3721 no índice atual de 659 vetores).
- **como-reproduzir:**
  ```bash
  grep -n "Fontes (4)" docs/evidencias/E8/ui_navegador.txt
  grep -n "citadas" app.py
  ```
- **saida-obtida:**
  ```
  docs/evidencias/E8/ui_navegador.txt:29:## 8.7 — expander de fontes aberto (texto da mensagem após clicar em "Fontes (4) — busca simples")
  docs/evidencias/E8/ui_navegador.txt:34:Fontes (4) — busca simples
  app.py:31:    with st.expander(f"Fontes (citadas {len(citadas)} de {len(fontes)}) — {busca['caminho']}"):
  ```
- **por-que-importa:** quem for conferir 8.7 pela evidência versionada vai procurar na tela um rótulo
  que não existe mais, e não vai encontrar a marcação "✅ citado", que é o que o critério passou a
  demonstrar depois do T04.
- **confianca:** alta
- **relacionado:** A4-02, A4-04

---

## O que se sustenta (verificado ao vivo nesta rodada, sem achado)

Registrado porque a ausência de achado também precisa de evidência:

- **8.1** — `AppTest` sobe o app sem exceção e sem avisos (`8.1 app carregou sem exceção: True |
  avisos: []`), e `subir_app()` (porta 8502) obteve HTTP 200 na sonda do slider. Processo derrubado ao
  fim (`processo.terminate()`, `capturar_app.py:56-58`).
- **8.3** — histórico persiste: 4 mensagens com papéis `['user','assistant','user','assistant']`, e o
  rerender mantém os expanders das respostas anteriores (o histórico sobreviveu inclusive ao rerun de
  A4-S3 e ao erro de Ollama de A4-S6).
- **8.4 / 8.5 / 8.6 no comportamento** — as três rodadas isoladas de `testar_app.py` passaram sem
  `FALHA`: k=5 devolveu 5 resultados; o modo "Dois estágios" produziu `caminho='dois estágios'` com
  `['liu2023_lost_middle.pdf', 'karpukhin2020_dpr.pdf', 'medeiros2025_embeddings_pt.pdf']` no estágio 1;
  o filtro `tema ∈ [avaliacao, limitacoes]` devolveu só `['limitacoes']`.
- **Filtro que zera o resultado** (Ano mínimo = 2026, os dois modos) — o app não quebra e não alucina:
  `resultados=0`, o modelo responde a recusa exata, o expander mostra
  `Fontes (citadas 0 de 0)` e o aviso `Nenhum trecho recuperado com esses filtros.`. No modo dois
  estágios o rótulo carrega o motivo completo
  (`busca simples (estágio 1 sem correspondência: nenhum resumo com esse filtro)`).
- **Recusa** — `citadas=[]`, rótulo `Fontes (citadas 0 de 5)` e aviso `Nenhuma fonte usada`, em duas
  execuções independentes.
- **8.8 no comportamento** — com `OLLAMA_HOST=http://localhost:1` o app sobe, mostra o aviso amarelo na
  barra superior e, ao perguntar, um `st.error` com a instrução de abrir o Ollama; `excecao nao
  tratada=False`, histórico em 0 mensagens. Com o Ollama caindo **no meio da conversa** (cliente
  apontado para porta morta após 3 respostas bem-sucedidas), o `except` de `app.py:103-105` trata o
  erro e o `pop()` remove a pergunta órfã: histórico de 6 mensagens antes e 6 depois, sem exceção.
  Falta só a **captura** (A4-10).
- **Botão "Limpar conversa"** (`app.py:59-60`) — zera `st.session_state.mensagens` e os expanders no
  mesmo rerun (`mensagens apos clique: 0`, `expanders apos clique: []`, sem exceção). Não havia
  cobertura automatizada disso em `testar_app.py`.
- **k maior que o número de chunks do filtro** — nenhuma combinação de filtros da barra lateral produz
  entre 1 e 9 chunks neste corpus (as combinações dão 0 ou ≥ 48 páginas), então o caso degenera no
  "filtro que zera o resultado", já coberto acima. Contagens conferidas direto na coleção
  (`tipo_chunk=pagina`: 651; por tema 88/259/136/87/81; por idioma 550 en / 101 pt; por ano
  159/391/101).

---

## Não verificado

- **Streaming visto de fato** (critério 8.2): eu não capturei a tela com texto crescendo. O `AppTest`
  não expõe os pedaços do `st.write_stream`, e gerar uma captura nova exigiria escrever em
  `docs/evidencias/E8/`, o que o protocolo proíbe ao auditor. Fica como
  `não-verificável-sem-efeito-colateral` no que diz respeito a **produzir** a evidência; o que eu pude
  fazer foi mostrar que a evidência existente não serve (A4-02).
- **Captura 8.8**: mesma razão. O comportamento foi verificado por `AppTest` (ver "O que se sustenta"),
  a captura não foi produzida.
- **Trocar o modelo no seletor com chamada real ao `qwen2.5:3b`**: não exercitei uma resposta completa
  com o plano B. A máquina tem 7,9 GB e carregar um segundo modelo enquanto o `bge-m3` e o `1.5b` estão
  residentes custa 40–80 s e degradaria as medições de A4-09 e de outros eixos
  (`docs/roteiro_facilitador.md:102`). Verifiquei só a composição da lista de opções (A4-08).
- **`streamlit run app.py` com navegador humano**: usei `AppTest` e Playwright/msedge. Não testei o
  comportamento relatado em `docs/roteiro_facilitador.md:101` ("o envio é pelo botão de seta; nos
  testes, o Enter não enviou") — se isso ainda vale, é uma pegadinha ao vivo que ninguém reverificou
  desde 2026-09-14.
- **8.1 com log de servidor novo**: `docs/evidencias/E8/streamlit_servidor.log` é de 2026-09-14, porta
  8501, e contém um `ConnectionResetError` do asyncio no Windows anotado como ruído. Não gerei log novo
  (seria escrita em `docs/evidencias/`).
- **Concorrência de sessões** (duas abas do mesmo app ao mesmo tempo, que é o cenário de quem replica
  junto com o facilitador): não exercitada. `@st.cache_resource` compartilha a coleção entre sessões e
  eu não medi o efeito de duas perguntas simultâneas no mesmo Ollama.
- **Exceções que não sejam `OllamaIndisponivel`** dentro do bloco `if pergunta:` (`app.py:85-105`): o
  `except` é específico. Um erro de outra natureza deixaria a mensagem do usuário em `session_state`
  sem resposta correspondente. Não encontrei caminho pela UI que produza isso, então não reportei.
- **Causa raiz exata do slider de A4-01** no nível do BaseWeb/React: eu demonstrei o efeito (valor do
  backend não muda), não o mecanismo interno do componente.
