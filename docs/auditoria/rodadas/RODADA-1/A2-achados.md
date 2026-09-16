# Eixo A2 — Verificação e evidências — achados (RODADA-1)

**Escopo:** `docs/VERIFICACAO.md`, `docs/evidencias/**`, `ferramentas/verificar.py` · **Data:** 2026-09-16 ·
**HEAD:** `eec1ecc` (branch `chore/agent-skills-setup`) · **Modo:** só leitura

**Pergunta central:** cada ✅ tem evidência que realmente demonstra o critério? Alguma checagem passa sem
checar nada?

**O que foi lido:** os 11 blocos de critérios (E0–E10) e as 43 linhas do Registro de execuções de
`docs/VERIFICACAO.md`; os 78 arquivos de `docs/evidencias/**` (incluindo os 8 PNGs não versionados de
`E8/capturas/`); as 499 linhas de `ferramentas/verificar.py`, função por função.

**O que foi executado** (tudo sem efeito colateral e **sem nenhuma chamada ao Ollama**, conforme a
coordenação da rodada): `verificar.py e6_fontes`, `e7_duplicadas`, `e7_estrutura`, `e7_saidas`,
`e9_numeros`, `e2_reabrir`, `e2_sobreposicao` (estes dois últimos leem só o ChromaDB já persistido e o
PDF via `pypdf`; não estão na lista de proibidos e não tocam o Ollama), `git log/show --stat` e a sonda
[`A2-sonda.py`](A2-sonda.py) (saída literal em [`A2-sonda.txt`](A2-sonda.txt)). **Não** foram rodadas
`e1_resumos`, `e2`, `e3`, `e4`, `e4_limiar`, `e6_ollama_desligado`, `e6_ollama_desligado_scripts` — ver
`## Não verificado`.

---

### A2-01 — As ✅ de E2 (2.2–2.6) apoiam-se em evidência do corpus de 6 artigos; o índice real tem 659 vetores

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:123-132` (critérios 2.1–2.6 e "**Evidência:** `docs/evidencias/E2/`"),
  `docs/evidencias/E2/verificacao_E2.txt:1-7`, `docs/evidencias/E2/reverificacao_e2.txt:1-7`,
  `docs/evidencias/E2/02_indexar_execucao1.txt:5-29`, `docs/evidencias/E2/02_indexar_execucao2.txt:4-28`
- **criterio:** 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
- **o-que-observei:** os quatro arquivos da pasta `E2/` descrevem uma coleção de **556** chunks
  (`{'pagina': 550, 'resumo': 6}`, 6 artigos). O índice que está em `chroma_db/` hoje tem **659**
  (`{'pagina': 651, 'resumo': 8}`, 8 artigos). Nenhum arquivo em `docs/evidencias/E2/` foi tocado depois
  de 2026-09-14 (`git log`: último commit a mexer em `E2/reverificacao_e2.txt` é `4dc236d`, de 14/09;
  o corpus foi a 8 artigos em `af18c3a`, de 15/09). Especificamente, 2.3 ("os resumos estão indexados
  como chunks próprios, **um por artigo**") está ✅ com uma contagem de 6 resumos para 8 artigos, e 2.2
  ("todo chunk tem os metadados") está ✅ com uma amostragem de 556 dos 659 chunks atuais.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A2-sonda.py   # bloco A2-01
  .venv/Scripts/python ferramentas/verificar.py e2_reabrir
  git log --format='%h %ad %s' --date=short -- docs/evidencias/E2/reverificacao_e2.txt
  ```
- **saida-obtida:**
  ```
  == A2-01 índice atual × evidência de E2 ==
    medição 1 (colecao.count())      = 659
    medição 2 (len(get()['ids']))    = 659
    por tipo_chunk                   = {'pagina': 651, 'resumo': 8}
    artigos distintos                = 8
    E2/verificacao_E2.txt: total=556 por_tipo={'pagina': 550, 'resumo': 6}
    E2/reverificacao_e2.txt: total=556 por_tipo={'pagina': 550, 'resumo': 6}

  2.6 contagem em outro processo: 659
  4dc236d 2026-09-14 Adiciona evidências de reverificação E2, E3, E4, E7
  ```
- **por-que-importa:** E2 é pré-requisito declarado de E3–E9 (`VERIFICACAO.md:44`). Cinco ✅ de uma etapa
  inteira estão hoje ancorados num artefato que não existe mais. Quem for reabilitar um critério
  contestado (ou quem auditar depois) vai reler um arquivo que descreve outro repositório e concluir que
  está tudo conferido.
- **confianca:** alta (duas medições independentes da contagem, mais um terceiro processo via `e2_reabrir`)
- **relacionado:** A2-02, A2-04

