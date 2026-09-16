# A5 — Documentação e números (RODADA-1)

**Eixo:** A5 · **Escopo:** `README.md`, `CLAUDE.md`, `docs/medicoes.md`, `docs/troubleshooting.md`,
`docs/ESTADO_ATUAL.md`, plano de aula v1.1 (`ferramentas/gerar_plano_v11.py` + `.docx` em `docs/`).
**Pergunta central:** todo número e toda afirmação batem com o código e com a última medição desta máquina?

**Data:** 2026-09-16 · **HEAD auditado:** `eec1ecc` · **Branch:** `chore/agent-skills-setup` · **Só leitura.**

Sonda versionada: [`A5-sonda.py`](A5-sonda.py) / [`A5-sonda.txt`](A5-sonda.txt).

Checagens estáticas rodadas (nenhuma usa Ollama):

```
.venv/Scripts/python.exe ferramentas/verificar.py e9_numeros   # exit 0
.venv/Scripts/python.exe ferramentas/verificar.py e7_saidas    # exit 0
.venv/Scripts/python.exe docs/auditoria/rodadas/RODADA-1/A5-sonda.py   # exit 0
```

**O que essas checagens cobrem e o que NÃO cobrem.** `e9_numeros` só confere números escritos com a
frase literal *"na última execução do notebook"* (achou 3: `190,7`, `50`, `17,9`, todos confirmados).
`e7_saidas` só extrai 4 tempos do `.ipynb` e os imprime — **não compara com nada**. Resultado: as
duas saem com `exit 0` enquanto **sete** outras células numéricas de `docs/medicoes.md` estão
defasadas, porque nenhuma delas usa aquela frase. Todos os achados A5-01 a A5-07 estão na zona cega
dessas duas checagens.

**Resumo:** 20 achados — 7 alta, 9 média, 4 baixa.

| ID | Sev. | Onde | Assunto |
|---|---|---|---|
| A5-01 | alta | `docs/medicoes.md:20` | "Chunking (556 chunks) / 9,0 s" × evidência citada diz 659 / 8,8 s |
| A5-02 | alta | `docs/medicoes.md:21` | Indexação "1104,1 s" foi removida da evidência citada, que hoje diz 1420,0 s |
| A5-03 | alta | `README.md:114`, `CLAUDE.md:69,99` | "~20 min / ~19 min" de indexação × 1420 s (23,7 min) medidos |
| A5-04 | alta | `docs/medicoes.md:52` | Extração de metadados "16,6 s" × 190,7 s na evidência citada |
| A5-05 | média | `docs/medicoes.md:51` | Resumo ao vivo "8,1 s" é a execução mais antiga; a atual é 8,9 s |
| A5-06 | alta | `docs/medicoes.md:33` | SHAP no notebook sem o valor atual (50 s) e com data errada |
| A5-07 | alta | `docs/medicoes.md:53,100` | AppTest "3b, 8 s · 17 s" × evidência atual "1.5b, 26–50 s" |
| A5-08 | média | `docs/medicoes.md:3` | "medidos entre 13 e 14/09/2026" × o próprio arquivo cita 15 e 16/09 |
| A5-09 | alta | `docs/troubleshooting.md:50-52` | "ainda não há artigos em português no corpus" é falso desde o T12 |
| A5-10 | média | `docs/troubleshooting.md:47` | "556 embeddings … 1141 s / 1111 s" |
| A5-11 | média | `README.md:5,179-181`, `troubleshooting.md:24`, `medicoes.md:100` | 3b descrito como padrão / instrução "troque para o 1.5b" sem sentido |
| A5-12 | média | `README.md:173-177` | Seção de auditoria lista como contestados critérios já resolvidos |
| A5-13 | média | `CLAUDE.md:20,30,43` | "6 PDFs do corpus", "branch `main`", "lote #11 a #23" |
| A5-14 | baixa | `CLAUDE.md:106` | Tabela documenta 10 dos 15 subcomandos de `verificar.py` |
| A5-15 | média | `ferramentas/gerar_plano_v11.py:9-10`, `README.md:159` | Comando documentado depende de arquivo fora do repositório |
| A5-16 | média | `ferramentas/gerar_plano_v11.py:57-64` × `:83-84` | Plano v1.1 diz 8 artigos e lista 6 nas referências |
| A5-17 | baixa | `docs/ESTADO_ATUAL.md:3,177` | HEAD e contagem de commits errados |
| A5-18 | baixa | `docs/ESTADO_ATUAL.md:142,151` | Status de E1/E10 diferente do de `VERIFICACAO.md` |
| A5-19 | média | `CLAUDE.md:36` | Afirma 6.5 resolvido sem a ressalva do modelo padrão (A1-08) |
| A5-20 | baixa | `docs/medicoes.md:5-10` | Tabela de contexto sem coluna Evidência, contra o que o registro T10 afirma |

---

### A5-01 — `medicoes.md` publica 556 chunks / 9,0 s citando um arquivo que diz 659 chunks / 8,8 s

- **severidade:** alta
- **categoria:** documentacao
- **onde:** `docs/medicoes.md:20`
- **criterio:** 9.1
- **o-que-observei:** a célula diz `| Chunking (556 chunks) | 9,0 s | E7/log_02_indexar.txt |`. O
  arquivo de evidência citado, no HEAD atual, diz `1) Chunking: 659 chunks em 8.8s` e
  `por tipo: {'pagina': 651, 'resumo': 8}`. Nem a contagem nem o tempo aparecem no arquivo citado.
  Segunda entrada: `git show 7e29c38:docs/evidencias/E7/log_02_indexar.txt` mostra que a versão
  anterior do mesmo arquivo dizia `1) Chunking: 556 chunks em 9.0s` — ou seja, o número foi copiado
  corretamente na época e a evidência foi substituída pelo T12/#12 sem que a tabela fosse atualizada.
  O próprio `medicoes.md:10` já diz "8 artigos … 659 chunks", contradizendo a linha 20 dez linhas abaixo.
- **como-reproduzir:**
  ```bash
  grep -n "Chunking" docs/medicoes.md docs/evidencias/E7/log_02_indexar.txt
  git show 7e29c38:docs/evidencias/E7/log_02_indexar.txt | grep -n "Chunking"
  ```
- **saida-obtida:**
  ```
  docs/medicoes.md:20:| Chunking (556 chunks) | 9,0 s | `E7/log_02_indexar.txt` |
  docs/evidencias/E7/log_02_indexar.txt:4:1) Chunking: 659 chunks em 8.8s
  (7e29c38) 4:1) Chunking: 556 chunks em 9.0s
  ```
