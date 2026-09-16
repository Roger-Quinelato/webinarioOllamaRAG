# Eixo A3 — Material didático — achados (RODADA-1)

**Escopo:** `webinario_rag.ipynb`, `ferramentas/construir_notebook.py`, `ferramentas/executar_notebook.py`,
`scripts/**`, `opcional/**`, `docs/roteiro_facilitador.md` · **Data:** 2026-09-16 ·
**Branch:** `chore/agent-skills-setup` · **Modo:** só leitura

**Pergunta central:** o material roda de ponta a ponta na máquina de quem assiste, na ordem e no tempo do
cronograma, com rede de segurança nas etapas lentas?

Comandos usados, todos sem efeito colateral e sem tocar no Ollama:
`ferramentas/verificar.py e7_saidas`, `e7_estrutura`, leitura do `.ipynb` e do
`docs/evidencias/E7/webinario_rag_offline.ipynb` como JSON, `git log -p -- scripts/03_buscar.py`, e a sonda
[`A3-sonda.py`](A3-sonda.py) (saída literal em [`A3-sonda.txt`](A3-sonda.txt)). Nenhuma reindexação, nenhuma
reexecução do notebook, nenhum `scripts/NN` executado.

Referência de célula: o `.ipynb` tem 40 células, 21 de código. "célula de código #N" é o índice 0-based na
lista de células de código (o mesmo que a sonda imprime), acompanhado do `execution_count` salvo, e sempre
com a linha de `ferramentas/construir_notebook.py` que a gera — o notebook não se edita à mão.

---

### A3-01 — O notebook só lista 6 dos 8 artigos do corpus, e diz que todos vêm do arXiv

- **severidade:** alta
- **categoria:** documentacao
- **onde:** `ferramentas/construir_notebook.py:99-108` (markdown do bloco 2.1, 5ª célula markdown do `.ipynb`);
  `config.py:32-42` (`ARTIGOS_CORPUS`, 8 entradas)