### A2-02 — O ticket que trocou o corpus (T12) declara sete verificações no Registro sem salvar nenhuma evidência

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:295` (linha do Registro de 2026-09-15, ticket #12),
  `docs/VERIFICACAO.md:13` (protocolo: "Rodar cada verificação da etapa e **salvar a saída** em
  `docs/evidencias/EN/`"), `docs/VERIFICACAO.md:18` ("**Nunca**: marcar ✅ sem evidência")
- **criterio:** 2.2–2.6, 3.1–3.6, 4.1–4.4, 7.1–7.6 (todos declarados reverificados nessa linha)
- **o-que-observei:** a linha afirma "Reverificação: `verificar.py e2/e3/e4/e4_limiar/e6_fontes/
  e7_duplicadas/e7_estrutura` (todos ✅, exit 0) … notebook regenerado e reexecutado ao vivo e
  `--offline` (21/21 células, 0 erros nos dois)" e lista como evidência quatro arquivos
  (`E1/verificacao_E1.txt`, `E7/log_01_preparar_corpus.txt`, `E7/saidas_notebook.txt`,
  `E10/plano_v11.txt`) — **nenhum deles contém a saída de e2, e3, e4, e4_limiar, e7_duplicadas ou
  e7_estrutura**. O commit do ticket (`af18c3a`) não tocou em nenhum arquivo de `E2/`, `E3/` ou `E4/`,
  e `E7/execucao_notebook.txt` / `execucao_notebook_offline.txt` continuam sendo os da execução anterior
  (T09, commit `9e15d94`, "tempo total: 388s" / "62s"), não os da reexecução que a linha reivindica.
- **como-reproduzir:**
  ```bash
  git show --stat af18c3a | grep -E 'evidencias|VERIFICACAO|medicoes'
  git log --format='%h %ad %s' --date=short -- docs/evidencias/E7/execucao_notebook.txt
  ```
- **saida-obtida:**
  ```
   docs/VERIFICACAO.md                                |   5 +-
   docs/evidencias/E1/verificacao_E1.txt              |  31 +-
   docs/evidencias/E10/plano_v11.txt                  |   2 +-
   docs/evidencias/E7/log_01_preparar_corpus.txt      |   8 +-
   docs/evidencias/E7/saidas_notebook.txt             |  29 +
   docs/evidencias/E7/webinario_rag_offline.ipynb     | 731 +++++++++--------
   docs/medicoes.md                                   |   8 +-

  9e15d94 2026-09-15 Fecha #9: reexecuta o notebook (ao vivo + offline) pós T01-T08
  7e29c38 2026-09-14 Material prático do Encontro 2: RAG com Ollama, ChromaDB e Streamlit
  ```
- **por-que-importa:** é a única mudança do projeto que reescreveu o índice inteiro, e é exatamente a
  mudança cuja tabela de dependências (`VERIFICACAO.md:43`) manda reverificar E1–E8. O Registro é o
  histórico canônico do repositório; aqui ele afirma um resultado que não pode ser conferido por
  ninguém, o que é o mesmo defeito que o documento proíbe no seu próprio cabeçalho.
- **confianca:** alta
- **relacionado:** A2-01, A2-04

### A2-03 — Sete das quinze checagens de `verificar.py` não têm como reprovar

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `ferramentas/verificar.py:39-50` (`e1_resumos`), `:53-69` (`e2`), `:72-81`
  (`e2_sobreposicao`), `:84-87` (`e2_reabrir`), `:90-118` (`e3`), `:236-245`
  (`e6_ollama_desligado`), `:395-409` (`e7_estrutura`)
- **criterio:** 1.6, 2.1, 2.2, 2.3, 2.4, 2.6, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 6.7, 7.3, 7.6
- **decisao-documentada:** nenhuma dessas sete funções tem comentário `why:`/`hazard:` no corpo. O
  padrão oposto está documentado e implementado em três lugares do mesmo arquivo — `:334` ("a versão
  anterior desta checagem … **nunca falhava** — o ✅ do critério 7.4 se apoiava nela sem que ela pudesse
  de fato reprovar nada"), `:425-428` e `:476-480` —, ou seja, o projeto já reconheceu esse defeito como
  defeito e o corrigiu caso a caso, sem varrer as demais.
- **o-que-observei:** as sete funções só imprimem. O valor booleano que decidiria o critério é impresso
  no meio da linha e descartado. Casos concretos: `e2:59-60` calcula `incompletos` (chunks sem metadado
  obrigatório) e imprime a lista, sem reprovar; `e3:97` imprime `ordenado=False` se a ordenação por
  distância quebrar (critério 3.1) e sai com 0; `e3:107` imprime `todos obedecem = False` se um filtro
  `where` vazar (critério 3.4) e sai com 0; `e6_ollama_desligado:243` tem literalmente o ramo
  `print(f"6.7 {nome}: NÃO levantou erro")` e termina com exit 0; `e7_estrutura` só lista os títulos do
  notebook, sem comparar com o cronograma (7.3), e lista como "rede de segurança" (7.6) células que
  casaram por acidente (`[1] import json`, `[6] colecao = rag.abrir_colecao()`). `e2_reabrir:87`
  imprime o stdout de um subprocesso sem comparar com nada: se o subprocesso falhar, a linha de
  evidência sai quase igual.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A2-sonda.py   # blocos A2-03 e A2-04
  ```
- **saida-obtida:**
  ```
  == A2-03 funções de verificar.py que não têm como reprovar ==
    e1_resumos      pode_reprovar_ast=False pode_reprovar_texto=False
    e2              pode_reprovar_ast=False pode_reprovar_texto=False
    e2_sobreposicao pode_reprovar_ast=False pode_reprovar_texto=False
    e2_reabrir      pode_reprovar_ast=False pode_reprovar_texto=False
    e3              pode_reprovar_ast=False pode_reprovar_texto=False
    e6_ollama_desligado  pode_reprovar_ast=False pode_reprovar_texto=False
    e7_estrutura    pode_reprovar_ast=False pode_reprovar_texto=False
  == A2-04 e2_reabrir com subprocesso que falha ==
    [subprocesso OK] returncode=0 → linha impressa por e2_reabrir seria:
        2.6 contagem em outro processo: 659
    [subprocesso quebrado] returncode=1 → linha impressa por e2_reabrir seria:
        2.6 contagem em outro processo:  boom
  ```
- **por-que-importa:** `docs/ESTADO_ATUAL.md:122-123` afirma para quem audita que "**todas** saem com
  código ≠ 0 quando falham". Não é o caso de quase metade delas, e são justamente as que sustentam E2 e
  E3 inteiras. Uma reverificação "exit 0" nessas etapas não é sinal de nada: um `rodar_scripts.sh` verde
  continuaria verde com a coleção corrompida, com filtro vazando ou com o Ollama respondendo quando
  deveria estar fora do ar.
- **confianca:** alta (duas leituras independentes do mesmo fato: AST e varredura textual do bloco de
  linhas de cada função, com resultado idêntico nas quinze)
- **relacionado:** A2-06, A2-07

### A2-04 — A evidência citada por 4.4 (e a de 3.6) demonstra um caso que o código não roda mais e que o corpus atual tornou impossível

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:158` (critério 4.4, que aponta explicitamente para
  `evidencias/E4/reverificacao_e4_v2.txt`), `docs/evidencias/E4/reverificacao_e4_v2.txt:3`,
  `docs/evidencias/E4/reverificacao_e4.txt:3`, `docs/evidencias/E3/verificacao_E3.txt:10`,
  `docs/evidencias/E3/reverificacao_e3.txt:10`, `ferramentas/verificar.py:133-134`, `:114-115`
- **criterio:** 3.6, 4.4
- **decisao-documentada:** `ferramentas/verificar.py:131-132` registra a decisão: "T12/#12: `idioma=pt`
  deixou de esvaziar o estágio 1 (2 artigos reais agora); troca para um filtro por ano fora do corpus"
  (idem `:112-113` para o 3.6). A decisão cobre o **código** — e está correta. O que ela não cobre é que
  o arquivo de evidência citado pelo critério continua sendo o anterior à troca: `VERIFICACAO.md:158`
  manda o leitor conferir 4.4 num arquivo que prova o caso antigo.
- **o-que-observei:** o arquivo que o critério 4.4 cita registra `4.4a estágio 1 vazio (idioma=pt)`; o
  código de hoje imprime `4.4a estágio 1 vazio (ano>=2030)`, e a string `4.4a estágio 1 vazio
  (idioma=pt)` não existe mais em `verificar.py`. Como o corpus passou a ter 2 artigos `idioma=pt`, o
  caso gravado na evidência (estágio 1 vazio por filtro de idioma) não é reproduzível: hoje ele
  devolveria resumos. O mesmo vale para 3.6, cuja única evidência (`E3/verificacao_E3.txt:10` e
  `reverificacao_e3.txt:10`) diz "filtro idioma=pt (sem artigos): 0 resultados".
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A2-sonda.py   # bloco A2-08
  ```