- **por-que-importa:** é o primeiro número da seção 9.1 e o único lugar onde o custo do chunking é
  publicado. Um participante que compara o próprio tempo com a tabela compara contra um corpus
  17 % menor. Viola o invariante 6 do `ESTADO_ATUAL.md` ("todo número publicado vem de medição
  **nesta** máquina, com data e comando"): o comando e o arquivo estão lá, mas já não produzem o número.
- **confianca:** alta
- **relacionado:** A5-02, A5-04, A5-10

### A5-02 — Indexação: o valor 1104,1 s foi apagado da evidência citada, que hoje registra 1420,0 s

- **severidade:** alta
- **categoria:** documentacao
- **onde:** `docs/medicoes.md:21`
- **criterio:** 9.1, 2.8
- **o-que-observei:** a linha publica `1141,1 s · 1111,0 s · 1104,1 s`, citando
  `E2/02_indexar_execucao1.txt`, `E2/02_indexar_execucao2.txt` e `E7/log_02_indexar.txt`. As duas
  primeiras evidências conferem (1141.1 s e 1111.0 s), **mas ambas são do corpus de 556 chunks**. A
  terceira evidência citada hoje diz `659 vetores na coleção 'artigos_rag' em 1420.0s` — 1104,1 não
  existe mais nela. Segunda entrada: `git log -S "1104.1" -- docs/evidencias/E7/log_02_indexar.txt`
  mostra o valor entrando em `7e29c38` e saindo em `4d6a16b` (#12). Ou seja, a única medição de
  indexação do corpus atual (1420,0 s) não está publicada em lugar nenhum de `medicoes.md`, e o
  registro de execuções de `VERIFICACAO.md:296` confirma `02_indexar.py → exit 0 em 1420s`.
- **como-reproduzir:**
  ```bash
  grep -n "Indexação completa" docs/medicoes.md
  grep -n "vetores na" docs/evidencias/E7/log_02_indexar.txt
  git log --oneline -S "1104.1" -- docs/evidencias/E7/log_02_indexar.txt
  ```
- **saida-obtida:**
  ```
  docs/medicoes.md:21:| Indexação completa com `bge-m3` (embeddings + ChromaDB) | 1141,1 s · 1111,0 s · 1104,1 s | ...
  docs/evidencias/E7/log_02_indexar.txt:   659 vetores na coleção 'artigos_rag' em 1420.0s
  4d6a16b Fecha #12: confirma bateria 00-07 completa e reverifica E5/E6/E7
  7e29c38 Material prático do Encontro 2: RAG com Ollama, ChromaDB e Streamlit
  ```
- **por-que-importa:** a decisão 9.3 "Reindexar ao vivo: **Não.** São 1104–1141 s, maior que o bloco 2
  inteiro (18 min = 1080 s)" (`medicoes.md:87`) usa uma faixa que subestima o custo real em ~25 %.
  A conclusão não muda (1420 s continua > 1080 s), mas o número que a sustenta está errado, e é o
  número que o README repete ao participante (A5-03).
- **confianca:** alta
- **relacionado:** A5-01, A5-03, A5-10

### A5-03 — README e CLAUDE.md prometem ~19–20 min de indexação; a última medição desta máquina é 23,7 min

- **severidade:** alta
- **categoria:** documentacao
- **onde:** `README.md:114`, `CLAUDE.md:69`, `CLAUDE.md:99`
- **criterio:** 9.1, 10.1
- **o-que-observei:** `README.md:114` diz "Sem GPU, espere cerca de 20 minutos (1104 a 1141 s na
  máquina de teste, ver docs/medicoes.md)". `CLAUDE.md:69` diz "leva ~19 min em CPU" e `CLAUDE.md:99`
  repete "Reindexa (~19 min)". A única medição pós-T12 é 1420,0 s = 23,7 min
  (`docs/evidencias/E7/log_02_indexar.txt`), confirmada por segunda fonte em `VERIFICACAO.md:296`
  ("`02_indexar.py → exit 0 em 1420s`"). O próprio `ESTADO_ATUAL.md:87,237` já usa a faixa corrigida
  "~19–24 min", o que mostra que as três frases acima ficaram para trás.
- **como-reproduzir:**
  ```bash
  grep -n "20 minutos\|1104" README.md
  grep -n "19 min" CLAUDE.md
  grep -n "vetores na" docs/evidencias/E7/log_02_indexar.txt
  ```
- **saida-obtida:**
  ```
  README.md:114:... Sem GPU, espere cerca de 20 minutos (1104 a 1141 s na máquina de teste, ver [docs/medicoes.md](docs/medicoes.md)).
  CLAUDE.md:69:- A coleção do ChromaDB é recriada do zero a cada `indexar()`: é idempotente e leva ~19 min em CPU.
  CLAUDE.md:99:| `scripts/02_indexar.py` | Reindexa (~19 min) |
  docs/evidencias/E7/log_02_indexar.txt:   659 vetores na coleção 'artigos_rag' em 1420.0s
  ```
- **por-que-importa:** é a etapa mais longa do passo a passo do README e a única que o participante
  roda sozinho em casa sem feedback intermediário de conclusão. Uma subestimativa de ~4 min numa
  espera de 24 min é o tipo de coisa que faz alguém achar que travou e cancelar o `02_indexar.py`
  no meio — e a coleção é recriada do zero, então cancelar custa a execução inteira.
- **confianca:** alta
- **relacionado:** A5-02, A5-10

### A5-04 — Extração de metadados por LLM: "16,6 s (quente)" contra 190,7 s na evidência citada

- **severidade:** alta
- **categoria:** documentacao
- **onde:** `docs/medicoes.md:52` (contradiz `docs/medicoes.md:94`)
- **criterio:** 9.1, 9.4, 2.7
- **o-que-observei:** a linha 52 publica `134,9 s · 136,9 s → 16,6 s`, citando
  `E2/02_indexar_execucao1.txt`, `E7/log_02_indexar.txt` e `E7/saidas_notebook.txt`. Duas das três
  evidências citadas hoje dizem 190,7 s: `log_02_indexar.txt` (`extração em 190.7s`, com
  `qwen2.5:1.5b`) e o bloco mais recente de `saidas_notebook.txt` (`[célula 13] extração: Extração em
  190.7s`). Segunda entrada: `verificar.py e7_saidas` lê o `.ipynb` sem kernel e devolve o mesmo
  190.7s. O valor 16,6 s é a **primeira** execução salva em `saidas_notebook.txt` (linha 28), do
  commit inicial. Dentro do mesmo arquivo, `medicoes.md:94` já diz "extração por LLM 190,7 s na
  última execução do notebook" — a tabela 9.1 e a tabela 9.4 publicam números incompatíveis para a
  mesma operação.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python.exe ferramentas/verificar.py e7_saidas
  grep -n "Extração de metadados\|extração por LLM" docs/medicoes.md
  grep -n "extração em" docs/evidencias/E7/log_02_indexar.txt
  ```
- **saida-obtida:**
  ```
  [célula 13] extração: Extração em 190.7s
  docs/medicoes.md:52:| Extração de metadados por LLM, frio → quente | 134,9 s · 136,9 s → 16,6 s | ...
  docs/medicoes.md:94:... extração por LLM 190,7 s na última execução do notebook (2026-09-15, ...)
  docs/evidencias/E7/log_02_indexar.txt:   extração em 190.7s
  ```
- **por-que-importa:** o bloco 2 (Indexação) tem 18 min de cronograma. A tabela 9.1 sugere 16,6 s
  para a demo de metadados por LLM; a medição real é 190,7 s — 11× mais. Quem planeja o bloco pela
  tabela 9.1 (e não pela nota da 9.4) subdimensiona a única operação lenta que ainda roda ao vivo ali.
- **confianca:** alta
- **relacionado:** A5-05, A5-06

### A5-05 — "Resumo ao vivo no notebook | 8,1 s" é a execução mais antiga salva, não a atual

- **severidade:** média
- **categoria:** documentacao
- **onde:** `docs/medicoes.md:51`
- **criterio:** 9.1, 7.2
- **o-que-observei:** a linha publica `8,1 s` citando `E7/saidas_notebook.txt`. O número existe no
  arquivo — na linha 35, que é o dump do commit inicial. O notebook versionado hoje diz
  `RESUMO AO VIVO (8.9s)`, e o arquivo de evidência registra quatro execuções posteriores
  (14.5 s, 11.9 s, 8.9 s). Segunda entrada: `grep "RESUMO AO VIVO" webinario_rag.ipynb` devolve 8.9s
  direto do `.ipynb`, sem passar pelo arquivo de evidência. É exatamente o caso "tempo copiado de
  execução que não é a mais recente", e passa despercebido por `e9_numeros` porque a célula não usa
  a frase "na última execução do notebook".
- **como-reproduzir:**
  ```bash
  grep -n "Resumo ao vivo" docs/medicoes.md
  grep -n "RESUMO AO VIVO" docs/evidencias/E7/saidas_notebook.txt
  grep -o "RESUMO AO VIVO ([0-9.]*s)" webinario_rag.ipynb
  ```
- **saida-obtida:**
  ```
  docs/medicoes.md:51:| Resumo ao vivo no notebook | 8,1 s | `E7/saidas_notebook.txt` |
  saidas_notebook.txt:35:stream: RESUMO AO VIVO (8.1s): ...
  saidas_notebook.txt:547:    [célula 15] resumo ao vivo: RESUMO AO VIVO (14.5s)
  saidas_notebook.txt:578:    [célula 15] resumo ao vivo: RESUMO AO VIVO (11.9s)
  saidas_notebook.txt:607:    [célula 15] resumo ao vivo: RESUMO AO VIVO (8.9s)
  webinario_rag.ipynb: "RESUMO AO VIVO (8.9s)
  ```
- **por-que-importa:** a diferença absoluta é pequena (0,8 s), mas o padrão é o problema: o número
  aponta para um arquivo que contém cinco valores diferentes e o publicado é o mais antigo. Quem
  audita o critério 9.1 encontrando o número no arquivo dá por confirmado sem perceber a defasagem —
  foi exatamente o que aconteceu no registro do T10 (`VERIFICACAO.md:290`).
- **confianca:** alta
- **relacionado:** A5-04, A5-06

### A5-06 — SHAP no notebook: histórico sem o valor atual (50 s) e com data de "última execução" errada

- **severidade:** alta
- **categoria:** documentacao
- **onde:** `docs/medicoes.md:33` (contradiz `docs/medicoes.md:97`)
- **criterio:** 9.1, 5a.1, 5a.3
- **o-que-observei:** a linha 33 publica `37 s · 34 s · 48 s · 36 s (última execução: 2026-09-15)`.
  O notebook versionado hoje diz `SHAP em 50s`, e `docs/evidencias/E5/notebook_E5.txt` — a evidência
  citada na própria linha — já foi atualizada para 50 s em 2026-09-16 (registro em
  `VERIFICACAO.md:298`: "tempo do SHAP no notebook … atualizado de 36s para 50s"). Segunda entrada:
  `verificar.py e7_saidas` extrai `[célula 27] shap: SHAP em 50s` direto do `.ipynb`. Dentro do
  próprio `medicoes.md`, a linha 97 (tabela 9.4) já diz "50 s na última execução do notebook,
  2026-09-15" — logo o arquivo publica, para a mesma operação, "última execução = 36 s, 15/09" na
  seção 9.1 e "última execução = 50 s, 15/09" na 9.4, e nenhuma das duas datas é a real (16/09).
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python.exe ferramentas/verificar.py e7_saidas
  grep -n "SHAP no notebook\|SHAP 19–112" docs/medicoes.md
  grep -n "SHAP em" docs/evidencias/E5/notebook_E5.txt
  ```
- **saida-obtida:**
  ```
  [célula 27] shap: SHAP em 50s
  docs/medicoes.md:33:| SHAP no notebook | 37 s · 34 s · 48 s · 36 s (última execução: 2026-09-15) | `E7/saidas_notebook.txt`, `E5/notebook_E5.txt` |
  docs/medicoes.md:97:| 4 SHAP | 12 | SHAP 19–112 s (50 s na última execução do notebook, 2026-09-15, ...
  docs/evidencias/E5/notebook_E5.txt:stream SHAP em 50s
  ```
- **por-que-importa:** 5a.1 foi um critério contestado justamente por defasagem de número de SHAP
  (achado da auditoria de 2026-09-14, corrigido no T08 e no T09) e voltou a defasar no T12. A linha
  33 é o histórico canônico dessa métrica: publicá-la sem o valor corrente reabre o mesmo achado
  que dois tickets já fecharam. A checagem `e9_numeros` não pega porque a linha 33 não usa a frase
  gatilho; a linha 97, que usa, passa.
- **confianca:** alta
- **relacionado:** A5-04, A5-05

### A5-07 — Streamlit: tabela 9.1 e orçamento do bloco 7 usam números do 3b que a evidência citada já não contém

- **severidade:** alta
- **categoria:** documentacao
- **onde:** `docs/medicoes.md:53`, `docs/medicoes.md:100`
- **criterio:** 9.1, 9.4
- **o-que-observei:** a linha 53 publica `Pergunta no Streamlit (AppTest, 3b, k=2 e k=5) | 8 s · 17 s`
  citando `E8/apptest.txt`. O `apptest.txt` atual (regravado em 2026-09-16 pelo ticket #16, com o
  corpus de 659 chunks) registra `modelo qwen2.5:1.5b` e os tempos `44s`, `50s`, `39s`, `28s` e `26s`
  — nem o modelo nem os números da tabela existem mais no arquivo. Segunda entrada:
  `git show 7e29c38:docs/evidencias/E8/apptest.txt` mostra os valores originais
  (`respondida em 8s`, `modelo qwen2.5:3b`, `pergunta 2 respondida em 17s`), e
  `git log -S "em 8s"` mostra a substituição em `5f7f481` (#16). A linha 100 (tabela 9.4) constrói
  em cima disso a conclusão do bloco 7: "8–17 s por pergunta com cache quente (AppTest); 42–118 s
  por resposta sem cache (3b) → ~4 perguntas no pior caso".
- **como-reproduzir:**
  ```bash
  grep -n "AppTest" docs/medicoes.md
  grep -n "respondida em\|modelo qwen" docs/evidencias/E8/apptest.txt
  git show 7e29c38:docs/evidencias/E8/apptest.txt | grep -n "respondida em\|modelo qwen"
  ```
- **saida-obtida:**
  ```
  docs/medicoes.md:53:| Pergunta no Streamlit (AppTest, 3b, k=2 e k=5) | 8 s · 17 s | `E8/apptest.txt` |
  docs/medicoes.md:100:| 7 Streamlit | 15 | 8–17 s por pergunta com cache quente (AppTest); 42–118 s ... | ~4 perguntas no pior caso |
  apptest.txt:4: 8.2 pergunta 1 respondida em 44s | exceção: False | erros: []
  apptest.txt:6: legendas: ['Caminho usado: busca simples · k = 2 · modelo qwen2.5:1.5b']
  apptest.txt:10: pergunta 2 (só k) respondida em 50s
  apptest.txt:13: pergunta 3 (só modo) respondida em 39s
  apptest.txt:16: pergunta 4 (só filtro) respondida em 28s
  (7e29c38) 8.2 pergunta 1 respondida em 8s  /  modelo qwen2.5:3b  /  pergunta 2 respondida em 17s
  ```
- **por-que-importa:** é o único achado do eixo que muda uma conclusão do cronograma. O bloco 7 tem
  15 min; com 8–17 s por pergunta cabem muitas, com 26–50 s medidos hoje cabem bem menos, e o
  "~4 perguntas no pior caso" da coluna "Cabe?" deixa de ter medição que o sustente. O critério 9.4
  ("cada bloco cabe no tempo do cronograma, ou há proposta de ajuste") está ✅ apoiado em números que
  a própria evidência citada substituiu.
- **confianca:** alta
- **relacionado:** A5-11, A5-19

### A5-08 — `medicoes.md` afirma que todos os números são de 13–14/09, mas cita medições de 15 e 16/09

- **severidade:** média
- **categoria:** documentacao
- **onde:** `docs/medicoes.md:3`
- **criterio:** 9.1
- **o-que-observei:** a abertura diz "Todos os números abaixo foram medidos **nesta máquina**, entre
  13 e 14/09/2026". O mesmo arquivo cita explicitamente 2026-09-15 em quatro pontos (linhas 10, 33,
  94, 97, 99) e a linha 10 descreve o corpus de 8 artigos, que só existe desde o T12 (15/09).
  Segunda entrada: o valor de SHAP que a linha 97 chama de "última execução" (50 s) veio de uma
  reexecução de 2026-09-16 (`VERIFICACAO.md:298`), fora do intervalo declarado nos dois sentidos.
- **como-reproduzir:**
  ```bash
  sed -n '1,12p' docs/medicoes.md
  grep -n "2026-09-15\|2026-09-16" docs/medicoes.md
  ```
- **saida-obtida:**
  ```
  docs/medicoes.md:3:Todos os números abaixo foram medidos **nesta máquina**, entre 13 e 14/09/2026. Cada um aponta para o arquivo de evidência de onde saiu.
  docs/medicoes.md:10:| Corpus | 8 artigos (T12/#12, 2026-09-15: +2 em português), 135 páginas, 659 chunks ...
  docs/medicoes.md:33:| SHAP no notebook | ... (última execução: 2026-09-15) | ...
  docs/medicoes.md:94: ... 190,7 s na última execução do notebook (2026-09-15, `E7/saidas_notebook.txt`) ...
  ```
- **por-que-importa:** a frase de abertura é a que dá data ao arquivo inteiro e é o que sustenta o
  invariante 6 ("todo número publicado vem de medição nesta máquina, **com data** e comando"). Como
  a maioria das células não tem data própria, quem lê não consegue distinguir os números de 13–14/09
  (corpus de 556 chunks, chat 3b) dos de 15–16/09 (659 chunks, chat 1.5b) — e essa é justamente a
  distinção que separa os achados A5-01, A5-02, A5-04, A5-06 e A5-07 dos números ainda válidos.
- **confianca:** alta
- **relacionado:** A5-01, A5-20

### A5-09 — Troubleshooting afirma que não há artigos em português; há dois desde o T12

- **severidade:** alta
- **categoria:** risco-ao-vivo
- **onde:** `docs/troubleshooting.md:50-52`
- **criterio:** 10.3, 3.4, 1.8
- **o-que-observei:** a entrada "O filtro `idioma = pt` não traz nada" diz, na causa, "ainda não há
  artigos em português no corpus. O resultado vazio é o comportamento esperado", e a resposta pronta
  para o chat é "Ainda não há artigos em português. Esse filtro volta vazio de propósito". O
  `metadados.csv` tem 8 linhas, duas com `idioma = pt` (`rocha2025_ragsft.pdf`,
  `medeiros2025_embeddings_pt.pdf`), acrescentadas pelo T12/#12. Segunda entrada, independente do
  CSV: `docs/evidencias/E8/apptest.txt:14` mostra `medeiros2025_embeddings_pt.pdf` entre os artigos
  escolhidos pelo estágio 1 do app real. O próprio registro de execuções (`VERIFICACAO.md:295`)
  documenta que `verificar.py`, `scripts/03` e `scripts/04` foram trocados por um filtro de ano
  justamente porque `idioma=pt` deixou de voltar vazio — `troubleshooting.md` ficou de fora dessa
  correção.
- **como-reproduzir:**
  ```bash
  sed -n '50,53p' docs/troubleshooting.md
  .venv/Scripts/python.exe -c "import csv;print([(x['arquivo'],x['idioma']) for x in csv.DictReader(open('metadados.csv',encoding='utf-8'))])"
  ```
- **saida-obtida:**
  ```
  ### O filtro `idioma = pt` não traz nada
  - **Causa:** ainda não há artigos em português no corpus. O resultado vazio é o comportamento esperado e não gera erro (E3 critério 3.6).
  - **Resposta:** "Ainda não há artigos em português. Esse filtro volta vazio de propósito."

  [('lewis2020_rag.pdf','en'), ..., ('rocha2025_ragsft.pdf','pt'), ('medeiros2025_embeddings_pt.pdf','pt')]
  ```
- **por-que-importa:** `troubleshooting.md` é descrito no próprio arquivo como "escrito para o João
  copiar e colar no chat" durante a aula. Se alguém marcar o filtro `idioma = pt` na barra lateral do
  Streamlit (é um dos controles demonstrados no bloco 7), agora **vêm** resultados, e a resposta
  pronta do suporte contradiz a tela na frente dos participantes. O critério 10.3 pede que o
  troubleshooting cubra os erros realmente encontrados; esta entrada cobre um comportamento que
  deixou de existir.
- **confianca:** alta
- **relacionado:** A5-10

### A5-10 — Troubleshooting publica "556 embeddings … 1141 s / 1111 s" para o corpus de 659

- **severidade:** média
- **categoria:** documentacao
- **onde:** `docs/troubleshooting.md:46-48`
- **criterio:** 10.3, 9.1
- **o-que-observei:** a entrada "A indexação demora quase 20 minutos" atribui a causa a "gerar os
  556 embeddings do `bge-m3` em CPU levou 1141 s na 1ª execução e 1111 s na 2ª". São 659 embeddings
  desde o T12 e a única medição desse corpus é 1420,0 s (23,7 min), conforme
  `docs/evidencias/E7/log_02_indexar.txt` e `VERIFICACAO.md:296`. O título da entrada ("quase 20
  minutos") herda a mesma subestimativa do A5-03. Segunda entrada: `git show 7e29c38:...log_02_indexar.txt`
  confirma que 556/1104,1 s pertencem ao corpus antigo.
- **como-reproduzir:**
  ```bash
  sed -n '46,49p' docs/troubleshooting.md
  grep -n "chunks em\|vetores na" docs/evidencias/E7/log_02_indexar.txt
  ```
- **saida-obtida:**
  ```
  ### A indexação demora quase 20 minutos
  - **Causa:** gerar os 556 embeddings do `bge-m3` em CPU levou 1141 s na 1ª execução e 1111 s na 2ª.
  ---
  1) Chunking: 659 chunks em 8.8s
     659 vetores na coleção 'artigos_rag' em 1420.0s
  ```
- **por-que-importa:** mesma resposta pronta de chat do A5-09. Um participante que pergunta "quanto
  falta?" recebe uma expectativa de 18–19 min para uma operação de ~24 min, no momento em que ele
  mais tende a cancelar.
- **confianca:** alta
- **relacionado:** A5-03, A5-09

### A5-11 — Três documentos ainda tratam `qwen2.5:3b` como padrão e mandam "trocar para o 1.5b"

- **severidade:** média
- **categoria:** documentacao
- **onde:** `README.md:5`, `README.md:179-181`, `docs/troubleshooting.md:24`, `docs/medicoes.md:100`
- **criterio:** 9.3, 10.1, 6.6
- **o-que-observei:** `config.py:17-18` tem `MODELO_CHAT = "qwen2.5:1.5b"` e
  `MODELO_CHAT_PLANO_B = "qwen2.5:3b"` desde o ticket #19, com o `why:` da decisão em `config.py:14-16`.
  Mesmo assim: `README.md:5` diz "o modelo de chat (`qwen2.5:3b`, com plano B `qwen2.5:1.5b`)";
  a seção `README.md:179-181` ("Trocar para o modelo menor") instrui "mude `MODELO_CHAT` em
  `config.py` para `\"qwen2.5:1.5b\"`", que já é o valor do arquivo; `troubleshooting.md:24` manda
  "troque para o `qwen2.5:1.5b` na barra lateral do app ou em `config.py`", sendo que
  `app.py:52` já monta o seletor como `[config.MODELO_CHAT, config.MODELO_CHAT_PLANO_B]` = 1.5b
  primeiro; e `medicoes.md:100` propõe como ajuste do bloco 7 "1.5b se estiver lento". Segunda
  entrada, independente da leitura de `config.py`: `docs/evidencias/E8/apptest.txt:6` mostra a
  legenda real do app, `modelo qwen2.5:1.5b`.
- **como-reproduzir:**
  ```bash
  sed -n '17,18p' config.py
  grep -n "qwen2.5:3b, com plano B\|Trocar para o modelo menor" README.md
  sed -n '179,181p' README.md
  sed -n '24p' docs/troubleshooting.md
  grep -n "modelo qwen" docs/evidencias/E8/apptest.txt
  ```
- **saida-obtida:**
  ```
  config.py:17:MODELO_CHAT = os.getenv("MODELO_CHAT", "qwen2.5:1.5b")
  config.py:18:MODELO_CHAT_PLANO_B = "qwen2.5:3b"
  README.md:5:- **Ollama** serve o modelo de embedding (`bge-m3`) e o modelo de chat (`qwen2.5:3b`, com plano B `qwen2.5:1.5b`).
  README.md:181:Se as respostas estiverem lentas, mude `MODELO_CHAT` em `config.py` para `"qwen2.5:1.5b"`, ou defina a variável de ambiente `MODELO_CHAT=qwen2.5:1.5b`. Nada mais precisa mudar.
  docs/troubleshooting.md:24:- **Resposta:** "Feche abas e programas pesados. Se continuar lento, troque para o `qwen2.5:1.5b` na barra lateral do app ou em `config.py`."
  docs/evidencias/E8/apptest.txt:6:  legendas: ['Caminho usado: busca simples · k = 2 · modelo qwen2.5:1.5b']
  ```
- **por-que-importa:** a instrução de plano B é a que o facilitador usa quando a máquina engasga ao
  vivo — e hoje ela não faz nada, porque o valor sugerido já é o corrente. Pior: quem seguir o
  `README.md:5` vai esperar o 3b e comparar tempos contra a tabela de tempos do 3b (A5-07), sem
  saber que o padrão é outro. A decisão do #19 está documentada em `config.py:14-16`, mas não
  chegou a nenhum dos quatro pontos acima.
- **confianca:** alta
- **relacionado:** A5-07, A5-19

### A5-12 — Seção "Auditoria de código (E10)" do README lista como contestados critérios já resolvidos

- **severidade:** média
- **categoria:** documentacao
- **onde:** `README.md:173-177`
- **criterio:** 10.1, 10.3
- **o-que-observei:** `README.md:177` diz que a auditoria "lista achados e um conjunto de critérios
  contestados (1.6, 4.4, 6.5, 6.7, 7.4, 8.2/8.4/8.5/8.7, 5a.1/7.2/9.1) para reverificar antes da
  próxima etapa". O `CLAUDE.md:34-42` já marca com `~~tachado~~` e "Resolvido" os critérios 4.4
  (#6/#7), 6.5 (#1/#3/#4), 7.4 (#2), 5a.1/7.2 (#8) e 9.1 (#10); o `VERIFICACAO.md` (linhas 281–294)
  registra cada um. Segunda entrada, independente do CLAUDE.md: `ESTADO_ATUAL.md:142-151` lista como
  pendências só 6.7 e 8.2/8.4/8.5/8.7. O README também não menciona a auditoria RODADA-1 (issues
  #27–#36), que é o processo em curso segundo `VERIFICACAO.md:50-79`.
- **como-reproduzir:**
  ```bash
  sed -n '173,178p' README.md
  grep -n "Resolvido no ticket\|Resolvido: " CLAUDE.md
  ```
- **saida-obtida:**
  ```
  README.md:177:A auditoria **não mudou nenhum ✅** ... um conjunto de critérios contestados (1.6, 4.4, 6.5, 6.7, 7.4, 8.2/8.4/8.5/8.7, 5a.1/7.2/9.1) para reverificar antes da próxima etapa ...
  CLAUDE.md:35: - **4.4** — ~~...~~ Resolvido: `rag.buscar_dois_estagios()` usa `config.DISTANCIA_MAXIMA_ESTAGIO_1` ...
  CLAUDE.md:36: - **6.5** — ~~...~~ Resolvido no ticket #1 (T01) ...
  CLAUDE.md:38: - **7.4** — ~~...~~ Resolvido no ticket #2 (T02) ...
  ```
- **por-que-importa:** o README é o documento público do material. Publicar como "em aberto" seis
  critérios que foram fechados com evidência subestima o estado do trabalho e, ao mesmo tempo,
  esconde a auditoria que está de fato em curso. Quem lê só o README tem um retrato do repositório
  com dois dias de atraso e uma lista de pendências que não corresponde a nenhum documento interno.
- **confianca:** alta
- **relacionado:** A5-13, A5-18

### A5-13 — CLAUDE.md descreve corpus de 6 PDFs, branch `main` e um lote de tickets encerrado

- **severidade:** média
- **categoria:** documentacao
- **onde:** `CLAUDE.md:20`, `CLAUDE.md:30`, `CLAUDE.md:43`
- **criterio:** 1.1, 10.5
- **o-que-observei:** três afirmações do bloco "Estado atual" do arquivo de instruções do projeto:
  (a) `:43` — "`arquivosPDF/artigos/`: os 6 PDFs do corpus"; são 8 desde o T12, e o próprio
  `CLAUDE.md:53` descreve os 8 doze linhas abaixo, contradizendo a si mesmo;
  (b) `:30` — "O git está na branch `main`"; `git rev-parse --abbrev-ref HEAD` devolve
  `chore/agent-skills-setup`;
  (c) `:20` — "Lote em execução (2026-09-15): tickets #11 a #23"; esses tickets estão fechados
  (`ESTADO_ATUAL.md:158`) e o lote corrente é #27–#36 (`VERIFICACAO.md:50-68`).
  Segunda entrada para (a): `metadados.csv` tem 8 linhas e `config.ARTIGOS_CORPUS` tem 8 chaves.
- **como-reproduzir:**
  ```bash
  grep -n "6 PDFs do corpus\|branch \`main\`\|Lote em execução" CLAUDE.md
  git rev-parse --abbrev-ref HEAD
  .venv/Scripts/python.exe -c "import config;print(len(config.ARTIGOS_CORPUS))"
  ```
- **saida-obtida:**
  ```
  CLAUDE.md:20: Lote em execução (2026-09-15): tickets #11 a #23. ...
  CLAUDE.md:30: Implementado e verificado nas etapas E0–E9 ... O git está na branch `main`. ...
  CLAUDE.md:43: - `arquivosPDF/artigos/`: os 6 PDFs do corpus, baixados por `scripts/01_preparar_corpus.py`.
  chore/agent-skills-setup
  8
  ```
- **por-que-importa:** `CLAUDE.md` é carregado como instrução em toda sessão de agente neste
  repositório. "6 PDFs" e "branch main" são o tipo de premissa que um agente usa sem conferir — por
  exemplo ao decidir se um `git commit` vai para a branch certa, ou ao validar uma contagem de
  chunks. A contradição interna entre `:43` e `:53` torna o arquivo ambíguo sobre o próprio corpus.
- **confianca:** alta
- **relacionado:** A5-17, A5-19

### A5-14 — A tabela de comandos do CLAUDE.md documenta 10 dos 15 subcomandos de `verificar.py`

- **severidade:** baixa
- **categoria:** documentacao
- **onde:** `CLAUDE.md:106`
- **criterio:** 10.1
- **o-que-observei:** a linha lista "e1_resumos, e2, e2_sobreposicao, e2_reabrir, e4,
  e6_ollama_desligado, e6_fontes, e7_duplicadas e e7_estrutura" (mais `e3` no exemplo). A sonda
  compara com as funções públicas definidas em `ferramentas/verificar.py`: são 15. Ficam de fora da
  documentação `e4_limiar`, `e6_ollama_desligado_scripts`, `e7_duplicadas_antes_v2`, `e7_saidas` e
  `e9_numeros` — os cinco criados nos tickets #6, #8 e #10 e pelo T02. Segunda entrada:
  `ESTADO_ATUAL.md:118-120` lista as 15 corretamente, o que mostra que a lacuna é do `CLAUDE.md` e
  não da leitura. Nenhum comando documentado deixou de existir (a sonda confere os dois sentidos).
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python.exe docs/auditoria/rodadas/RODADA-1/A5-sonda.py
  ```
- **saida-obtida:**
  ```
  == 2) subcomandos de verificar.py documentados x definidos ==
    definidos  (15): ['e1_resumos', 'e2', 'e2_reabrir', 'e2_sobreposicao', 'e3', 'e4', 'e4_limiar', 'e6_fontes', 'e6_ollama_desligado', 'e6_ollama_desligado_scripts', 'e7_duplicadas', 'e7_duplicadas_antes_v2', 'e7_estrutura', 'e7_saidas', 'e9_numeros']
    documentados (10) em CLAUDE.md: [...]
    definidos e NAO documentados: ['e4_limiar', 'e6_ollama_desligado_scripts', 'e7_duplicadas_antes_v2', 'e7_saidas', 'e9_numeros']
    documentados e NAO definidos: []
  ```
- **por-que-importa:** `e9_numeros` e `e7_saidas` são exatamente as checagens que existem para
  impedir os achados A5-04, A5-05 e A5-06. Não estarem na única tabela de comandos do `CLAUDE.md`
  ajuda a explicar por que não foram rodadas depois do T12. O `README.md` (tabela de manutenção,
  linhas 162-169) não menciona `verificar.py` em nenhuma linha.
- **confianca:** alta
- **relacionado:** A5-04, A5-06

### A5-15 — `gerar_plano_v11.py` documentado no README depende de um `.docx` que não está no repositório

- **severidade:** média
- **categoria:** reprodutibilidade
- **onde:** `ferramentas/gerar_plano_v11.py:9-10`, `README.md:159`
- **criterio:** 10.4, 10.1
- **decisao-documentada:** o único comentário `why:` do arquivo está em `gerar_plano_v11.py:162-163`
  e trata de outra coisa — justifica gerar a evidência do 10.4 dentro do próprio script "em vez de
  depender de uma conferência manual não versionada (ticket #18)". Ele não menciona nem justifica a
  dependência de um arquivo de entrada fora do repositório; a decisão registrada não cobre este caso.
- **o-que-observei:** `ORIGEM = Path(sys.argv[1]) if len(sys.argv) > 1 else next((Path.home() /
  "Downloads").glob("Plano_Aula_2-*v1.0.docx"))`. A sonda confirma 0 cópias do `v1.0.docx` dentro do
  repositório e 2 em `~/Downloads`, fora dele. O `README.md:159` lista
  `python ferramentas/gerar_plano_v11.py` na tabela "Para quem mantém o material" sem nenhuma nota
  de pré-requisito; a tabela de comandos (linha 169) apenas repete "Gera o plano de aula v1.1 em
  `docs/`". O `CLAUDE.md:46` registra a localização do v1.0 ("`C:\Users\roger\Downloads\`"), mas o
  README — que é o documento de quem replica — não. Sem argumento e sem o arquivo, o `next()` sem
  default levanta `StopIteration` (não rodei o script: ele sobrescreve `docs/*.docx` e
  `docs/evidencias/E10/plano_v11.txt`, o que a salvaguarda de só leitura proíbe).
- **como-reproduzir:**
  ```bash
  sed -n '9,11p' ferramentas/gerar_plano_v11.py
  .venv/Scripts/python.exe docs/auditoria/rodadas/RODADA-1/A5-sonda.py
  ```
- **saida-obtida:**
  ```
  ORIGEM = Path(sys.argv[1]) if len(sys.argv) > 1 else next(
      (Path.home() / "Downloads").glob("Plano_Aula_2-*v1.0.docx"))
  ---
  == 4) gerar_plano_v11.py: origem do .docx v1.0 ==
    copias do v1.0 dentro do repositorio: 0
    copias do v1.0 em ~/Downloads (fora do repo): 2
  ```
- **por-que-importa:** é o único comando da tabela de manutenção do README que não funciona numa
  cópia limpa do repositório, e falha com `StopIteration` — não com uma mensagem que diga o que
  falta. O critério 10.4 (".docx v1.1") só é reproduzível na máquina do autor.
- **confianca:** alta
- **relacionado:** A5-16

### A5-16 — Plano v1.1: "8 artigos como base documental" e 6 entradas nas Referências

- **severidade:** média
- **categoria:** documentacao
- **onde:** `ferramentas/gerar_plano_v11.py:57-64` × `ferramentas/gerar_plano_v11.py:82-84`,
  `docs/evidencias/E10/plano_v11.txt`
- **criterio:** 10.4, 1.8
- **decisao-documentada:** o `why:` em `gerar_plano_v11.py:162-163` cobre só a geração da evidência
  do 10.4; não há comentário registrando uma decisão de manter as referências restritas aos artigos
  do arXiv. Nada na região justifica a divergência.
- **o-que-observei:** a lista de Material Didático (linhas 82-84) foi atualizada pelo T12 e diz
  "8 artigos como base documental (6 do arXiv + 2 em português, via SBBD e SEMISH)". A lista de
  Referências (linhas 57-64) continua com 6 itens: Lewis, Karpukhin, Gao, Es, Asai, Liu. Rocha et al.
  2025 (SBBD) e Medeiros & Oliveira 2025 (SEMISH) não aparecem. Segunda entrada, lendo o `.docx`
  gerado e não o script: `docs/evidencias/E10/plano_v11.txt` (saída do próprio `gerar_plano_v11.py`)
  mostra os mesmos 6 parágrafos "1. LEWIS … 6. LIU" e o parágrafo de Material Didático com "8 artigos".
  O `README.md:99-106` lista os 8 corretamente, então a lacuna é só do plano.
- **como-reproduzir:**
  ```bash
  sed -n '57,64p;82,84p' ferramentas/gerar_plano_v11.py
  grep -n "LEWIS\|LIU\|ROCHA\|MEDEIROS\|base documental" docs/evidencias/E10/plano_v11.txt
  ```
- **saida-obtida:**
  ```
  [normal] Material didático: ... e 8 artigos como base documental (6 do arXiv + 2 em português, via SBBD e SEMISH). ...
  [normal] 1. LEWIS, P. et al. ... NeurIPS, 2020.
  [normal] 2. KARPUKHIN, V. et al. ... EMNLP, 2020.
  [normal] 3. GAO, Y. et al. ... arXiv:2312.10997, 2023.
  [normal] 4. ES, S. et al. ... arXiv:2309.15217, 2023.
  [normal] 5. ASAI, A. et al. ... ICLR, 2024.
  [normal] 6. LIU, N. F. et al. ... TACL, 2024.
  (nenhuma linha com ROCHA ou MEDEIROS)
  ```
- **por-que-importa:** o `.docx` v1.1 é o documento formal entregue ao CIIA. Um plano que afirma 8
  artigos e referencia 6 é inconsistente na leitura de quem aprova o material, e os dois artigos em
  português — que são a resposta ao critério 1.8 e o diferencial do corpus para a turma brasileira —
  ficam sem citação bibliográfica.
- **confianca:** alta
- **relacionado:** A5-15

### A5-17 — `ESTADO_ATUAL.md` declara um HEAD e uma contagem de commits que não conferem

- **severidade:** baixa
- **categoria:** documentacao
- **onde:** `docs/ESTADO_ATUAL.md:3`, `docs/ESTADO_ATUAL.md:177`
- **criterio:** — (contexto de partida da auditoria, `PROTOCOLO_AUDITORIA.md:7`)
- **o-que-observei:** o cabeçalho diz "**Data do levantamento:** 2026-09-16 · **Branch:**
  `chore/agent-skills-setup` · **HEAD:** `4d6a16b`". O arquivo foi modificado depois disso em dois
  commits (`git log -- docs/ESTADO_ATUAL.md` → `4402884` do #27 e `eec1ecc` do #28), e o HEAD atual
  é `eec1ecc`. A §7 diz "25 commits desde o inicial"; `git rev-list --count HEAD` = 36 e
  `git rev-list --count 4d6a16b` = 34 — a contagem não bate nem com o HEAD declarado (segunda
  entrada, mesma pergunta em dois pontos da história). A branch declarada está correta.
- **como-reproduzir:**
  ```bash
  sed -n '3p;177p' docs/ESTADO_ATUAL.md
  git rev-list --count HEAD; git rev-list --count 4d6a16b
  git log --oneline -- docs/ESTADO_ATUAL.md
  ```
- **saida-obtida:**
  ```
  **Data do levantamento:** 2026-09-16 · **Branch:** `chore/agent-skills-setup` · **HEAD:** `4d6a16b`
  - Branch `chore/agent-skills-setup`, 25 commits desde o inicial; `main` também existe no remoto.
  36
  34
  eec1ecc Fecha #28: calibra protocolo e prompts com o aprendizado do piloto
  4402884 Fecha #27: piloto do ciclo de auditoria no eixo A1
  ```
- **por-que-importa:** `ESTADO_ATUAL.md` é leitura obrigatória de todos os seis eixos e o protocolo
  o define como o contexto de partida. Um auditor que tomar `4d6a16b` como o commit auditado deixa de
  fora o piloto A1 (#27) e a calibração do protocolo (#28) — que são justamente o que ele precisa
  conhecer. O restante do arquivo é preciso: conferi as 21 contagens de linhas da §3.2 uma a uma
  (todas batem, inclusive `rag.py` 485 e `verificar.py` 499) e as citações `rag.py:250/347/358-366`
  da §3.1 (todas apontam para o que o texto diz).
- **confianca:** alta
- **relacionado:** A5-13, A5-18

### A5-18 — Status de E1 e E10 divergem entre `ESTADO_ATUAL.md` e `VERIFICACAO.md`

- **severidade:** baixa
- **categoria:** documentacao
- **onde:** `docs/ESTADO_ATUAL.md:142`, `docs/ESTADO_ATUAL.md:151`
- **criterio:** 1.8, 10.1
- **o-que-observei:** duas divergências na tabela §5:
  (a) E10 — `ESTADO_ATUAL.md:151` diz "⏸️ parcial"; o resumo de `VERIFICACAO.md:34` diz
  "✅ (10.1 ⏸️ macOS/Linux)". São rótulos diferentes para o mesmo estado, e só um deles é o que o
  documento-fonte declara.
  (b) E1 — `ESTADO_ATUAL.md:142` diz "✅ / — (1.8 fechada pelo T12)", que bate com a tabela detalhada
  de E1 (`VERIFICACAO.md:113`, 1.8 ✅), mas **não** com o resumo de `VERIFICACAO.md:25`, que ainda diz
  "✅ (1.8 ⏸️)". Segunda entrada: o registro de execuções (`VERIFICACAO.md:295`) diz explicitamente
  "Critério 1.1 (contagem) e 1.8 (artigos PT) atualizados para ✅".
  Registro o achado aqui porque o arquivo do meu escopo é o `ESTADO_ATUAL.md`; a linha 25 do
  `VERIFICACAO.md` é do eixo A2.
- **como-reproduzir:**
  ```bash
  sed -n '139,152p' docs/ESTADO_ATUAL.md
  sed -n '24,35p' docs/VERIFICACAO.md
  sed -n '113p' docs/VERIFICACAO.md
  ```
- **saida-obtida:**
  ```
  ESTADO_ATUAL.md:142:| E1 Corpus e metadados | ✅ | — (1.8 fechada pelo T12) |
  ESTADO_ATUAL.md:151:| E10 Documentação | ⏸️ parcial | 10.1 verificado só no Windows; ...
  VERIFICACAO.md:25:| E1 | Corpus e metadados | ✅ (1.8 ⏸️) | `docs/evidencias/E1/` |
  VERIFICACAO.md:34:| E10 | Documentação e plano v1.1 | ✅ (10.1 ⏸️ macOS/Linux) | `docs/evidencias/E10/` |
  VERIFICACAO.md:113:| 1.8 | Artigos em português (1–2) | T12/#12 ... | ✅ |
  ```
- **por-que-importa:** `ESTADO_ATUAL.md:9-10` declara que a fonte de verdade é o `VERIFICACAO.md`.
  Onde os dois discordam, o auditor não tem como saber qual lado está defasado sem ir ao registro de
  execuções. No caso de E1 o `ESTADO_ATUAL` está certo e o resumo do `VERIFICACAO` está errado; no
  de E10 é o inverso.
- **confianca:** alta
- **relacionado:** A5-12, A5-17

### A5-19 — CLAUDE.md declara 6.5 resolvido sem a ressalva do modelo padrão atual

- **severidade:** média
- **categoria:** documentacao
- **onde:** `CLAUDE.md:36`
- **criterio:** 6.5
- **o-que-observei:** o bullet tacha o achado original e afirma, sem condicionantes, que "Fontes
  citadas" passou a aparecer "separado de 'Trechos enviados ao prompt' (o top-k bruto)" no notebook
  e que `app.py` "marca ✅ citado nos trechos de `rag.fontes_da_resposta()`". O achado A1-08 do
  piloto mostrou que, com `MODELO_CHAT = qwen2.5:1.5b` (padrão desde o #19), o modelo frequentemente
  não emite `[n]`, o fallback de `rag.py:365` (`indices_citados(...) or list(range(...))`) dispara e
  "citadas" volta a ser o top-k inteiro. Medi contra uma segunda entrada, o AppTest real do #16:
  `apptest.txt:11` registra `k=5 → citadas: [1, 2, 3, 4, 5]` (degenerou para o top-k), enquanto
  `apptest.txt:7` registra `Fontes (citadas 1 de 2)` e `apptest.txt:18` `Fontes (citadas 1 de 5)`
  (citação parcial funcionando). Ou seja, o comportamento é **intermitente** com o modelo padrão —
  a afirmação do `CLAUDE.md` não é falsa, mas é mais forte do que o observado. Não encontrei
  afirmação mais forte que essa em `README.md` (só "resposta com fontes", `:14`) nem em
  `docs/roteiro_facilitador.md` (`:86`, "devolve as fontes"; `:99`, "o expander … mostra arquivo,
  página, trecho e resumo") — nenhum dos dois promete distinção entre citado e recuperado.
- **como-reproduzir:**
  ```bash
  grep -n "6.5" CLAUDE.md
  grep -n "citadas" docs/evidencias/E8/apptest.txt
  sed -n '365p' rag.py
  ```
- **saida-obtida:**
  ```
  apptest.txt:7:  8.4 k=2 → expanders: ['Fontes (citadas 1 de 2) — busca simples'] | fontes na sessão: 2 | citadas: [1]
  apptest.txt:11: 8.4 k=5 → fontes na última resposta: 5 | citadas: [1, 2, 3, 4, 5] | ...
  apptest.txt:18: 8.7/T04 rótulo do último expander: 'Fontes (citadas 1 de 5) — dois estágios'
  rag.py:365:    indices = indices_citados(texto, len(resultados)) or list(range(1, len(resultados) + 1))
  ```
- **por-que-importa:** 6.5 é um critério que já foi contestado uma vez e está ✅ apoiado nessa
  narrativa. Com o modelo padrão, a demonstração ao vivo do bloco 6 pode mostrar "citadas 5 de 5" —
  visualmente indistinguível do bug que os tickets #1/#3/#4 corrigiram. O `CLAUDE.md` é o documento
  que um agente futuro lê antes de decidir se 6.5 precisa de reverificação; sem a ressalva, ele
  conclui que não precisa.
- **confianca:** média
- **relacionado:** A1-08, A5-07, A5-11

### A5-20 — Tabela de contexto de `medicoes.md` publica números sem comando, data ou arquivo

- **severidade:** baixa
- **categoria:** evidencia
- **onde:** `docs/medicoes.md:5-10`
- **criterio:** 9.1
- **o-que-observei:** a primeira tabela do arquivo (CPU, RAM, Ollama, Corpus) é a única sem coluna
  Evidência, e publica "7,9 GB. **Livre durante os testes: 0,22 a 0,68 GB**", "Ollama 0.34.0" e
  "8 artigos …, 135 páginas, 659 chunks (651 de página + 8 de resumo)" sem apontar de onde vieram.
  Os números do corpus estão corretos — conferi contra duas fontes independentes:
  `docs/evidencias/E7/log_01_preparar_corpus.txt` (`total: 135 páginas`, 8 linhas de artigo) e
  `docs/evidencias/E7/log_02_indexar.txt` (`659 chunks`, `{'pagina': 651, 'resumo': 8}`). O achado é
  de forma, não de valor. Contraria o que o registro do T10 afirma em `VERIFICACAO.md:290`:
  "Confirmado também que as ~30 outras linhas de dados do arquivo já citavam a coluna Evidência …
  nenhuma célula numérica ficou sem fonte."
- **como-reproduzir:**
  ```bash
  sed -n '5,12p' docs/medicoes.md
  grep -n "total:" docs/evidencias/E7/log_01_preparar_corpus.txt
  grep -n "por tipo" docs/evidencias/E7/log_02_indexar.txt
  ```
- **saida-obtida:**
  ```
  | Item | Valor |
  |---|---|
  | CPU | Intel Core i5-8250U, só GPU integrada (UHD 620) |
  | RAM | 7,9 GB. **Livre durante os testes: 0,22 a 0,68 GB** ... |
  | Ollama | 0.34.0, modelos em `D:\webinarioOllamaRAG\Ollama\models` |
  | Corpus | 8 artigos ..., 135 páginas, 659 chunks (651 de página + 8 de resumo), vetores de 1024 dimensões |
  ---
  log_01_preparar_corpus.txt: total: 135 páginas
  log_02_indexar.txt:5:   por tipo: {'pagina': 651, 'resumo': 8}
  ```
- **por-que-importa:** é a tabela que define o contexto de todas as outras — em particular o corpus,
  que é o que muda o significado dos números de indexação (A5-01, A5-02). Sem coluna de evidência,
  é a tabela mais fácil de ficar defasada sem que ninguém perceba, e a afirmação do T10 de que o
  arquivo inteiro tem fonte por célula não se sustenta.
- **confianca:** alta
- **relacionado:** A5-01, A5-08

---

## Não verificado

Itens do escopo A5 que **não** consegui fechar nesta rodada, com o motivo:

1. **Números de LLM e busca de `medicoes.md:22-26, 41-50, 69-78` (seções 9.1 LLM e 9.2).** Todas as
   evidências (`docs/evidencias/E9/medicao_*.json`) são de 14/09/2026 04:26–04:37, portanto do corpus
   de 556 chunks e com `qwen2.5:3b` como padrão. Os valores conferem com os arquivos citados, mas
   **não há nenhuma medição de `medir.py` posterior ao T12**, então não sei se ainda representam esta
   máquina. Refazer exige rodar `ferramentas/medir.py`, que usa o Ollama — proibido neste eixo
   (recurso único, em uso por outro eixo). Entrego como pergunta ao CTO: 9.1 e 9.2 deveriam ser
   remedidos depois da mudança de corpus e de modelo padrão?
2. **Conteúdo do `.docx` v1.1 além do que a evidência dump mostra.** Li
   `docs/evidencias/E10/plano_v11.txt` (gerado pelo próprio script) e o código de
   `gerar_plano_v11.py`, mas não abri o `.docx` binário diretamente nem o regerei — regerar
   sobrescreve `docs/*.docx` e a evidência, o que a salvaguarda de só leitura proíbe. Formatação,
   estilos e conteúdo de tabelas fora das duas que o dump imprime ficam sem conferência.
3. **`README.md` seguido do zero (critério 10.1).** Não executei o passo a passo numa cópia limpa:
   os passos 3, 6, 7 e 8 usam o Ollama e o passo 7 recria a coleção. A conferência foi estática
   (comandos existem, arquivos existem, links resolvem). macOS/Linux continuam sem máquina, como o
   próprio critério registra.
4. **`docs/roteiro_facilitador.md`.** Fora do meu escopo (eixo A3). Só o inspecionei para responder à
   pergunta sobre afirmações de citação de fontes (A5-19); não auditei seus números.
5. **Se `medicoes.md:35` (Shapley, 621 s) e `:62-63` (pip install, RAGAS) ainda valem.** As
   evidências citadas existem e contêm os números, mas são todas anteriores ao T12. Não classifiquei
   como achado porque nada no corpus novo afeta obviamente o Shapley pré-computado nem o tempo de
   `pip install`; registro como ponto de atenção, não como achado.
6. **Tempo de `E8/ui_navegador.txt` (`medicoes.md:54`).** O arquivo é de 14/09 e descreve o 3b; o
   número confere com a evidência. Não virou achado porque a célula declara o modelo explicitamente,
   mas o cenário (navegador real, streaming) nunca foi remedido com o modelo padrão atual.