- **criterio:** 1.7, 7.3
- **decisao-documentada:** não há comentário `why:`/`hazard:` na região (`construir_notebook.py:95-116`); a
  única decisão registrada é a do `CLAUDE.md` ("PDFs dos artigos **não são versionados**: o README e o
  notebook trazem os links"), que este trecho deixa de cumprir para 2 dos 8 artigos.
- **o-que-observei:** a linha 99 afirma "`scripts/01_preparar_corpus.py` baixa cada um do arXiv"; a tabela das
  linhas 102-108 tem 6 linhas. Os dois artigos em português acrescentados pelo T12/#12
  (`rocha2025_ragsft.pdf`, `medeiros2025_embeddings_pt.pdf`) não aparecem em nenhuma célula markdown do
  notebook, e os dois não vêm do arXiv: `config.py:40-41` aponta para `sol.sbc.org.br`. O gerador tem 6
  ocorrências de `arxiv.org` e nenhuma de `sol.sbc.org.br`. O bloco 3.2 (`construir_notebook.py:219`) até
  menciona "6 artigos + 2 em português", mas sem nome de arquivo e sem link.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py   # seção A3-01
  ```
- **saida-obtida:**
  ```
  lewis2020_rag.pdf                  citado no notebook: True
  ...
  rocha2025_ragsft.pdf               citado no notebook: False
  medeiros2025_embeddings_pt.pdf     citado no notebook: False
  config.ARTIGOS_CORPUS tem 8 artigos; metadados.csv tem 8 linhas
  ocorrências de 'arxiv.org' em construir_notebook.py: 6
  ocorrências de 'sol.sbc.org.br' em construir_notebook.py: 0
  ```
- **por-que-importa:** o notebook é um dos dois lugares que carregam os links do corpus, justamente porque os
  PDFs não são versionados. Quem replicar em casa lendo o notebook vê um corpus de 6 artigos do arXiv; a
  célula seguinte (`construir_notebook.py:113-116`) imprime 8 linhas do CSV e a de chunks imprime 8 artigos,
  incluindo dois nomes que a tabela nunca apresentou. Ao vivo, é o bloco 2 começando com uma contradição
  visível na tela.
- **confianca:** alta
- **relacionado:** A5 (README e docs citam o corpus de 8)

### A3-02 — No bloco 5, "Fontes citadas" e "Trechos enviados ao prompt" saem idênticos, palavra por palavra

- **severidade:** alta
- **categoria:** risco-ao-vivo
- **onde:** `ferramentas/construir_notebook.py:314-336` (célula de código #16, `execution_count=17`);
  `rag.py:365`; `config.py:17`
- **criterio:** 6.5, 7.2
- **decisao-documentada:** `construir_notebook.py:321-326` (`why:`) diz que mostrar todo o top-k como
  "Fontes" mistura o que entrou no prompt com o que a resposta citou, e que por isso os dois blocos ficam
  separados; `rag.py:359-365` (`hazard:`) documenta o fallback "se o modelo não citou nenhum, cai para os
  recuperados, para nunca ficar sem fontes". Nenhuma das duas decisões cobre o caso observado: as duas
  regras, combinadas com o modelo que o #19 tornou padrão, produzem **duas listas idênticas sob dois
  rótulos diferentes**, que é pior para a didática do que o problema que o `why:` foi escrito para resolver
  — o espectador lê "Fontes citadas" e "Trechos enviados ao prompt" com o mesmo conteúdo e conclui que o
  modelo citou os quatro.
- **o-que-observei:** na saída salva do notebook, a resposta "Com contexto" do bloco 5 não contém nenhuma
  citação `[n]`, o fallback de `rag.py:365` dispara e os dois blocos exibidos ficam byte a byte iguais. A
  mesma execução do notebook mostra `Chat: qwen2.5:1.5b` no bloco 1. No bloco 6 (célula de código #18,
  `execution_count=19`, gerada em `construir_notebook.py:350-367`) o mesmo modelo **citou** `[2]` e a
  separação aparece corretamente — ou seja, a falha é intermitente, não sistemática.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py   # seção A3-02
  ```
- **saida-obtida:**
  ```
  célula de código #16 (execution_count=17)
    citações [n] na resposta 'Com contexto': NENHUMA
    'Fontes citadas'            = ['[1] asai2023_selfrag.pdf, p. 10', ... '[4] asai2023_selfrag.pdf, p. 4']
    'Trechos enviados ao prompt'= ['[1] asai2023_selfrag.pdf, p. 10', ... '[4] asai2023_selfrag.pdf, p. 4']
    os dois blocos são idênticos? True
  célula de código #18 (bloco 6, execution_count=19)
    'Fontes:' (citadas)         = ['[2] gao2023_survey.pdf, p. 12']
    'Trechos enviados ao prompt'= ['[1] asai2023_selfrag.pdf, p. 1', ... '[4] lewis2020_rag.pdf, p. 5']
    os dois blocos são idênticos? False
  ```
- **por-que-importa:** os tickets #1/#3/#4 existiram para que o material ensinasse a diferença entre
  "contexto oferecido" e "fonte usada". O notebook versionado — que é o que o participante abre depois e o
  que aparece na tela ao vivo — ensina o contrário no bloco 5 e o correto no bloco 6, com dois rótulos e um
  conteúdo só. É o critério 6.5 demonstrado invertido na frente da turma.
- **confianca:** alta
- **relacionado:** A1-08 (é a manifestação dele no notebook), A4 (a mesma regra na tela do Streamlit)

### A3-03 — `REINDEXAR = False` não impede a reindexação, e o comentário promete "alguns minutos" para 1420 s

- **severidade:** alta
- **categoria:** risco-ao-vivo
- **onde:** `ferramentas/construir_notebook.py:149` (célula de código #5, `execution_count=6`) e
  `ferramentas/construir_notebook.py:52` (comentário de `REINDEXAR`); `docs/roteiro_facilitador.md:37`,
  `docs/roteiro_facilitador.md:42`
- **criterio:** 7.6, 9.4, 10.2
- **decisao-documentada:** não há `why:`/`hazard:` na região (`construir_notebook.py:147-156`). A decisão
  registrada em sentido contrário é a do roteiro (`:42`): "**Nunca reindexar ao vivo**".
- **o-que-observei:** a condição é `if REINDEXAR or colecao.count() != len(chunks):` → `rag.indexar(chunks)`.
  Com `REINDEXAR = False` (valor salvo na célula de configuração), qualquer divergência entre a contagem da
  coleção e os 659 chunks dispara a reindexação completa sem confirmação. O roteiro, no item 4 do bloco 2,
  instrui o facilitador assim: "Com `REINDEXAR = False`, ela só reabre a coleção" — o que só é verdade
  enquanto as contagens baterem. O comentário da linha 52 descreve a operação como "alguns minutos em CPU";
  a medição do corpus atual em `docs/evidencias/E7/log_02_indexar.txt:30` é `659 vetores … em 1420.0s`
  (23,7 min), contra 1080 s do bloco 2 inteiro.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py   # seção A3-08
  ```
- **saida-obtida:**
  ```
    colecao = rag.abrir_colecao()
    if REINDEXAR or colecao.count() != len(chunks):
        inicio = time.perf_counter()
        colecao = rag.indexar(chunks)
    REINDEXAR na célula de configuração: ['False']
    -> com REINDEXAR=False, rag.indexar() ainda dispara se colecao.count() != len(chunks)
  ```
- **por-que-importa:** duas consequências distintas. Ao vivo: uma coleção parcial (indexação interrompida,
  `chroma_db/` copiado pela metade, mudança em `TAMANHO_CHUNK`) põe a aula dentro de uma espera de ~24 min
  no bloco de 18 min, exatamente o cenário que o roteiro manda nunca acontecer, e o facilitador foi
  instruído a confiar no `REINDEXAR = False`. Em casa: quem abre o notebook com `chroma_db/` vazio (o
  diretório é `.gitignore`) cai na mesma célula achando, pelo comentário, que espera "alguns minutos".
- **confianca:** alta
- **relacionado:** A3-07, A6 (primeira execução em máquina limpa)

### A3-04 — O plano B do bloco 5 troca a alucinação ao vivo por uma recusa, e o ponto da aula desaparece

- **severidade:** alta
- **categoria:** didatico
- **onde:** `ferramentas/construir_notebook.py:314-320` (célula de código #16, ramo `else` do `LLM_AO_VIVO`);
  `resultados/com_sem_contexto.json`; `docs/roteiro_facilitador.md:80-81`
- **criterio:** 6.3, 7.6
- **decisao-documentada:** nenhum `why:`/`hazard:` cobre o ramo offline (o `why:` de
  `construir_notebook.py:321-326` trata só da separação das fontes).
- **o-que-observei:** comparando o notebook ao vivo com a cópia `--offline`
  (`docs/evidencias/E7/webinario_rag_offline.ipynb`), a mesma célula #16 muda de conteúdo: ao vivo a resposta
  "Sem contexto" é uma alucinação completa (o modelo lista `self`, `this`, `super`, `cls` como "tokens de
  reflexão do Self-RAG"); no ramo offline, a resposta salva para a mesma pergunta é
  `"Desculpe, mas não tenho informações específicas sobre tokens de reflexão propostos no Self-RAG."` — uma
  recusa educada, não uma invenção. O roteiro, no bloco 5, tem como checkpoint "Onde a resposta sem contexto
  inventou algo?" (`:80`) e como plano B exatamente `LLM_AO_VIVO = False` (`:81`).
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py   # seção A3-10, célula #16
  ```
- **saida-obtida:**
  ```
  #16 ≠ ao vivo  2276 chars | offline  1133 chars | 'if LLM_AO_VIVO:'
  ```
  ```
  CELULA 16 AO VIVO:   ### Sem contexto
  Os tokens de reflexão (reflection tokens) propostos no Self-RAG são:
  1. "self": Representa a instância do objeto atual. …
  CELULA 16 OFFLINE:   ### Sem contexto
  Desculpe, mas não tenho informações específicas sobre tokens de reflexão propostos no Self-RAG. …
  ```
- **por-que-importa:** o plano B do bloco mais didático da aula não reproduz o que a célula ao vivo mostra.
  Se o LLM travar no bloco 5 — o cenário para o qual o plano B foi escrito — o facilitador faz a pergunta do
  checkpoint e a resposta salva não tem invenção nenhuma para apontar. A primeira pergunta salva no mesmo
  JSON (Lost in the Middle) tem uma invenção clara, mas não é a que a célula do notebook usa.
- **confianca:** alta
- **relacionado:** A3-05

### A3-05 — Bloco 2.5 não tem saída pré-computada: com `LLM_AO_VIVO = False` o resumo ao vivo some

- **severidade:** média
- **categoria:** didatico
- **onde:** `ferramentas/construir_notebook.py:182-191` (célula de código #7, `execution_count=8`);
  `docs/roteiro_facilitador.md:39`, `docs/roteiro_facilitador.md:42`
- **criterio:** 7.6
- **decisao-documentada:** não há `why:`/`hazard:` na região (`construir_notebook.py:176-191`).
- **o-que-observei:** a célula tem `if LLM_AO_VIVO: … print(f"RESUMO AO VIVO …")` **sem ramo `else`** e sem
  nenhum `carregar_resultado(...)`. Na cópia `--offline` a célula imprime só o abstract e o
  `RESUMO NO CSV`; a linha `RESUMO AO VIVO` não existe. O roteiro lista, no bloco 2, o item de demo
  "6. Resumo do abstract ao vivo × resumo salvo no CSV" (`:39`) e manda cair para `LLM_AO_VIVO = False`
  quando "extração ou resumo" estiverem lentos (`:42`) — a comparação que é o item de demo desaparece
  exatamente quando o plano B é acionado.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py   # seção A3-10, célula #7
  ```
- **saida-obtida:**
  ```
  #7 ≠ ao vivo  1806 chars | offline  1014 chars | 'primeira = rag.extrair_paginas(config.PASTA_ARTIGOS '
  ```
  ```
  CELULA 7 OFFLINE:
  ABSTRACT: While recent language models have the ability to take long contexts as input, …
  RESUMO NO CSV: The study found that recent language models struggle with using longer input contexts …
  ```
- **por-que-importa:** o critério 7.6 pede saída pré-computada para **toda** etapa lenta. Esta é lenta
  (8,9 s quente no notebook atual, 232,2 s frio segundo `docs/medicoes.md:50`), está listada por
  `verificar.py e7_estrutura` como coberta — porque a checagem só procura a presença da chave
  `LLM_AO_VIVO`, não um caminho alternativo — e não tem rede nenhuma. Falha silenciosa: a célula não quebra,
  só perde metade do que ela existe para mostrar.
- **confianca:** alta
- **relacionado:** A2 (`e7_estrutura` aceita a chave como prova de rede de segurança)

### A3-06 — O roteiro planeja o bloco 2 com 16,6 s de extração; as quatro medições seguintes dão 106–191 s

- **severidade:** média
- **categoria:** documentacao
- **onde:** `docs/roteiro_facilitador.md:41`
- **criterio:** 9.4, 10.2
- **o-que-observei:** o roteiro diz "**Tempo medido:** extração 16,6 s e resumo 8,1 s com o modelo aquecido;
  135 s e 232 s frios". Os 16,6 s são a primeira execução salva do notebook (corpus de 6 artigos,
  `qwen2.5:3b`), registrada em `docs/evidencias/E7/saidas_notebook.txt:28`. As três execuções posteriores do
  mesmo arquivo de evidência dão 158,1 s (T08), 106,6 s (T09) e 190,7 s (execução atual, linhas 546, 577 e
  606), e `docs/evidencias/E7/log_02_indexar.txt:35` registra 190,7 s numa execução independente de
  `scripts/02_indexar.py`. `docs/medicoes.md:94` já foi reconciliado para 190,7 s; o roteiro não.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python ferramentas/verificar.py e7_saidas
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py   # seção A3-03, extração independente
  ```
- **saida-obtida:**
  ```
  [célula 13] extração: Extração em 190.7s
  [célula 15] resumo ao vivo: RESUMO AO VIVO (8.9s)
  ```
  ```
  bloco 2.4 extração de metadados por LLM    ['190.7']
  bloco 2.5 resumo ao vivo                   ['8.9']
  ```
- **por-que-importa:** o roteiro é o documento que o facilitador lê durante a aula para decidir se aciona o
  plano B. Quem espera 17 s e recebe 3 min de tela parada não sabe se o modelo travou ou se é normal; a
  decisão de acionar `LLM_AO_VIVO = False` depende de saber o tempo esperado. O resumo (8,1 s → 8,9 s) está
  certo; só a extração está fora por uma ordem de grandeza.
- **confianca:** alta (quatro medições independentes, três delas posteriores à escrita da frase)
- **relacionado:** A5 (`docs/medicoes.md:52` ainda repete os 16,6 s como valor "quente")

### A3-07 — O número de "nunca reindexar ao vivo" no roteiro é do corpus de 6 artigos

- **severidade:** média
- **categoria:** documentacao
- **onde:** `docs/roteiro_facilitador.md:42`
- **criterio:** 9.4, 10.2
- **o-que-observei:** o roteiro diz "**Nunca reindexar ao vivo:** leva 1104–1141 s, mais que o bloco
  inteiro". Esse intervalo vem de `docs/medicoes.md:21`, cujas três evidências são
  `E2/02_indexar_execucao1.txt`, `E2/02_indexar_execucao2.txt` e `E7/log_02_indexar.txt` — as duas primeiras
  do corpus de 556 chunks. A única medição existente para o corpus atual de 659 chunks está em
  `docs/evidencias/E7/log_02_indexar.txt:30`: `659 vetores na coleção 'artigos_rag' em 1420.0s`, +25% a +29%
  sobre o intervalo publicado.
- **como-reproduzir:**
  ```bash
  grep -n "1104\|1141\|1420" docs/roteiro_facilitador.md docs/medicoes.md docs/evidencias/E7/log_02_indexar.txt
  ```
- **saida-obtida:**
  ```
  docs/roteiro_facilitador.md:42: **Nunca reindexar ao vivo:** leva 1104–1141 s, mais que o bloco inteiro.
  docs/medicoes.md:21: | Indexação completa com `bge-m3` … | 1141,1 s · 1111,0 s · 1104,1 s |
  docs/evidencias/E7/log_02_indexar.txt:30:    659 vetores na coleção 'artigos_rag' em 1420.0s
  ```
- **por-que-importa:** a conclusão ("não reindexar") não muda, mas o número sustenta uma decisão de risco em
  tempo real, e é o mesmo número que o A3-03 mostra que pode disparar sozinho. 1420 s é 3,7× o bloco 3b
  inteiro; 1104 s já é o dobro.
- **confianca:** média — **uma só medição** para o corpus atual. A segunda exigiria rodar
  `scripts/02_indexar.py`, proibido pelo protocolo (recria a coleção). O que é certo com duas fontes é a
  procedência: os 1104–1141 s são das evidências E2 do corpus de 556 chunks.
- **relacionado:** A3-03, A5 (`docs/medicoes.md:21` e `:87`)

### A3-08 — O plano B geral não cobre o Ollama fora do ar: 8 células buscam embedding sem nenhuma chave

- **severidade:** média
- **categoria:** risco-ao-vivo
- **onde:** `ferramentas/construir_notebook.py:151` (célula #5), `:201` (#8), `:214` (#9), `:226` (#10),
  `:237-238` (#11), `:270` (#13), `:310` (#15), `:352` (#18); `docs/roteiro_facilitador.md:16`
- **criterio:** 7.6, 10.2
- **decisao-documentada:** não há `why:`/`hazard:` em nenhuma dessas células dizendo que as chaves cobrem só
  o modelo de chat. O `why:` de `construir_notebook.py:321-326` e o de `:364-365` tratam de outro assunto.
- **o-que-observei:** o roteiro afirma, no plano B geral, "Todas as células lentas carregam o resultado
  salvo em `resultados/`". Oito células de código chamam `rag.buscar()`, `rag.buscar_dois_estagios()` ou
  `rag.indexar()` **fora** de qualquer ramo `if LLM_AO_VIVO` / `if SHAP_AO_VIVO`; todas passam por
  `rag.gerar_embeddings()` e portanto pelo `bge-m3` no Ollama. Duas delas (#13 do SHAP e #18 do bloco 6)
  têm a chave, mas a busca está antes dela. Com o servidor Ollama parado, os blocos 3, 3b, 4, 5 e 6 quebram
  mesmo com `LLM_AO_VIVO = SHAP_AO_VIVO = False`.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py   # seção A3-05
  ```
- **saida-obtida:**
  ```
  célula #13 (tem chave LLM_AO_VIVO/SHAP_AO_VIVO: True)
      FORA da chave  -> chunk = rag.buscar(pergunta, k=1, colecao=colecao)[0]
  célula #15 (tem chave LLM_AO_VIVO/SHAP_AO_VIVO: False)
      FORA da chave  -> resultados = rag.buscar(pergunta, k=config.K_PADRAO, colecao=colecao)
  célula #18 (tem chave LLM_AO_VIVO/SHAP_AO_VIVO: True)
      FORA da chave  -> resultados_bloco6 = rag.buscar(pergunta, colecao=colecao)
  (todas as linhas 'FORA da chave' chamam rag.gerar_embeddings() e portanto o Ollama)
  ```
- **por-que-importa:** o facilitador tem uma única frase de plano B para o caso mais provável de pane ao
  vivo, e ela promete mais do que entrega. As chaves cobrem o modelo de chat (que é o lento); o modelo de
  embedding não tem cobertura nenhuma, e é ele que está no caminho crítico de cinco dos nove blocos. Numa
  máquina com 7,9 GB de RAM, "o Ollama não responde" é o mesmo evento para os dois modelos.
- **confianca:** alta
- **relacionado:** A1-09 (mensagem de erro do Ollama), A3-05

### A3-09 — A rede de segurança dos blocos 4.1 e 8 é de outro corpus e de outro modelo

- **severidade:** média
- **categoria:** evidencia
- **onde:** `resultados/shapley_chunks.json`, `resultados/avaliacao_estilo_ragas.json`;
  `ferramentas/construir_notebook.py:292-297` (célula de código #14) e `:392-398` (célula #20);
  `opcional/calcular_shapley_chunks.py`, `opcional/avaliacao_estilo_ragas.py`
- **criterio:** 5b.1, 7.2, 7.6
- **o-que-observei:** os dois arquivos são de 2026-09-14, anteriores ao T12/#12 (corpus 6→8 artigos,
  556→659 chunks, reindexado em 2026-09-16) e ao #19 (`MODELO_CHAT` 3b→1.5b). O `shapley_chunks.json` grava
  `"modelo": "qwen2.5:3b"`, e a célula #14 imprime isso na tela; a célula #1 da **mesma execução** do
  notebook imprime `Chat: qwen2.5:1.5b`. O `avaliacao_estilo_ragas.json` não grava modelo nem data
  nenhuma — `opcional/avaliacao_estilo_ragas.py:78-80` monta o registro sem esses campos, ao contrário de
  `scripts/02` (`metadados_llm.json`), `scripts/06` (`com_sem_contexto.json`) e
  `opcional/calcular_shapley_chunks.py`, que gravam `modelo`.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py   # seções A3-03 e A3-04
  ```
- **saida-obtida:**
  ```
  modelo de chat anunciado no bloco 1: ['qwen2.5:1.5b']
  modelo do Shapley pré-computado (bloco 4.1): ['qwen2.5:3b']
  ```
  ```
  avaliacao_estilo_ragas.json  existe |  3833 bytes | mtime=2026-09-14 04:54 | modelo=—
  shapley_chunks.json          existe |  8251 bytes | mtime=2026-09-14 03:14 | modelo=qwen2.5:3b
  ```
- **por-que-importa:** os blocos 4.1 e 8 publicam números na tela (valores de Shapley; fidelidade 1,00 e
  0,60; relevância 0,55 e 0,47; precisão 0,75) que não vêm da configuração que a turma está vendo rodar. O
  invariante 6 do `ESTADO_ATUAL.md` ("todo número publicado vem de medição nesta máquina, com data e
  comando") não se sustenta para a tabela do bloco 8, que não tem como ser atribuída a modelo nenhum. O
  top-4 do Shapley ainda bate com o índice atual (asai p.10, asai p.1, gao p.12, asai p.4, iguais aos da
  célula #16), então o problema é de proveniência, não de retrieval quebrado.
- **confianca:** alta
- **relacionado:** A2 (força da evidência de 5b.1), A5

### A3-10 — Rodado fora da ordem, `scripts/03`–`07` sai com 0 e não avisa que o índice não existe

- **severidade:** média
- **categoria:** reprodutibilidade
- **onde:** `scripts/03_buscar.py:9`, `scripts/04_dois_estagios.py:9`, `scripts/05_shap.py:13`,
  `scripts/06_com_sem_contexto.py:19`, `scripts/07_ollama.py:23`; `rag.py:190` (`get_or_create_collection`),
  `rag.py:274`
- **criterio:** 7.5
- **decisao-documentada:** `rag.py:189` tem um `why:` sobre `embedding_function=None`, não sobre o
  `get_or_create`. Nenhum comentário na região trata do caso "coleção ainda não construída".
- **o-que-observei:** `rag.abrir_colecao()` usa `get_or_create_collection`, então um projeto sem
  `chroma_db/` (o diretório é `.gitignore`) não dá erro: cria uma coleção vazia. Exercitei uma coleção
  vazia equivalente num diretório temporário: `_consultar` devolve 0 resultados sem exceção,
  `tabela_resultados([])` imprime `(nenhum resultado)` e `montar_prompt` cai em
  `(nenhum trecho recuperado)`. Consequência por script: `03` e `04` imprimem `(nenhum resultado)` em todos
  os casos e saem com 0; `04` ainda anuncia o caminho de fallback do estágio 1, sugerindo que o limiar
  atuou; `05` itera sobre uma lista vazia, não escreve nenhum `shap_similaridade_chunkN.*` e sai com 0;
  `06` e `07` chamam o LLM com "(nenhum trecho recuperado)" e saem com 0.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A3-sonda.py   # seção A3-07
  ```
- **saida-obtida:**
  ```
  coleção recém-criada: 0 vetores
  buscar (tipo_chunk=pagina)     -> 0 resultados, sem exceção
  estágio 1 (tipo_chunk=resumo)  -> 0 resultados, sem exceção
  rag.tabela_resultados([])            -> '(nenhum resultado)'
  rag.montar_prompt('p', [])[:60]      -> 'Trechos:\n(nenhum trecho recuperado)\n\nPergunta: p'
  ```
- **por-que-importa:** o critério 7.5 é "roda sozinho, em ordem, com código de saída 0" — e o modo de falha
  mais provável para quem replica é justamente **pular a ordem**, porque o passo pulado é o de 24 min
  (`scripts/02`). Quem faz isso recebe exit 0 em cinco scripts seguidos, nenhuma mensagem, e conclui que o
  material está quebrado ou que o corpus não tem o assunto. É o mesmo padrão do A1-00: um sucesso que mente.
- **confianca:** alta
- **relacionado:** A6 (`rodar_scripts.sh`, primeira execução), A1 (`rag.abrir_colecao`)

### A3-11 — `scripts/01` e `scripts/02` seguem sem `rag.cli_seguro()`

- **severidade:** média
- **categoria:** correcao
- **onde:** `scripts/01_preparar_corpus.py:17-65` (nenhum `with rag.cli_seguro():`),
  `scripts/02_indexar.py:18-60` (idem); comparar com `scripts/03_buscar.py:8`,
  `scripts/04_dois_estagios.py:8`, `scripts/05_shap.py:11`, `scripts/06_com_sem_contexto.py:18`,
  `scripts/07_ollama.py:17`, `opcional/calcular_shapley_chunks.py:20`,
  `opcional/avaliacao_estilo_ragas.py:68`
- **criterio:** 6.7, 7.5
- **o-que-observei:** confirmado por leitura integral dos dois arquivos: `scripts/01` chama
  `rag.resumir_abstract` (linha 60) e `scripts/02` chama `rag.indexar` (36) e `rag.extrair_metadados_llm`
  (49) fora de qualquer captura de `OllamaIndisponivel`. Os outros sete scripts do repositório abrem com o
  context manager na primeira linha executável.
- **como-reproduzir:**
  ```bash
  grep -Ln "cli_seguro" scripts/*.py opcional/*.py
  ```
- **saida-obtida:**
  ```
  scripts/00_checar_ambiente.py
  scripts/01_preparar_corpus.py
  scripts/02_indexar.py
  ```
  (`scripts/00` não usa o Ollama por meio de `rag`, trata o erro ele mesmo em `:58-60`.)
- **por-que-importa:** `scripts/02` é o script que quem replica roda primeiro e o que mais demora; se o
  Ollama cair no meio da indexação, o participante recebe um traceback cru em vez da mensagem de
  `rag._erro_ollama`. Registro aqui apenas para fechar o escopo A3 — **não é achado novo**, é exatamente a
  issue #24 já aberta e o critério 6.7 já contestado no `ESTADO_ATUAL.md:200`.
- **confianca:** alta
- **relacionado:** issue #24 (já aberta); A1 (`rag.cli_seguro`)

### A3-12 — Faixa de tempo do SHAP no roteiro não cobre as medições do corpus atual

- **severidade:** baixa
- **categoria:** documentacao
- **onde:** `docs/roteiro_facilitador.md:70`
- **criterio:** 5a.3, 9.4, 10.2
- **o-que-observei:** o roteiro diz "**Tempo medido:** 19–41 s com o `bge-m3` já carregado e até 112 s frio
  ou com pouca RAM". As medições do corpus atual: 50 s no notebook salvo (`e7_saidas`, confirmado pela
  extração independente da sonda e por `docs/evidencias/E5/notebook_E5.txt:16`) e, na mesma execução de
  `scripts/05_shap.py`, 83,3 s para o chunk 1 e 17,8 s para o chunk 2
  (`docs/evidencias/E7/log_05_shap.txt:3` e `:20`). Duas das três medições ficam fora de 19–41 s.
  `docs/medicoes.md:97` já usa a faixa corrigida "19–112 s (50 s na última execução)".
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python ferramentas/verificar.py e7_saidas
  grep -n "SHAP em" docs/evidencias/E7/log_05_shap.txt
  ```
- **saida-obtida:**
  ```
  [célula 27] shap: SHAP em 50s
  3:SHAP em 83.3s
  20:SHAP em 17.8s
  ```
- **por-que-importa:** o bloco 4 tem 12 min e o gatilho do plano B do roteiro é implícito ("com RAM baixa").
  Uma faixa que já está errada no caso quente não serve para decidir se 50 s é normal ou se é hora de
  `SHAP_AO_VIVO = False`. Baixa porque o bloco cabe de qualquer forma.
- **confianca:** alta (três medições, duas independentes entre si)
- **relacionado:** A5

### A3-13 — `scripts/03` e o bloco 3.1 perderam a demonstração do filtro que não casa com nada

- **severidade:** baixa
- **categoria:** didatico
- **onde:** `scripts/03_buscar.py:25`; `ferramentas/construir_notebook.py:212` (célula de código #9)
- **criterio:** 3.6
- **o-que-observei:** o registro de execuções do `VERIFICACAO.md` (linha do T12/#12) afirma que os três
  lugares que assumiam `idioma=pt` sempre vazio foram "trocados para um filtro por ano fora do corpus, que
  continua garantidamente vazio". Isso vale para `ferramentas/verificar.py:114` e `:133` e para
  `scripts/04_dois_estagios.py:40` (`{"ano": {"$gte": 2030}}`), mas o diff do commit `af18c3a` em
  `scripts/03_buscar.py` é **só uma troca de rótulo**; nenhum dos cinco filtros do script devolve vazio hoje.
  O bloco 3.1 do notebook tem o mesmo `{"idioma": "pt"}` e nenhum filtro vazio.
- **como-reproduzir:**
  ```bash
  git log -p -1 --format='%h %s' -- scripts/03_buscar.py
  ```
- **saida-obtida:**
  ```
  af18c3a Avança #12: adiciona 2 artigos em português ao corpus (6 → 8)
  -        "idioma = pt (ainda sem artigos em português)": {"idioma": "pt"},
  +        "idioma = pt (T12/#12: 2 artigos)": {"idioma": "pt"},
  ```
- **por-que-importa:** o critério 3.6 continua coberto por `verificar.py e3` (`3.6 filtro ano>=2030`), então
  nenhum ✅ cai. O que se perdeu é didático: nem o script nem o notebook mostram mais o caso "filtro que não
  casa com nada devolve vazio sem erro", que era o motivo original daquela linha, e o registro de execuções
  descreve para `scripts/03` uma correção que não foi feita ali.
- **confianca:** alta
- **relacionado:** A2 (linha do T12 no Registro de execuções)

### A3-14 — O resumo da bateria `00`–`07` salvo é o de 2026-09-14, do corpus de 6 artigos

- **severidade:** baixa
- **categoria:** evidencia
- **onde:** `ferramentas/rodar_scripts.sh:12-16` (o resumo vai só para stdout);
  `docs/evidencias/E7/sequencia_scripts.txt`
- **criterio:** 7.5
- **o-que-observei:** `rodar_scripts.sh` redireciona a saída de cada script para `log_<nome>.txt` (linha 10),
  mas imprime o resumo por script e o `scripts com falha:` apenas em stdout — não existe arquivo de resumo
  gerado pelo próprio comando. O único resumo salvo, `sequencia_scripts.txt`, é de 2026-09-14 04:09 e traz
  `02_indexar.py → exit 0 em 1260s`, do corpus de 556 chunks. A linha de 2026-09-16 do
  `VERIFICACAO.md` cita `"02_indexar.py → exit 0 em 1420s"` como confirmação da bateria completa, e a nota
  de `docs/evidencias/E7/log_02_indexar.txt:41` repete essa citação — mas esse resumo não está em lugar
  nenhum do repositório.
- **como-reproduzir:**
  ```bash
  grep -rn "1260\|1420" docs/evidencias/E7/sequencia_scripts.txt docs/evidencias/E7/log_02_indexar.txt
  ```
- **saida-obtida:**
  ```
  docs/evidencias/E7/sequencia_scripts.txt:3:04:00:21 scripts/02_indexar.py → exit 0 em 1260s
  docs/evidencias/E7/log_02_indexar.txt:30:   659 vetores na coleção 'artigos_rag' em 1420.0s
  docs/evidencias/E7/log_02_indexar.txt:41:  sucesso (confirmado pelo resumo do rodar_scripts.sh: "02_indexar.py → exit 0 em 1420s"
  ```
- **por-que-importa:** os `log_03`–`log_07` individuais existem e são de 2026-09-16, então a bateria de fato
  rodou; o que falta é o resumo que prova a **sequência e o exit code** — que é literalmente o que o
  critério 7.5 pede. Como o script não salva esse resumo, reproduzi-lo exige rodar a bateria inteira
  (inclusive os 1420 s do `02`), o que o protocolo proíbe nesta rodada.
- **confianca:** alta
- **relacionado:** A2 (evidência de 7.5), A6 (`rodar_scripts.sh`)

---

## Não verificado

- **Execução real do notebook, ao vivo ou `--offline`.** Proibido pelo protocolo (`executar_notebook.py`
  sobrescreve `webinario_rag.ipynb` mesmo com `--offline`, e o caminho offline continua chamando o Ollama
  para embeddings — ver A3-08). Todo achado sobre o notebook vem do JSON salvo e da cópia offline já
  versionada em `docs/evidencias/E7/webinario_rag_offline.ipynb`, que é de 2026-09-15 23:42, anterior à
  última execução ao vivo — a comparação da seção A3-10 da sonda mistura, portanto, duas execuções
  diferentes. As diferenças que reportei (células #7 e #16) são estruturais (um ramo de `if` que não existe,
  um texto que vem de arquivo em vez do modelo), não de variação entre execuções; as das células #5, #6 e
  #13 são variação e foram descartadas.
- **`scripts/00`–`07` e `opcional/*.py` executados.** Todos usam o Ollama e o recurso estava reservado a
  outro eixo. Julguei-os por leitura integral, pelos logs de `docs/evidencias/E7/` e pela sonda de funções
  puras. Em particular, **não** confirmei ao vivo o A3-10: o comportamento com coleção vazia foi
  reproduzido numa coleção temporária equivalente, não rodando os scripts.
- **Reindexação (`scripts/02_indexar.py`).** Proibida. Por isso o A3-07 fica com uma medição só para o
  corpus atual.
- **Tempo de `rag.gerar_chunks()` (célula de código #4).** Medi quatro vezes: 24,3 s, 24,7 s, 19,3 s e
  13,3 s — contra os 8,8 s de `docs/evidencias/E7/log_02_indexar.txt:4`. A variação de 1,9× entre medições
  minhas indica contenção de CPU com outro eixo da auditoria, então não transformei isso em achado: o
  número não é confiável nas condições de hoje, e 25 s dentro de um bloco de 1080 s não muda o cronograma.
  Vale remedir com a máquina ociosa.
- **Cronograma ponta a ponta.** Conferi os blocos 2 e 4 contra tempos medidos. Os blocos 3, 3b, 5, 6, 7 e 8
  não têm, no notebook salvo, nenhum tempo impresso — só o bloco 6 (17,9 s). A afirmação de 9.4 ("cada bloco
  cabe no tempo") depende de `docs/medicoes.md`, que é escopo do A5.
- **`opcional/avaliacao_estilo_ragas.py` e `opcional/calcular_shapley_chunks.py` executados.** ~10 min e
  2^k gerações; nunca rodam ao vivo por decisão do `CLAUDE.md`. Só li o código e os JSON salvos.
- **`ferramentas/executar_notebook.py` com um erro de célula.** A linha 24-25 captura
  `CellExecutionError`, imprime a última linha e **grava o notebook mesmo assim** (`finally`, linha 26-27),
  saindo com 1. Não exercitei o caso, mas o efeito de gravar um notebook parcialmente executado por cima do
  versionado merece um olhar — foi exatamente a regressão descrita na linha do T03 no Registro de execuções.
- **README como porta de entrada do notebook.** O preâmbulo do notebook
  (`ferramentas/construir_notebook.py:33-34`) manda seguir o README para "Ollama, modelos, `.venv`", mas não
  cita `scripts/01` nem `scripts/02` como passos; a primeira célula que abre PDF é a #3
  (`construir_notebook.py:125`). Se o README cobre isso é escopo do A5/A6.