- **saida-obtida:**
  ```
  == A2-08 rótulos gravados na evidência × rótulos do código atual ==
    '3.6 filtro ano>=2030'                presente em verificar.py = True
    '3.6 filtro idioma=pt (sem artigos)'  presente em verificar.py = False
    '4.4a estágio 1 vazio (ano>=2030)'    presente em verificar.py = True
    '4.4a estágio 1 vazio (idioma=pt)'    presente em verificar.py = False
    E3/verificacao_E3.txt: ['3.6 filtro idioma=pt (sem artigos): 0 resultados, sem erro']
    E3/reverificacao_e3.txt: ['3.6 filtro idioma=pt (sem artigos): 0 resultados, sem erro']
    E4/reverificacao_e4_v2.txt: ["4.4a estágio 1 vazio (idioma=pt): caminho = 'busca simples (…nenhum
      resumo com esse filtro)', 0 resultados", "4.4b pergunta fora da base sem filtro: …0.7322…"]
  ```
- **por-que-importa:** 4.4 é o critério que a auditoria de 14/09 contestou e que os tickets #6 e #7
  existiram para fechar; é o único cujo texto em `VERIFICACAO.md` aponta para um arquivo nominal. Metade
  do que esse arquivo prova (o caso 4.4a) caducou com o corpus, e o número do caso 4.4b (0.7322) também
  é da calibração de 6 artigos — `docs/ESTADO_ATUAL.md:80-81` já registra que o valor equivalente hoje é
  outro. Um ✅ apontando para a prova errada é pior do que um ✅ sem ponteiro: dá a impressão de rastro.
- **confianca:** alta
- **relacionado:** A2-01, A2-02, A1-06

### A2-05 — Os números de 9.1 contradizem os arquivos de evidência que eles próprios citam

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:230` (critério 9.1 ✅), `docs/medicoes.md:20`, `:31`, `:32`, `:53`,
  `:60`, `:61` × `docs/evidencias/E7/log_02_indexar.txt:4`,
  `docs/evidencias/E7/log_05_shap.txt:3` e `:20`, `docs/evidencias/E8/apptest.txt:4,10,13,16`,
  `docs/evidencias/E7/execucao_notebook.txt:4`, `docs/evidencias/E7/execucao_notebook_offline.txt:4`
- **criterio:** 9.1
- **o-que-observei:** cinco linhas da tabela 9.1 afirmam um valor e citam, na própria coluna
  "Evidência", um arquivo que diz outra coisa:

  | `medicoes.md` afirma | Evidência que ele cita | O que o arquivo diz |
  |---|---|---|
  | `:20` "Chunking (**556 chunks**) \| 9,0 s" | `E7/log_02_indexar.txt` | "Chunking: **659** chunks em 8.8s" |
  | `:31` "SHAP … frio \| 112,0 s · **81,6 s**" | `E7/log_05_shap.txt` | "SHAP em **83.3**s" |
  | `:32` "SHAP … já carregado \| 18,9 s · **19,7 s**" | `E7/log_05_shap.txt` | "SHAP em **17.8**s" |
  | `:53` "Pergunta no Streamlit (AppTest, **3b**, k=2 e k=5) \| **8 s · 17 s**" | `E8/apptest.txt` | 44 s, 50 s, 39 s, 28 s, com `qwen2.5:1.5b` |
  | `:60` "Notebook inteiro ao vivo \| **959 s** na última execução" | `E7/execucao_notebook.txt` | "tempo total: **388s**" |
  | `:61` "Notebook inteiro offline \| **61 s**" | `E7/execucao_notebook_offline.txt` | "tempo total: **62s**" |

- **como-reproduzir:**
  ```bash
  grep -nE 'Chunking|SHAP de 1 chunk|AppTest|Notebook inteiro' docs/medicoes.md
  grep -n 'tempo total' docs/evidencias/E7/execucao_notebook.txt docs/evidencias/E7/execucao_notebook_offline.txt
  grep -n 'SHAP em' docs/evidencias/E7/log_05_shap.txt
  grep -n 'respondida em' docs/evidencias/E8/apptest.txt
  grep -n 'Chunking' docs/evidencias/E7/log_02_indexar.txt
  ```
- **saida-obtida:**
  ```
  execucao_notebook.txt: células de código: 21 | executadas: 21 | com erro: 0 | … | tempo total: 388s
  execucao_notebook_offline.txt: … tempo total: 62s
  log_05_shap.txt: SHAP em 83.3s
  log_05_shap.txt: SHAP em 17.8s
  log_02_indexar.txt: 1) Chunking: 659 chunks em 8.8s
  8.2 pergunta 1 respondida em 44s | exceção: False | erros: []
      pergunta 2 (só k) respondida em 50s | …
  ```
- **por-que-importa:** 9.1 está ✅ e o invariante nº 6 do repositório (`ESTADO_ATUAL.md:218`) é "todo
  número publicado vem de medição **nesta** máquina, com data e comando". Aqui o número e o comando
  estão no mesmo documento e discordam. O caso de `:60` é o mais grave para a aula: quem ler "959 s"
  planeja o bloco do notebook com quase 16 minutos, quando a última execução salva levou 388 s — e é o
  mesmo tipo de defasagem que o ticket #10 criou o `e9_numeros` para impedir, mas que essa linha escapa
  porque diz "na última execução" e não "na última execução do notebook" (ver A2-06).
- **confianca:** alta (cada número foi lido duas vezes, por caminhos diferentes: leitura integral do
  arquivo e `Select-String` sobre o mesmo par de arquivos)
- **relacionado:** A2-06, eixo A5 (dono de `docs/medicoes.md`)

### A2-06 — `e9_numeros` confere os números contra um arquivo append-only, então qualquer valor histórico "confirma"

- **severidade:** média
- **categoria:** evidencia
- **onde:** `ferramentas/verificar.py:467` (`_PADRAO_NUMERO_ULTIMA_EXECUCAO`), `:472` (lê
  `E7/saidas_notebook.txt`), `:489` (`re.search(rf"(?<!\d){numero}s\b", saidas)`),
  `docs/evidencias/E7/saidas_notebook.txt` (8 blocos acumulados de execuções diferentes),
  `docs/evidencias/E9/reconciliacao_numeros.txt:7`
- **criterio:** 9.1, 5a.1, 7.2
- **decisao-documentada:** `verificar.py:463-466` explica por que a checagem existe (números que "ficam
  defasados quando o notebook é reexecutado") e `:476-480` endurece o caso "nenhuma menção encontrada".
  Nenhum dos dois comentários trata do arquivo de referência: `E7/saidas_notebook.txt` é **anexado**, não
  substituído, a cada execução — o próprio Registro (`VERIFICACAO.md:288`) registra isso como escolha
  deliberada ("a saída do novo comando foi **anexada** ao fim do arquivo, não sobrescreveu"). Com um
  arquivo que guarda todo o histórico, "o número aparece em `saidas_notebook.txt`" deixa de significar
  "o número é o da última execução", que é o que o comentário `:463-466` diz querer garantir.
- **o-que-observei:** `36s` e `70,6s` (os valores que o próprio
  `E9/reconciliacao_numeros.txt:7` registra como o "DEPOIS" correto do ticket #10, e que hoje já são
  história) continuam sendo confirmados pelo arquivo, assim como `48s` e `34s` (execuções ainda mais
  antigas). Ou seja: se `medicoes.md` tivesse ficado em 36 s, `e9_numeros` sairia com 0 do mesmo jeito.
  A checagem também só enxerga a frase literal "na última execução do notebook" — 3 dos ~30 números
  publicados em `medicoes.md`; as linhas `:20`, `:31`, `:32`, `:53`, `:60` e `:61` do achado A2-05 estão
  todas fora do alcance dela. Como efeito colateral, `E9/reconciliacao_numeros.txt`, que é a evidência
  nominal de 9.1, mostra `['36', '70,6']` enquanto `medicoes.md` hoje diz `['190,7', '50', '17,9']`.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python ferramentas/verificar.py e9_numeros
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A2-sonda.py   # bloco A2-02
  ```
- **saida-obtida:**
  ```
  9.1 números 'na última execução do notebook' em docs/medicoes.md: ['190,7', '50', '17,9']
  9.1 números sem confirmação em docs/evidencias/E7/saidas_notebook.txt: nenhum
  [e9_numeros em 0.0s]

  == A2-02 e9_numeros × histórico acumulado de saidas_notebook.txt ==
    '36s'   seria CONFIRMADO por saidas_notebook.txt? True (1 ocorrência(s))
    '70,6s' seria CONFIRMADO por saidas_notebook.txt? True (1 ocorrência(s))
    '48s'   seria CONFIRMADO por saidas_notebook.txt? True (1 ocorrência(s))
    '34s'   seria CONFIRMADO por saidas_notebook.txt? True (1 ocorrência(s))
    blocos acumulados no arquivo (marcadores): 8
  ```
- **por-que-importa:** 9.1 é o único critério de E9 com checagem automatizada, e ela foi criada
  exatamente para que "número defasado" não passasse mais despercebido. Como está, a checagem envelhece
  junto com o arquivo: quanto mais execuções são anexadas, mais números velhos ela aceita. A2-05 é a
  demonstração de que isso já aconteceu na prática, por fora do recorte da frase.
- **confianca:** alta (quatro entradas distintas testadas: 36, 70,6, 48 e 34 — todas confirmadas pelo
  arquivo; e duas entradas de controle, 94 e 163,8, corretamente não confirmadas)
- **relacionado:** A2-05

### A2-07 — `e6_ollama_desligado_scripts` exclui por construção os dois scripts que o achado 6.7 nomeia

- **severidade:** média
- **categoria:** evidencia
- **onde:** `ferramentas/verificar.py:253` (`glob("0[3-7]_*.py")`), `:260`
  (`ok = not tem_traceback and (mensagem_clara or saida.returncode != 0)`),
  `docs/evidencias/E6/reverificacao_e6_ollama_desligado_scripts.txt:1-7`, `docs/VERIFICACAO.md:188`
- **criterio:** 6.7
- **decisao-documentada:** `verificar.py:249-251` registra o motivo da checagem existir: "testar só
  `rag.py` … não prova nada sobre os scripts — o achado 6.7 mostrou **03-06** e `opcional/` sem nenhum
  try/except". A decisão nomeia o escopo que existia quando foi escrita. O que ela não cobre é que o
  escopo de 6.7 cresceu depois: `CLAUDE.md` e `docs/ESTADO_ATUAL.md:147,200` registram que 6.7 segue
  contestado **porque `scripts/01` e `scripts/02` não têm `cli_seguro()`** (issue #24). O glob fixo
  `0[3-7]_*.py` não alcança nenhum dos dois, então a checagem continuará saindo com 0 estando o achado
  aberto — e continuará saindo com 0 depois de o #24 ser corrigido, sem verificar a correção.
- **o-que-observei:** o glob cobre 7 arquivos (`scripts/03`–`07` e os 2 de `opcional/`), exatamente os 7
  que já usam `rag.cli_seguro()`. Os 3 não cobertos (`scripts/00`, `01`, `02`) são os 3 que não usam.
  Além disso, o critério de aprovação em `:260` aceita um script que **não** imprima mensagem clara,
  desde que saia com código ≠ 0 — o que é o comportamento de um traceback impresso fora de
  `stderr` ou de um `SystemExit` silencioso.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A2-sonda.py   # bloco A2-07
  ```
- **saida-obtida:**
  ```
  == A2-07 cobertura do glob de e6_ollama_desligado_scripts ==
    cobertos   : ['03_buscar.py', '04_dois_estagios.py', '05_shap.py', '06_com_sem_contexto.py',
                  '07_ollama.py', 'avaliacao_estilo_ragas.py', 'calcular_shapley_chunks.py']
    NÃO cobertos: ['scripts/00_checar_ambiente.py', 'scripts/01_preparar_corpus.py',
                   'scripts/02_indexar.py']
      scripts/01_preparar_corpus.py  usa rag.cli_seguro()=False coberto=False
      scripts/02_indexar.py          usa rag.cli_seguro()=False coberto=False
  ```
- **por-que-importa:** `scripts/01` e `02` são os dois primeiros que o participante roda depois do README
  e os únicos longos. É neles que o Ollama tem mais chance de cair (o `02` fica ~19 min pedindo
  embeddings). A única checagem automatizada de 6.7 é estruturalmente cega para eles, e o ✅ de 6.7 se
  apoia numa evidência (`reverificacao_e6_ollama_desligado_scripts.txt`) que lista 7 arquivos como se
  fossem o conjunto.
- **confianca:** alta
- **relacionado:** A2-03, issue #24

### A2-08 — 8.2/8.4/8.5/8.7/8.8 exigem captura de tela; nenhuma captura está versionada e a tabela mostra ✅ sem marca de contestado

- **severidade:** alta
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:214,216,217,219,220` (coluna "Como verificar" = "captura de tela" /
  "captura"), `docs/VERIFICACAO.md:222` ("**Evidência:** `docs/evidencias/E8/` (capturas + log)"),
  `docs/evidencias/E8/ui_navegador.txt:6-8`, `docs/evidencias/E8/capturas/` (8 PNGs, não versionados)
- **criterio:** 8.2, 8.4, 8.5, 8.7, 8.8
- **decisao-documentada:** o repositório já registra o problema em `CLAUDE.md` ("8.2, 8.4, 8.5, 8.7 —
  sem captura de tela salva; evidência é texto de DOM/AppTest") e em `docs/ESTADO_ATUAL.md:149,199`
  ("capturas geradas mas **não commitadas**", issues #15 e #25). O que essas decisões não cobrem é o
  estado do próprio `VERIFICACAO.md`: ali os cinco critérios aparecem como ✅ **limpos**, e a linha
  `:222` afirma que a pasta contém "capturas + log". A tabela de resumo (`:32`) mostra `E8 | ✅` sem
  qualquer ressalva, diferentemente de E1 (`✅ (1.8 ⏸️)`), E9 (`✅ (9.3 ⏸️)`) e E10, que sinalizam a
  pendência. Quem consultar só o documento de verificação — que é o que o protocolo manda consultar no
  início de toda tarefa (`:3`) — não tem como saber que cinco ✅ de E8 estão contestados.
- **o-que-observei:** `git status --short -- docs/evidencias` devolve exatamente uma linha,
  `?? docs/evidencias/E8/capturas/`: os 8 PNGs existem no disco e **não estão no repositório**. Falta
  também o cenário 8.8 (nenhum `8.8_*.png`). A evidência versionada de 8.2/8.7 é
  `E8/ui_navegador.txt`, que declara no cabeçalho a limitação ("a ferramenta não grava imagens em
  disco. Por isso a evidência abaixo é o texto e o DOM"), e `E8/apptest.txt`, que é AppTest — nenhum dos
  dois é o que a coluna "Como verificar" pede.
- **como-reproduzir:**
  ```bash
  git status --short -- docs/evidencias
  git ls-files docs/evidencias/E8
  ```
- **saida-obtida:**
  ```
  ?? docs/evidencias/E8/capturas/
  docs/evidencias/E8/apptest.txt
  docs/evidencias/E8/streamlit_servidor.log
  docs/evidencias/E8/t04_fontes_citadas_app.txt
  docs/evidencias/E8/ui_navegador.txt
  docs/evidencias/E8/ui_ollama_desligado.txt
  ```
- **por-que-importa:** um clone limpo do repositório — que é o critério de sucesso declarado do material
  — não contém nenhuma das capturas que cinco critérios ✅ dizem ter. E, ao contrário de 9.3 e 10.1, a
  contestação não é visível em nenhum lugar de `VERIFICACAO.md`, que é o documento que o `CLAUDE.md`
  manda ler no início e no fim de toda tarefa.
- **confianca:** alta
- **relacionado:** eixo A4; issues #15, #25

### A2-09 — `E6/ollama_desligado.txt` anota `exit=0` para execuções que saem com código 1

- **severidade:** média
- **categoria:** evidencia
- **onde:** `docs/evidencias/E6/ollama_desligado.txt:3` e `:17`, `scripts/00_checar_ambiente.py:66-68`
- **criterio:** 0.8, 6.7
- **o-que-observei:** o arquivo registra duas execuções com o Ollama parado e anota `exit=0` nas duas.
  A segunda delas é `scripts/00_checar_ambiente.py`, cuja saída no próprio arquivo é
  "1 verificação(ões) falharam: Servidor Ollama respondendo" — e o script tem `sys.exit(1)` nesse
  caminho (`scripts/00_checar_ambiente.py:66-68`). Reexecutando o mesmo script com o host apontado para
  uma porta morta (nenhum contato com o Ollama real), o código de saída é 1, não 0. A primeira anotação
  `exit=0` acompanha uma mensagem `ERRO: Não consegui falar com o Ollama`, padrão de `rag.cli_seguro()`,
  que a evidência posterior `E6/reverificacao_e6_ollama_desligado_scripts.txt` mostra saindo com
  `exit=2`.
- **como-reproduzir:**
  ```bash
  OLLAMA_HOST=http://localhost:11999 .venv/Scripts/python scripts/00_checar_ambiente.py; echo "exit=$?"
  OLLAMA_HOST=http://127.0.0.1:1     .venv/Scripts/python scripts/00_checar_ambiente.py; echo "exit=$?"
  ```
- **saida-obtida:**
  ```
  == A2-05 código de saída real de scripts/00 com o Ollama inalcançável ==
    últimas linhas: ['[INFO] OLLAMA_MODELS = D:\\webinarioOllamaRAG\\Ollama\\models',
                     '1 verificação(ões) falharam: Servidor Ollama respondendo']
    returncode real = 1
    o que a evidência E6/ollama_desligado.txt anota:
      exit=0
      1 verificação(ões) falharam: Servidor Ollama respondendo
      exit=0
  ```
- **por-que-importa:** `exit=0` é o carimbo que quase todos os arquivos de `docs/evidencias/` usam para
  dizer "passou" (aparece em `E7/sequencia_scripts.txt`, `E7/execucao_notebook.txt`,
  `E9/reconciliacao_numeros.txt`, `E10/revisao_codigo_checagens.txt`). Se em pelo menos um arquivo esse
  carimbo foi capturado do processo errado (provavelmente o código de saída do `tee`, não o do Python),
  ele deixa de ser verificável em todos — e o critério 0.8, que é literalmente "sai com código 0", passa
  a depender de um dado que já se sabe ter sido registrado errado uma vez.
- **confianca:** alta (duas medições, com dois hosts inalcançáveis diferentes: `localhost:11999` e
  `127.0.0.1:1`, ambas `exit=1`)
- **relacionado:** A2-03, eixo A6

### A2-10 — `E7/t03_fontes_notebook.txt`, evidência de 6.5 no notebook, mostra as duas listas idênticas

- **severidade:** média
- **categoria:** evidencia
- **onde:** `docs/evidencias/E7/t03_fontes_notebook.txt:11-25` e `:30-41`, `docs/VERIFICACAO.md:283`
  (linha do Registro do ticket #3), `docs/VERIFICACAO.md:186` (critério 6.5)
- **criterio:** 6.5
- **o-que-observei:** o ticket #3 existiu para exibir "Fontes citadas" **separado** de "Trechos enviados
  ao prompt". No arquivo de evidência desse ticket, os dois blocos são caractere a caractere iguais nas
  duas células (`[1] asai2023_selfrag.pdf, p. 10 / [2] … p. 1 / [3] gao2023_survey.pdf, p. 12 /
  [4] … p. 4`), porque o modelo não emitiu nenhuma citação `[n]` e o fallback listou o top-k inteiro. A
  evidência, portanto, é compatível com o comportamento anterior ao ticket: ela não distingue as duas
  implementações.
- **como-reproduzir:**
  ```bash
  grep -n -A6 'Fontes citadas' docs/evidencias/E7/t03_fontes_notebook.txt
  ```
- **saida-obtida:**
  ```
  **Fontes citadas**
  [1] asai2023_selfrag.pdf, p. 10
  [2] asai2023_selfrag.pdf, p. 1
  [3] gao2023_survey.pdf, p. 12
  [4] asai2023_selfrag.pdf, p. 4
  **Trechos enviados ao prompt**
  [1] asai2023_selfrag.pdf, p. 10
  [2] asai2023_selfrag.pdf, p. 1
  [3] gao2023_survey.pdf, p. 12
  [4] asai2023_selfrag.pdf, p. 4
  ```
- **por-que-importa:** 6.5 é o critério cujo ✅ o `CLAUDE.md` descreve como resolvido pelos tickets #1,
  #3 e #4. Para o notebook, o arquivo que sustenta esse "resolvido" mostra o caso em que a separação não
  aparece. É a mesma situação que o eixo A1 encontrou no `resultados/com_sem_contexto.json` (achado
  A1-08), aqui do lado da evidência: não há nenhum arquivo em `docs/evidencias/` em que o notebook ou o
  app exiba "Fontes citadas" **menor** que o top-k, com o modelo padrão atual.
- **confianca:** alta
- **relacionado:** A1-08, A2-11

### A2-11 — 6.6 está ✅ demonstrando a troca de modelo no sentido que deixou de existir

- **severidade:** média
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:187` (critério 6.6: "Trocar `MODELO_CHAT` para `qwen2.5:1.5b` em
  `config.py` funciona sem outra alteração"), `config.py:17-18`, `docs/evidencias/E6/07_ollama.txt`
- **criterio:** 6.6, 9.3
- **o-que-observei:** desde o ticket #19 (2026-09-15), `config.MODELO_CHAT` já **é** `qwen2.5:1.5b` e o
  plano B passou a ser `qwen2.5:3b` (`config.py:17-18`). O critério 6.6, que continua ✅, verifica a
  troca para o modelo que virou o padrão — isto é, verifica o estado de repouso do sistema. Varrendo
  todas as evidências de E6/E7/E8, todo arquivo posterior ao #19 usa `qwen2.5:1.5b`
  (`E7/log_02_indexar.txt`, `log_07_ollama.txt`, `E8/apptest.txt`); os únicos arquivos com
  `qwen2.5:3b` são de 14–15/09, anteriores à inversão e ao corpus de 8 artigos
  (`E6/reverificacao_6.5_fontes.txt`, `E8/t04_fontes_citadas_app.txt`, `E8/ui_navegador.txt`).
- **como-reproduzir:**
  ```bash
  grep -rn 'qwen2.5:3b' docs/evidencias/E6 docs/evidencias/E7 docs/evidencias/E8
  git log --format='%h %ad %s' --date=short -1 -- docs/evidencias/E8/t04_fontes_citadas_app.txt
  ```
- **saida-obtida:**
  ```
  Count Name
  ----- ----
      2 07_ollama.txt, qwen2.5:1.5b
      4 07_ollama.txt, qwen2.5:3b
      1 apptest.txt, qwen2.5:1.5b
      1 log_07_ollama.txt, qwen2.5:1.5b
      1 reverificacao_6.5_fontes.txt, qwen2.5:3b
      1 t04_fontes_citadas_app.txt, qwen2.5:3b
      2 ui_navegador.txt, qwen2.5:3b
  ```
- **por-que-importa:** o critério 9.3 está ⏸️ esperando o ensaio de 21/09 para decidir se o `qwen2.5:3b`
  volta a ser o modelo ao vivo. Se voltar, não existe nenhuma evidência de que ele funciona com o corpus
  e o código de hoje: a última execução dele é anterior aos 2 artigos em português, ao limiar
  recalibrado e às mudanças de fontes/recusa dos tickets #1–#10. O ✅ de 6.6 sugere que o caminho de
  plano B está coberto, e ele não está.
- **confianca:** média (a varredura cobre `docs/evidencias/E6`, `E7` e `E8`; não varri `resultados/`,
  que é escopo de A3, embora o eixo A1 já tenha registrado `com_sem_contexto.json` como 1.5b)
- **relacionado:** A1-08, eixo A5

### A2-12 — 5b.1 está ✅ com um Shapley pré-computado do corpus de 6 artigos e do modelo antigo

- **severidade:** média
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:171` (critério 5b.1), `docs/evidencias/E5/calcular_shapley_chunks.txt`
  (de 2026-09-14, commit `7e29c38`), `resultados/shapley_chunks.json`
- **criterio:** 5b.1
- **o-que-observei:** o arquivo de resultado pré-computado carrega `"modelo": "qwen2.5:3b"` e um top-4
  calculado sobre o índice de 556 vetores (`asai2023_selfrag.pdf` p.10/p.1/p.4 + `gao2023_survey.pdf`
  p.12). Nem o `.json` nem a evidência de E5 foram regerados depois do T12
  (`git log -- docs/evidencias/E5/calcular_shapley_chunks.txt` → só o commit inicial). O Registro
  (`VERIFICACAO.md:298`) trata isso explicitamente: "5b.1 … não precisa reindexar — critério já deixa
  explícito que não roda ao vivo". O critério diz que não roda **ao vivo**; não diz que o resultado pode
  ser de outro corpus e de outro modelo.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python -c "import json;d=json.load(open('resultados/shapley_chunks.json',encoding='utf-8'));print(d['modelo'],[(c['arquivo'],c['pagina']) for c in d['contribuicoes']])"
  git log --format='%h %ad %s' --date=short -- docs/evidencias/E5/calcular_shapley_chunks.txt resultados/shapley_chunks.json
  ```
- **saida-obtida:**
  ```
  qwen2.5:3b [('asai2023_selfrag.pdf', 10), ('asai2023_selfrag.pdf', 1), ('gao2023_survey.pdf', 12),
              ('asai2023_selfrag.pdf', 4)]
  7e29c38 2026-09-14 Material prático do Encontro 2: RAG com Ollama, ChromaDB e Streamlit
  ```
- **por-que-importa:** o bloco 4 do notebook carrega esse arquivo como "Shapley dos chunks do top-k". Se
  o top-k de hoje (8 artigos, 659 vetores, `qwen2.5:1.5b`) não for o mesmo top-4 de 14/09, a célula
  mostra contribuições de chunks que não são os recuperados na aula — e nada no material avisa. Não
  consegui confirmar se o top-4 mudou, porque isso exige embeddings (ver `## Não verificado`).
- **confianca:** média
- **relacionado:** eixo A3

### A2-13 — `E10/verificacao_consulta_sessao.txt` é um auto-relato, sem nenhuma saída de comando

- **severidade:** baixa
- **categoria:** evidencia
- **onde:** `docs/evidencias/E10/verificacao_consulta_sessao.txt:1-36`, `docs/VERIFICACAO.md:3` e `:18`
- **criterio:** — (arquivo guardado em `docs/evidencias/E10/`, mas não citado por nenhum critério)
- **o-que-observei:** o arquivo lista "VERIFICAÇÕES EXECUTADAS: ✅ E2 (2.2-2.6) … ✅ E7 (7.3-7.4)" e
  "STATUS FINAL: Todas as reverificações passaram (✅)". Não há um único comando, número ou trecho de
  saída — só as afirmações e os nomes dos arquivos que teriam sido salvos. É, no formato, o oposto do
  que `VERIFICACAO.md:3` define ("saída de comando, arquivo ou captura de tela. Afirmação sem evidência
  não conta").
- **como-reproduzir:**
  ```bash
  cat docs/evidencias/E10/verificacao_consulta_sessao.txt
  ```
- **saida-obtida:**
  ```
  VERIFICAÇÕES EXECUTADAS:
  ✅ E2 (2.2-2.6): indexação, metadados, embeddings
  ✅ E3 (3.1-3.6): busca top-k, filtros, cross-lingual
  ...
  STATUS FINAL:
  Todas as reverificações passaram (✅). Nenhum critério falhou.
  ```
- **por-que-importa:** o arquivo está dentro de `docs/evidencias/`, o que lhe dá o mesmo peso visual dos
  demais. Como ninguém o cita, o risco imediato é baixo; o risco real é de precedente — se um relato
  assim conta como evidência, o critério de "✅ só com evidência" perde a definição.
- **confianca:** alta

### A2-14 — `E7/log_02_indexar.txt` é uma reconstrução, não a saída da execução que documenta

- **severidade:** baixa
- **categoria:** evidencia
- **onde:** `docs/evidencias/E7/log_02_indexar.txt:38-45`, `docs/VERIFICACAO.md:296` (linha do Registro
  de 2026-09-16), `docs/medicoes.md:21` e `:52` (citam esse arquivo como fonte de números)
- **criterio:** 2.1, 2.5, 2.8, 7.5, 9.1
- **decisao-documentada:** o próprio arquivo declara, em `:38-45`, que a saída real foi sobrescrita por
  um `git checkout` e que o conteúdo "foi reconstruído a partir da saída real e completa de **uma
  execução equivalente**", com o detalhe do modelo ajustado à mão. A declaração é honesta e está no
  lugar certo. O que ela não cobre é o uso a jusante: `docs/medicoes.md:21` e `:52` citam esse arquivo
  como evidência de números (1104,1 s de indexação, 136,9 s de extração) como se fosse medição direta,
  e o Registro o lista sem a ressalva.
- **o-que-observei:** um arquivo de evidência montado a partir de outra execução, com pelo menos um
  campo editado manualmente ("só o detalhe '3) Demo' reflete o modelo então configurado … em vez do 3b
  visto nessa execução anterior").
- **como-reproduzir:**
  ```bash
  tail -12 docs/evidencias/E7/log_02_indexar.txt
  grep -n 'log_02_indexar' docs/medicoes.md
  ```
- **saida-obtida:**
  ```
  # nota (ticket #12, 2026-09-15): a saída completa desta execução foi acidentalmente sobrescrita
  # por um `git checkout HEAD --` durante a organização dos commits, enquanto o processo do
  # `rodar_scripts.sh` ainda estava rodando em segundo plano. … Este arquivo foi reconstruído a
  # partir da saída real e completa de uma execução equivalente do mesmo script, rodada minutos
  # antes … só o detalhe "3) Demo" reflete o modelo então configurado (qwen2.5:1.5b …)
  ```
- **por-que-importa:** 2.5 (idempotência) não tem checagem automatizada nenhuma e sua evidência direta
  (`E2/02_indexar_execucao1/2.txt`) é do corpus de 6 artigos (A2-01); a única execução de indexação do
  corpus atual é justamente este log reconstruído. O invariante nº 6 (`ESTADO_ATUAL.md:218`) pede
  "medição nesta máquina, com data e comando" — uma reconstrução transparente ainda é uma reconstrução.
- **confianca:** alta
- **relacionado:** A2-01, A2-05

### A2-15 — Evidências de E1 e E3 na pasta nominal do critério continuam descrevendo 6 artigos

- **severidade:** baixa
- **categoria:** evidencia
- **onde:** `docs/VERIFICACAO.md:115` ("**Evidência:** `docs/evidencias/E1/`") e `:147`
  ("`docs/evidencias/E3/`"), `docs/evidencias/E1/01_preparar_corpus.txt:1-21`,
  `docs/evidencias/E3/03_buscar.txt`, `docs/evidencias/E1/verificacao_E1.txt:82`
- **criterio:** 1.1, 1.2, 1.6, 3.1–3.6
- **o-que-observei:** a evidência que demonstra 1.1/1.2 para o corpus de hoje (8 artigos, 135 páginas,
  0 páginas sem texto) está em `docs/evidencias/**E7**/log_01_preparar_corpus.txt`, enquanto
  `docs/evidencias/E1/01_preparar_corpus.txt` — a pasta que o critério indica — ainda lista 6 artigos e
  "total: 109 páginas". O mesmo vale para E3: a única saída de busca sobre o corpus de 8 artigos é
  `E7/log_03_buscar.txt`. Também notei que a conferência manual de 1.6 em
  `E1/verificacao_E1.txt` termina com o campo `conferido por/data:` em branco (linha 82), apesar de o
  critério ser explicitamente "conferência manual de cada linha".
- **como-reproduzir:**
  ```bash
  grep -n 'total:' docs/evidencias/E1/01_preparar_corpus.txt docs/evidencias/E7/log_01_preparar_corpus.txt
  grep -n 'conferido por/data' docs/evidencias/E1/verificacao_E1.txt
  ```
- **saida-obtida:**
  ```
  docs/evidencias/E1/01_preparar_corpus.txt:8:   total: 109 páginas
  docs/evidencias/E7/log_01_preparar_corpus.txt:10:   total: 135 páginas
  docs/evidencias/E1/verificacao_E1.txt:82:conferido por/data:
  ```
- **por-que-importa:** o conteúdo certo existe; está arquivado na pasta da etapa errada. Quem seguir o
  ponteiro do critério lê o número velho. É a forma mais barata de um ✅ parecer verificado sem estar.
- **confianca:** alta
- **relacionado:** A2-01

### A2-16 — A cobertura de 10.3 endossa uma entrada do troubleshooting que o corpus atual tornou falsa

- **severidade:** baixa
- **categoria:** evidencia
- **onde:** `docs/evidencias/E10/troubleshooting_cobertura.txt:13`, `docs/troubleshooting.md:50-52`,
  `docs/VERIFICACAO.md:245` (critério 10.3 ✅)
- **criterio:** 10.3
- **o-que-observei:** a tabela de cobertura lista "Filtro idioma=pt vazio | `E3/verificacao_E3.txt`
  (3.6) | 'O filtro idioma = pt não traz nada'" como um item **coberto**. A entrada correspondente do
  troubleshooting diz: "**Causa:** ainda não há artigos em português no corpus." Desde o T12 há dois, e
  o filtro devolve resultados — `E8/apptest.txt:14` mostra `medeiros2025_embeddings_pt.pdf` sendo
  escolhido no estágio 1.
- **como-reproduzir:**
  ```bash
  grep -n -A3 'idioma = pt' docs/troubleshooting.md
  grep -n 'idioma=pt' docs/evidencias/E10/troubleshooting_cobertura.txt
  ```
- **saida-obtida:**
  ```
  50:### O filtro `idioma = pt` não traz nada
  51:- **Causa:** ainda não há artigos em português no corpus. O resultado vazio é o comportamento
     esperado e não gera erro (E3 critério 3.6).
  52:- **Resposta:** "Ainda não há artigos em português. Esse filtro volta vazio de propósito."
  ```
- **por-que-importa:** 10.3 é "cobre os erros realmente encontrados"; aqui a cobertura aponta para uma
  resposta que o facilitador daria errada ao vivo, e o arquivo de evidência a carimba como coberta.
  `docs/troubleshooting.md:47` ("gerar os 556 embeddings") tem o mesmo problema de defasagem.
- **confianca:** alta
- **relacionado:** A2-04, eixo A5 (dono de `docs/troubleshooting.md`)

---

## Não verificado

**Bloqueado pela regra de serialização do Ollama nesta rodada** (o recurso estava em uso por outro
eixo; nenhuma destas checagens foi executada):

- `verificar.py e1_resumos` — critério 1.6. Não pude confirmar que a listagem de resumos em
  `E1/verificacao_E1.txt` ainda reproduz, nem se `_detectar_idioma` acerta nos 8 artigos hoje.
- `verificar.py e2` — critérios 2.2 (metadados completos em todos os 659 chunks) e 2.4 (dimensão do
  vetor). Medi a contagem e a distribuição de `tipo_chunk` lendo o ChromaDB direto na sonda (sem
  Ollama), mas não rodei a checagem oficial.
- `verificar.py e3` — critérios 3.1–3.6 no corpus de 8 artigos. Não sei se `ordenado`, `campos` e "todos
  obedecem" continuam `True`, nem qual é o resultado real de 3.6 com o filtro novo (`ano>=2030`).
- `verificar.py e4` e `e4_limiar` — critérios 4.1–4.4 e a margem do limiar. O achado A1-06 mediu a
  margem atual (0,6566); não repeti.
- `verificar.py e6_ollama_desligado` e `e6_ollama_desligado_scripts` — critério 6.7. Só analisei o código
  e o glob; não exercitei os scripts com o servidor fora do ar. (O único subprocesso que rodei foi
  `scripts/00_checar_ambiente.py` apontado para uma porta morta, que não estabelece conexão com o
  Ollama.)

**Não verificável sem efeito colateral** (proibido pelo protocolo, §9):

- **2.5 (idempotência da indexação)** — exige rodar `scripts/02_indexar.py` duas vezes (~24 min cada,
  recria a coleção). Não há checagem automatizada para esse critério, e sua evidência é a do corpus de
  6 artigos (A2-01). É a lacuna de verificação mais larga que encontrei em E2.
- **7.1 (notebook de ponta a ponta)** — exige `executar_notebook.py` sem `--offline`, que sobrescreve as
  saídas versionadas. Rodei só `e7_saidas`, que lê o `.ipynb` salvo.
- **5b.1 (top-4 do Shapley pré-computado)** — confirmar se os 4 chunks de `resultados/shapley_chunks.json`
  ainda são o top-4 da mesma pergunta exige um embedding. Achado A2-12 fica com confiança média por isso.

**Fora do alcance por outro motivo:**

- **Conteúdo visual dos 8 PNGs de `E8/capturas/`** — abri a listagem e os nomes, mas não inspecionei as
  imagens para dizer se cada uma demonstra o critério que o nome promete. Isso é do eixo A4, que tem o
  `capturar_evidencias_e8.py` no escopo.
- **`docs/evidencias/auditoria_plano.html` (40 KB)** — li o Registro que o descreve, não o documento
  inteiro; é a versão navegável da auditoria de 14/09, superada pelos tickets #1–#23.
- **`docs/evidencias/E7/webinario_rag_offline.ipynb` (189 KB)** — não comparei célula a célula com o
  `webinario_rag.ipynb` versionado; é escopo de A3.
- **Causa da anotação `exit=0` em `E6/ollama_desligado.txt`** (A2-09) — provavelmente o código de saída
  do `tee` e não o do Python, mas não há registro do comando usado, então é hipótese.
- **`docs/medicoes.md` e `docs/troubleshooting.md` como um todo** — só conferi as linhas que citam
  arquivos de `docs/evidencias/`. O documento inteiro é do eixo A5.
