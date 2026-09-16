# Eixo A6 — Reprodutibilidade e ambiente — achados (RODADA-1)

**Escopo:** `requirements.txt`, `requirements-dev.txt`, `requirements.lock`, `.gitignore`,
`scripts/00_checar_ambiente.py`, `ferramentas/rodar_scripts.sh`, estado do git ·
**Data:** 2026-09-16 · **Branch:** `chore/agent-skills-setup` · **Modo:** só leitura

**HEAD:** a auditoria começou em `eec1ecc` e terminou em `631da36`. Os quatro commits desse intervalo
(`d85ea6a`, `7b840fd`, `77de74f`, `631da36`) são as entregas dos eixos A2–A5 e quatro linhas anexadas
ao fim do Registro de execuções de `docs/VERIFICACAO.md`: `git diff --stat eec1ecc..HEAD` não toca
nenhum arquivo do meu escopo, e as linhas citadas em `docs/VERIFICACAO.md` (90, 93, 96, 292, 296)
foram reconferidas em `631da36`.

**Pergunta central:** um participante partindo de zero chega ao app funcionando sem conhecimento
prévio nem arquivo que não está no repositório?

Comandos usados, todos sem efeito colateral sobre o índice, sobre as saídas versionadas ou sobre a
`.venv`: `git status`/`ls-files`/`check-ignore`/`show`/`grep`/`clone` (leitura), `pip check`,
`pip freeze`, `scripts/00_checar_ambiente.py` (leve, só consulta versão e lista de modelos do Ollama)
e a sonda [`A6-sonda.py`](A6-sonda.py), cuja saída literal está em [`A6-sonda.txt`](A6-sonda.txt).
**Nada foi instalado, desinstalado ou atualizado.** Nenhum `scripts/01`–`07`, nenhum `opcional/*`,
nenhuma reindexação, nenhuma execução do notebook.

A sonda nunca desinstala pacote para testar ausência: ela insere um *finder* em `sys.meta_path` num
subprocesso, que levanta `ImportError` para os nomes escolhidos. Cada simulação vem com um
**controle** (`import <pacote>` no mesmo subprocesso) provando que o bloqueio de fato pegou.

---

### A6-01 — `scripts/00_checar_ambiente.py` não checa 0.2 nem 0.5; o critério 0.8 não se sustenta

- **severidade:** crítica
- **categoria:** evidencia
- **onde:** `scripts/00_checar_ambiente.py:37` (lista de pacotes), `scripts/00_checar_ambiente.py:62-63`
  (`OLLAMA_MODELS` só é impresso), `docs/VERIFICACAO.md:96` (critério 0.8), `docs/VERIFICACAO.md:90`
  (0.2), `docs/VERIFICACAO.md:93` (0.5)
- **criterio:** 0.8 (e, por consequência, 0.2 e 0.5)
- **o-que-observei:** o critério 0.8 afirma que o script "cobre 0.1–0.6". O script tem exatamente 7
  chamadas a `checar()` — as únicas capazes de reprovar o ambiente — e nenhuma delas corresponde a
  0.2 nem a 0.5:
  - **0.2** (`OLLAMA_MODELS` aponta para a pasta certa): `scripts/00_checar_ambiente.py:62-63` calcula
    o valor e o imprime com `print(f"[INFO] OLLAMA_MODELS = ...")`. Não há `checar()`, não há
    comparação com caminho nenhum, e a variável indefinida imprime um texto que diz que está tudo bem
    (`'não definida (o Ollama usa a pasta padrão ~/.ollama/models)'`). O script sai 0 do mesmo jeito.
  - **0.5** (dependências com `==` e instaladas; `pip check` sem conflito): as palavras `pip`,
    `requirements` e `check` **não aparecem** no arquivo. O script nunca lê `requirements.txt`, nunca
    confere versão fixada e nunca roda `pip check`.

  Também vale registrar que **0.4** ("`.venv` criado no projeto") é checado só como
  `sys.prefix != sys.base_prefix` (`scripts/00_checar_ambiente.py:35`), sem conferir que o `.venv`
  está dentro do projeto.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A6-sonda.py   # bloco A6/scripts00
  grep -c "checar(" scripts/00_checar_ambiente.py                     # 2ª medição, independente do AST
  grep -n "pip\|requirements\|check" scripts/00_checar_ambiente.py
  ```
- **saida-obtida:**
  ```
  chamadas a checar() (as únicas que podem FALHAR o script): 7
    linha  34: 'Python 3.10+'
    linha  35: 'Rodando dentro de um ambiente virtual'
    linha  41: f-string: import {...}
    linha  50: 'Servidor Ollama respondendo'
    linha  56: 'Modelos baixados'
    linha  43: f-string: import {...}
    linha  59: 'Servidor Ollama respondendo'

  palavras-chave ausentes do script (critério 0.5 = pip check / versões fixadas):
    'pip' presente: False
    'requirements' presente: False
    'check' presente: False

  critério 0.2 (OLLAMA_MODELS aponta para D:\webinarioOllamaRAG\Ollama\models):
    linha 62-63 usa print('[INFO] ...'), não checar(): True
  ```
  Duas medições independentes concordam no número de `checar()`: a sonda (AST, 7) e o `grep -c` (7).
- **por-que-importa:** 0.8 existe justamente para dar ao participante **um** comando que responda "meu
  ambiente está bom?". O comando responde "Ambiente pronto." sem ter olhado para duas das seis coisas
  que o próprio documento diz que ele olha. O ✅ de 0.8 é, pela letra do critério, falso — e 0.5 é
  exatamente a área do incidente A1-00.
- **confianca:** alta
- **relacionado:** A6-02, A6-03, A1-00

### A6-02 — `scripts/00` aprova ("Ambiente pronto.", exit 0) um ambiente sem `matplotlib`, e o bloco de SHAP quebra depois

- **severidade:** alta
- **categoria:** risco-ao-vivo
- **onde:** `scripts/00_checar_ambiente.py:37`, `requirements.txt:9` (`matplotlib==3.11.2`),
  `scripts/05_shap.py:36` (`shap.plots.text(...)`), `ferramentas/construir_notebook.py:278`
  (mesma chamada, na célula do bloco 4 sob `SHAP_AO_VIVO`)
- **criterio:** 0.6, 0.8, 7.5
- **o-que-observei:** a lista de `scripts/00_checar_ambiente.py:37` tem 6 pacotes
  (`ollama, chromadb, streamlit, pypdf, shap, numpy`). Dos 10 de `requirements.txt`, três não estão
  lá: `pandas`, `matplotlib`, `ipykernel`. Simulei a ausência de cada um:
  - `pandas` e `httpx`: **cobertos por acidente**, porque `shap` importa `pandas` e `ollama`/`chromadb`
    importam `httpx`. O script reprova (com mensagem enganosa, atribuindo a falha ao `shap`).
  - `matplotlib`: o script imprime **"Ambiente pronto." e sai 0**. Mas `shap.plots.text` — chamada em
    `scripts/05_shap.py:36` e na célula SHAP do notebook — exige matplotlib e levanta `ImportError`.
    `rag.cli_seguro()` (`rag.py:49-54`) só captura `OllamaIndisponivel`, então o erro sai como
    traceback cru, **depois** dos ~40 s do cálculo do SHAP.
  - `ipykernel`: o script também imprime "Ambiente pronto." e sai 0, embora o kernel do notebook
    (README passo 4 e passo 8) dependa dele.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A6-sonda.py   # bloco A6/scripts00-sim
  ```
- **saida-obtida:**
  ```
  -- bloqueando ['matplotlib'] --
     Ambiente pronto.
     exit=0
     [controle] import matplotlib nesse mesmo subprocesso: ImportError: [sonda A6] matplotlib indisponível (exit=1)

  -- bloqueando ['ipykernel'] --
     Ambiente pronto.
     exit=0
     [controle] import ipykernel nesse mesmo subprocesso: ImportError: [sonda A6] ipykernel indisponível (exit=1)
  ```
  Segunda medição, com alvo diferente (`import shap; shap.plots.text` em vez de `scripts/00`), no mesmo
  subprocesso com matplotlib bloqueado:
  ```
  shap ok
  ImportError: matplotlib is not installed so plotting is not available! Run `pip install matplotlib` to fix this.
  exit= 1
  ```
- **por-que-importa:** é literalmente o caso "o `scripts/00` aprova um ambiente onde a bateria depois
  falha". O participante que instala com o pip interrompido no meio (cenário documentado em
  `docs/troubleshooting.md:28-30`, "passou de 50 minutos… se cancelar, rode de novo") pode ficar sem
  matplotlib, receber "Ambiente pronto." e só descobrir o problema no bloco de SHAP — 12 minutos do
  cronograma, no meio da aula, com traceback cru na tela.
- **confianca:** alta
- **relacionado:** A6-01

### A6-03 — Nada no repositório detecta o modo de falha do A1-00, e o troubleshooting não o cobre

- **severidade:** alta
- **categoria:** reprodutibilidade
- **onde:** `scripts/00_checar_ambiente.py:37-43`, `ferramentas/verificar.py` (nenhuma checagem de
  integridade), `docs/troubleshooting.md:26-42` (seção "Ambiente Python"),
  `docs/auditoria/PROTOCOLO_AUDITORIA.md:197-202` (único lugar onde o reparo está escrito)
- **criterio:** 0.5, 0.6, 10.3
- **o-que-observei:** o incidente A1-00 (`.venv` com os diretórios de código de ~31 distribuições
  apagados e os `dist-info` intactos) continua **indetectável e não documentado**:
  1. Nenhum dos dois arquivos de checagem contém `dist-info`, `RECORD`, `pip check`,
     `requirements.lock` ou `importlib.metadata`.
  2. `docs/troubleshooting.md` não menciona `dist-info`, nem `requirements.lock`, nem
     `force-reinstall`. A única entrada de instalação (`:28-30`) trata de lentidão, não de ambiente
     corrompido.
  3. O comando de reparo só existe dentro do protocolo de auditoria — um documento de processo que o
     facilitador não consulta em aula.

  Um detalhe que torna o achado mais grave: a API óbvia para escrever essa checagem **não funciona**.
  `importlib.metadata.Distribution.files` no Python 3.12 aplica `skip_missing_files()` e descarta em
  silêncio exatamente os arquivos que sumiram. Minha primeira versão da sonda usava essa API e reportou
  "venv íntegra" por construção, mesmo num `site-packages` sintético onde não havia nenhum código. Uma
  checagem precisa ler o `RECORD` como texto.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A6-sonda.py   # blocos A6/venv e A6/venv2
  ```
- **saida-obtida:**
  ```
  dist-info com RECORD lidos: 142
  nenhuma distribuição com arquivo de RECORD faltando — venv íntegra

  -- existe alguma checagem no repositório que detecte isso? --
    scripts/00_checar_ambiente.py: nenhum padrão de integridade encontrado
    ferramentas/verificar.py: nenhum padrão de integridade encontrado
    docs/troubleshooting.md menciona 'dist-info':  False
    docs/troubleshooting.md menciona 'requirements.lock':  False
    docs/troubleshooting.md menciona 'force-reinstall':  False

  -- prova de que o detector dispara: site-packages sintético só com dist-info --
    metadata.version('ollama') = 0.6.2  <- o pip/pip list o dá como instalado
    diretório 'ollama/' existe no disco? False  <- import falharia
    Distribution.files (API do 3.12): 0 arquivos de código -> detector via API dispara: False  (FALSO NEGATIVO)
    RECORD lido como texto: 5 arquivos de código, 5 ausentes -> detector via RECORD dispara: True
  ```
  O estado **atual** da `.venv` foi medido duas vezes, por caminhos diferentes, e os dois concordam:
  por `RECORD` (142 dist-info, 0 arquivos ausentes) e por nome de topo importável no disco
  (142 distribuições, 0 órfãs). `pip check` sai 0 e `pip freeze` é byte a byte igual a
  `requirements.lock` (141 linhas, `diff` vazio).
- **por-que-importa:** o A1-00 travou a auditoria inteira e o CTO já pediu no parecer exatamente estas
  duas coisas (detecção + linha no troubleshooting). Enquanto não existirem, a única defesa é alguém
  perceber sozinho que `pip list` está mentindo. Se acontecer às 19h do dia 21/09, o facilitador não
  tem onde ler o que fazer.
- **confianca:** alta
- **relacionado:** A1-00 (confirmado pelo CTO, ação atribuída a este eixo), A6-01

### A6-04 — O trabalho do #15 não está commitado, e o script depende de uma alteração também não commitada

- **severidade:** média
- **categoria:** reprodutibilidade
- **onde:** `ferramentas/capturar_evidencias_e8.py:16` e `:139` (arquivo não versionado),
  `ferramentas/capturar_app.py:14-18` (alteração não commitada), `HEAD:ferramentas/capturar_app.py:13`,
  `docs/evidencias/E8/capturas/` (8 PNGs não versionados),
  `docs/auditoria/PROTOCOLO_AUDITORIA.md:46`, `docs/auditoria/PROMPT_AUDITORIA.md:108`
- **criterio:** 8.2, 8.4, 8.5, 8.7, 10.5
- **decisao-documentada:** `ferramentas/capturar_app.py:14-16` traz
  `# why: 'env' existe para T15 (8.8 — OLLAMA_HOST inválido): precisa subir o app com uma variável de
  ambiente diferente da do processo atual, sem afetar outras capturas na mesma sessão.` O comentário
  justifica **por que o parâmetro existe**, e é uma boa justificativa. O que ele não cobre — e não tem
  como cobrir — é o estado de versionamento: o parâmetro está só na árvore de trabalho. Não contradigo
  a decisão; reporto que ela ainda não chegou ao repositório.
- **o-que-observei:** clonei o repositório num diretório temporário fora do projeto e conferi o que um
  participante (ou outro auditor) recebe. `ferramentas/capturar_evidencias_e8.py` e
  `docs/evidencias/E8/capturas/` **não existem** no clone. Pior: o script importa
  `subir_app` (`:16`) e o chama com `subir_app(env={"OLLAMA_HOST": "http://localhost:1"})` (`:139`), e
  a assinatura em `HEAD` é `def subir_app(porta=PORTA, timeout=90):` — sem `env`. Mesmo que alguém
  copiasse só o script para um clone, a cena 8.8 estouraria `TypeError`.

  Ao mesmo tempo, `docs/auditoria/PROTOCOLO_AUDITORIA.md:46` e `docs/auditoria/PROMPT_AUDITORIA.md:108`
  — os dois **versionados** — listam `capturar_evidencias_e8.py` no escopo do eixo A4. O escopo de um
  auditor aponta para um arquivo que não está no repositório.
- **como-reproduzir:**
  ```bash
  git status --short
  git show HEAD:ferramentas/capturar_app.py | grep -n "def subir_app"
  grep -n "subir_app" ferramentas/capturar_evidencias_e8.py
  git clone D:/webinarioOllamaRAG /tmp/clone-a6 && ls /tmp/clone-a6/ferramentas/
  ```
- **saida-obtida:**
  ```
   D .tlc/harness/config.json
   D .tlc/harness/lessons.md
   D .tlc/harness/rules/verificacao.md
   M ferramentas/capturar_app.py
  ?? docs/evidencias/E8/capturas/
  ?? ferramentas/capturar_evidencias_e8.py

  HEAD:ferramentas/capturar_app.py -> 13:def subir_app(porta=PORTA, timeout=90):
  ferramentas/capturar_evidencias_e8.py -> 139:    processo, url = subir_app(env={"OLLAMA_HOST": "http://localhost:1"})

  (no clone)
  ferramentas/capturar_evidencias_e8.py      ausente
  docs/evidencias/E8/capturas                ausente
  ```
  O `git status` acima é o do início da minha auditoria (`eec1ecc`). Ao reproduzir hoje, ele traz
  também os relatórios dos eixos A2–A6 e o parecer do CTO, ainda não commitados; as quatro linhas que
  importam para este achado (`M ferramentas/capturar_app.py`, `?? docs/evidencias/E8/capturas/`,
  `?? ferramentas/capturar_evidencias_e8.py` e as três remoções em `.tlc/harness/`) continuam iguais.
- **por-que-importa:** a evidência de 8.2/8.4/8.5/8.7 que o #15 produziu existe só nesta máquina. Se o
  disco falhar ou alguém rodar `git clean`, some — e some junto o script que a regeraria. É também o
  caso "documentação versionada assume trabalho não commitado": o eixo A4 desta mesma rodada foi
  instruído a auditar um arquivo que um clone não tem.
- **confianca:** alta
- **relacionado:** A4 (dono de `docs/evidencias/E8/**`), A6-08

### A6-05 — `rodar_scripts.sh` sobrescreve 8 arquivos de evidência versionados, antes de saber se o script passou

- **severidade:** média
- **categoria:** evidencia
- **onde:** `ferramentas/rodar_scripts.sh:8-10`, `README.md:156`, `CLAUDE.md` (tabela de comandos)
- **criterio:** 7.5
- **o-que-observei:** o laço percorre `scripts/0*.py` e redireciona a saída de cada um direto para
  `docs/evidencias/E7/log_$(basename ...).txt`. Os 8 arquivos de destino estão **todos versionados**. O
  redirecionamento acontece no momento da invocação, então o arquivo antigo é truncado antes de o
  script rodar: uma execução que falha logo no início substitui a evidência boa por um log vazio ou por
  um traceback, sem cópia de segurança e sem confirmação. O `rodar_scripts.sh` é o comando documentado
  no README e no CLAUDE.md, e a bateria inclui `02_indexar.py` (~20 min) — ou seja, quem o roda para
  "ver se está tudo bem" já está mexendo na evidência de E7.
- **como-reproduzir:**
  ```bash
  cat -n ferramentas/rodar_scripts.sh
  for s in scripts/0*.py; do n="docs/evidencias/E7/log_$(basename "$s" .py).txt"; \
    printf "%s -> %s | versionado: %s\n" "$s" "$n" \
    "$(git ls-files --error-unmatch "$n" >/dev/null 2>&1 && echo SIM || echo NAO)"; done
  ```
- **saida-obtida:**
  ```
  10	  "$python" -u "$script" > "docs/evidencias/E7/log_$(basename "$script" .py).txt" 2>&1

  scripts/00_checar_ambiente.py -> docs/evidencias/E7/log_00_checar_ambiente.txt | versionado: SIM
  scripts/01_preparar_corpus.py -> docs/evidencias/E7/log_01_preparar_corpus.txt | versionado: SIM
  scripts/02_indexar.py         -> docs/evidencias/E7/log_02_indexar.txt         | versionado: SIM
  scripts/03_buscar.py          -> docs/evidencias/E7/log_03_buscar.txt          | versionado: SIM
  scripts/04_dois_estagios.py   -> docs/evidencias/E7/log_04_dois_estagios.txt   | versionado: SIM
  scripts/05_shap.py            -> docs/evidencias/E7/log_05_shap.txt            | versionado: SIM
  scripts/06_com_sem_contexto.py-> docs/evidencias/E7/log_06_com_sem_contexto.txt| versionado: SIM
  scripts/07_ollama.py          -> docs/evidencias/E7/log_07_ollama.txt          | versionado: SIM
  ```
  Segunda medição, por caminho diferente (listagem do git em vez da expansão do glob):
  `git ls-files docs/evidencias/E7/` traz os mesmos 8 `log_*.txt`.
- **por-que-importa:** a fragilidade já cobrou o preço uma vez. O registro de execuções
  (`docs/VERIFICACAO.md:296`) diz que `log_02_indexar.txt` "foi reconstruído a partir de uma execução
  equivalente (a saída real foi sobrescrita por engano)". Enquanto o comando documentado gravar por
  cima da evidência versionada, "rodar a bateria" e "preservar a prova" continuam sendo ações em
  conflito.
- **confianca:** alta

### A6-06 — O passo 4 do README manda clonar de uma URL que o repositório não fornece

- **severidade:** média
- **categoria:** documentacao
- **onde:** `README.md:63`
- **criterio:** 10.1
- **o-que-observei:** o primeiro comando do passo "Obter o código e criar o ambiente Python" é
  `git clone <url-do-repositorio> webinarioOllamaRAG`. O placeholder nunca é resolvido: `github.com`
  não aparece uma única vez no `README.md`. A URL real
  (`Roger-Quinelato/webinarioOllamaRAG`) existe em `CLAUDE.md` e em `docs/agents/issue-tracker.md`,
  que são documentos de manutenção, não o material do participante.
- **como-reproduzir:**
  ```bash
  grep -n "github.com\|url-do-repositorio" README.md
  ```
- **saida-obtida:**
  ```
  63:git clone <url-do-repositorio> webinarioOllamaRAG
  ```
  (nenhuma ocorrência de `github.com`)
- **por-que-importa:** é o primeiro passo em que o participante sai do vídeo de instalação e vai para o
  repositório sozinho. Ao vivo o link vai no chat e ninguém percebe; quem replicar depois, pelo README
  e pelo vídeo do YouTube, para no passo 4. O critério 10.1 pede o README "seguido do zero, sem
  conhecimento prévio" — a URL é exatamente conhecimento prévio.
- **confianca:** alta
- **relacionado:** A5 (dono do `README.md`)

### A6-07 — O caminho de instalação documentado não reproduz o ambiente testado

- **severidade:** média
- **categoria:** reprodutibilidade
- **onde:** `README.md:72-75`, `requirements.txt` (10 linhas), `requirements-dev.txt` (5 extras),
  `requirements.lock` (141 linhas)
- **criterio:** 0.5, 10.1
- **o-que-observei:** os três arquivos são **consistentes entre si** — nenhuma linha sem `==`, nenhum
  pacote de `requirements.txt`/`-dev.txt` ausente do lock, nenhuma versão divergente — e o lock bate
  exatamente com o que está instalado hoje (`diff` de `pip freeze` contra `requirements.lock`: vazio).
  O problema é outro: o README manda instalar `requirements.txt`, que fixa 10 pacotes. Os outros 126 do
  lock são dependências transitivas, resolvidas na hora pelo pip. O `requirements.lock` é citado no
  README apenas entre parênteses, como descrição ("lista o ambiente completo testado"), e nenhum
  comando do material o usa — enquanto o procedimento de reparo do A1-00 depende justamente dele.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A6-sonda.py   # bloco A6/imports
  .venv/Scripts/python -m pip freeze > /tmp/freeze.txt && diff <(sort /tmp/freeze.txt) <(sort requirements.lock)
  ```
- **saida-obtida:**
  ```
  requirements.txt=10  requirements-dev.txt(extras)=5  requirements.lock=141

  -- declarado em requirements.txt/-dev.txt e ausente ou divergente no lock --
    nenhum
  ```
  e o `diff` de `pip freeze` × `requirements.lock` sai vazio (141 linhas idênticas).
- **por-que-importa:** um participante que instalar em outubro recebe versões transitivas diferentes
  das testadas. É o tipo de deriva que produz "na minha máquina não funciona" sem nenhum sinal no
  `pip check`. O `CLAUDE.md` registra a decisão de ter `requirements.txt` fixado e o lock como
  `pip freeze` do ambiente testado, mas não diz qual dos dois o participante deve instalar — e o
  material só oferece um caminho, o menos determinístico.
- **confianca:** média
- **relacionado:** A6-03

### A6-08 — `.claude/worktrees/*` estão versionados como gitlinks sem `.gitmodules`

- **severidade:** baixa
- **categoria:** reprodutibilidade
- **onde:** índice do git: `.claude/worktrees/abstract-wishing-sparkle` e
  `.claude/worktrees/humble-painting-spindle` (modo `160000`); ausência de `.gitmodules` na raiz;
  `.gitignore` (não cobre `.claude/worktrees/`)
- **criterio:** 10.5
- **o-que-observei:** as duas worktrees que o `docs/ESTADO_ATUAL.md:178-179` declara "fora do escopo"
  não estão apenas presentes no disco: estão **commitadas**, como submódulos (`160000`), apontando para
  commits que não existem em lugar nenhum e sem entrada em `.gitmodules`. Um clone traz dois diretórios
  vazios, e `git submodule update --init` falha.
- **como-reproduzir:**
  ```bash
  git ls-files -s .claude
  git clone D:/webinarioOllamaRAG /tmp/clone-a6
  cd /tmp/clone-a6 && git submodule update --init
  ```
- **saida-obtida:**
  ```
  100644 7511b7e3a7598582803094b2f511a2495ffb183d 0	.claude/launch.json
  160000 39206c8c08444d97813fe24b0f828240a9a17ec6 0	.claude/worktrees/abstract-wishing-sparkle
  160000 f39927519520ff0a14213f3168e5029bac0dae2f 0	.claude/worktrees/humble-painting-spindle

  fatal: No url found for submodule path '.claude/worktrees/abstract-wishing-sparkle' in .gitmodules
  ```
- **por-que-importa:** o `git clone` em si funciona e o material roda — por isso é baixa. Mas é lixo de
  ferramenta commitado no repositório do webinário, e qualquer participante que rode um
  `git submodule update` reflexo recebe um `fatal:` no primeiro contato com o projeto.
- **confianca:** alta
- **relacionado:** A6-04

### A6-09 — O exemplo de Windows do passo 2 usa um caminho que só existe nesta máquina

- **severidade:** baixa
- **categoria:** documentacao
- **onde:** `README.md:47`
- **criterio:** 0.2, 10.1
- **o-que-observei:** o passo 2 ("Escolher onde os modelos ficam"), marcado como opcional, dá o exemplo
  de PowerShell já preenchido com `D:\webinarioOllamaRAG\Ollama\models` — o caminho da máquina do
  autor. O texto acima explica que é "para usar outra pasta", mas o bloco de código é copiável como
  está e cria uma variável de usuário apontando para um `D:` que a maioria das máquinas não tem. O
  `scripts/00_checar_ambiente.py` não reprova esse caso (ver A6-01): ele só imprime o valor.
- **como-reproduzir:**
  ```bash
  grep -n "SetEnvironmentVariable" README.md
  ```
- **saida-obtida:**
  ```
  47:  [Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "D:\webinarioOllamaRAG\Ollama\models", "User")
  ```
- **por-que-importa:** quem copiar o bloco vê o Ollama baixar 5 GB para um caminho que não queria, ou
  falhar por unidade inexistente — e `docs/troubleshooting.md:14-16` só cobre o caso de a variável não
  ter efeito, não o de ela estar apontando para o lugar errado.
- **confianca:** alta
- **relacionado:** A6-01, A5 (dono do `README.md`)

### A6-10 — A ferramenta de captura exige o Edge instalado, e isso não está documentado em lugar nenhum

- **severidade:** baixa
- **categoria:** reprodutibilidade
- **onde:** `ferramentas/capturar_app.py:45` (`p.chromium.launch(channel="msedge")`),
  `requirements-dev.txt:6` (`playwright==1.62.0`), `README.md:152-169` (seção "Para quem mantém o
  material")
- **criterio:** 8.2, 8.4, 8.5, 8.7
- **decisao-documentada:** `ferramentas/capturar_app.py:36-37` traz
  `# why: channel="msedge" usa o Edge já instalado na máquina de demo em vez de baixar o Chromium do
  Playwright (~150 MB) — a máquina tem pouco espaço/RAM (ver CLAUDE.md).` A decisão é boa e eu não a
  contesto: baixar 150 MB de Chromium numa máquina com 7,9 GB de RAM e pouco disco é pior. O que ela
  não cobre é a consequência para **outra** pessoa: trocar um download por um pré-requisito de máquina
  só funciona se o pré-requisito estiver escrito. Não está — `msedge` não aparece no `README.md`, e a
  seção "Para quem mantém o material" nem lista `capturar_app.py` entre os comandos.
- **o-que-observei:** `requirements-dev.txt` fixa o Playwright, mas nem o README nem o `CLAUDE.md`
  registram qualquer passo de instalação de navegador (`playwright install` ou equivalente), e a única
  menção a `msedge` fora do código está em `docs/ESTADO_ATUAL.md:110` e no registro de execuções
  (`docs/VERIFICACAO.md:292`) — descrições do que foi feito, não instruções.
- **como-reproduzir:**
  ```bash
  git grep -n "playwright install\|msedge\|channel=" -- README.md docs/ CLAUDE.md
  grep -n "capturar_app" README.md
  ```
- **saida-obtida:**
  ```
  docs/ESTADO_ATUAL.md:110:| `ferramentas/capturar_app.py` | 66 | Sobe o app e tira captura via Playwright (msedge) |
  docs/VERIFICACAO.md:292:| 2026-09-15 | Ticket #13 (T13): … usa Playwright (`channel="msedge"`, sem baixar Chromium) …
  ```
  (`grep -n "capturar_app" README.md` não devolve nada)
- **por-que-importa:** é caminho de mantenedor, não de participante — daí a severidade baixa. Mas o
  suporte da aula é o João Victor, em outra máquina: se as capturas de 8.2–8.8 precisarem ser
  regeradas por ele e o Edge não estiver no lugar esperado, a falha é um erro do Playwright sem
  nenhuma entrada no troubleshooting.
- **confianca:** alta
- **relacionado:** A6-04, A4

### A6-11 — O procedimento de reparo manda excluir pacotes que não estão no `requirements.lock`

- **severidade:** baixa
- **categoria:** documentacao
- **onde:** `docs/auditoria/PROTOCOLO_AUDITORIA.md:199-202`,
  `docs/auditoria/PROMPT_AUDITORIA.md:25-27`, `requirements.lock`,
  `docs/evidencias/E0/reverificacao_ambiente_2026-09-16.txt:3`
- **criterio:** 0.5
- **o-que-observei:** o reparo registrado é
  `pip install --force-reinstall --no-deps -r requirements.lock`, "excluindo `pip`, `setuptools` e
  `wheel` — incluí-los faz o pip travar no meio da própria reinstalação". Mas os três **não estão** no
  `requirements.lock` (o `pip freeze` já os omite). A ressalva não tem como ser executada: não há o que
  excluir, e quem tentar montar um arquivo filtrado vai procurar linhas que não existem.
- **como-reproduzir:**
  ```bash
  grep -n -i "^pip==\|^setuptools==\|^wheel==" requirements.lock; echo "exit=$?"
  ```
- **saida-obtida:**
  ```
  (nenhuma linha)
  exit=1
  ```
- **por-que-importa:** é o único procedimento escrito para o incidente mais grave já visto neste
  repositório (A1-00). Uma instrução com um passo impossível convida a pessoa sob pressão a achar que
  entendeu errado o comando inteiro. Note também que o log do reparo
  (`docs/evidencias/E0/reverificacao_ambiente_2026-09-16.txt:5-7`) registra
  `WARNING: Ignoring invalid distribution ~edi` — resíduo de instalação interrompida, hoje já ausente
  do `site-packages`.
- **confianca:** alta
- **relacionado:** A6-03, A1-00

---

## Verificado sem achado

Registro explícito do que passou, para o CTO não precisar refazer:

- **Critério 10.5 — nada proibido versionado.** `git ls-files` traz 132 arquivos; o filtro
  `\.pdf$|^\.venv/|^chroma_db/|^Ollama/|\.gguf$` não casa nenhum. `git check-ignore -v` confirma as
  regras ativas: `.gitignore:2` (`.venv/`), `:14` (`Ollama/models/`), `:15` (`chroma_db/`), `:18`
  (`arquivosPDF/**/*.pdf`, que cobre tanto `arquivosPDF/artigos/*.pdf` quanto os `Curso-*.pdf` na
  raiz da pasta).
- **Nenhum arquivo necessário está coberto pelo `.gitignore`.** `metadados.csv`, `resultados/` (10
  arquivos), `config.py`, `rag.py`, `app.py`, `webinario_rag.ipynb`, `scripts/`, `ferramentas/` e
  `docs/` estão todos versionados; o clone limpo os traz. Os PNGs de
  `docs/evidencias/E8/capturas/` aparecem como `??` (não ignorados) — a ausência deles no repositório é
  o A6-04, não uma regra de ignore.
- **Consistência dos três arquivos de dependências.** Nenhuma linha sem `==` em nenhum dos três;
  nenhum pacote declarado ausente do lock; nenhuma versão divergente; `pip check` limpo;
  `pip freeze` idêntico ao lock.
- **Nenhum pacote usado no código e ausente do `requirements`.** Os 15 imports de terceiros
  encontrados em todos os `.py` e nas células do notebook resolvem para distribuições declaradas. A
  única de fora é `IPython` (importada pela primeira célula do notebook), que entra como dependência
  do `ipykernel` e está fixada no lock (`ipython==9.17.1`) — declarada indiretamente, e não quebra.
- **Integridade atual da `.venv`.** Duas medições independentes: 142 dist-info com `RECORD` completo, 0
  arquivos ausentes; 142 distribuições com nome de topo presente no disco, 0 órfãs. Nenhum diretório
  `~*` residual em `site-packages`.
- **Critério 0.7 (kernel do Jupyter).** `jupyter kernelspec list` lista `webinario-rag` (em
  `%APPDATA%\jupyter\kernels`, como o `--user` do README produz) e `python3` do `.venv`.
- **Critério 0.3 (modelos).** `scripts/00_checar_ambiente.py:53-55` confere
  `MODELO_EMBEDDING`, `MODELO_CHAT` e `MODELO_CHAT_PLANO_B`, que cobrem os três modelos do critério; o
  README passo 3 manda baixar exatamente esses três.
- **`git clone` funciona.** O clone limpo sai com exit 0, na branch `chore/agent-skills-setup`, com
  `git status` limpo e sem `chroma_db/`, `arquivosPDF/artigos/` ou `.venv` (esperado: o participante
  os gera nos passos 6 e 7).

## Não verificado

- **Critério 7.5 (`scripts/00`–`07` em sequência, exit 0)** — `ferramentas/rodar_scripts.sh` executa
  `02_indexar.py`, que recria a coleção (~20 min) e é proibido pelo protocolo, e o próprio script
  sobrescreve as evidências versionadas (A6-05). `não-verificável-sem-efeito-colateral`. Para
  verificar seria preciso uma cópia do repositório e um `chroma_db/` separado, fora da máquina que
  está servindo as outras verificações.
- **Critério 10.1 em macOS e Linux** — sem máquina; é a pendência já registrada (issue #17). Não tenho
  como confirmar se `ferramentas/rodar_scripts.sh:6` (`.venv/bin/python`) e os passos do README
  funcionam fora do Windows.
- **Instalação do zero num `.venv` novo a partir do `requirements.txt`** — exigiria `pip install`, o
  que está proibido nesta rodada (invalidaria o ambiente dos outros eixos). O achado A6-07 é sobre a
  **forma** do caminho documentado, não sobre uma instalação que eu tenha executado. Confirmar a deriva
  transitiva na prática pede um `.venv` descartável fora do projeto.
- **`scripts/01_preparar_corpus.py` num corpus ausente** — depende de rede (arXiv e SBC) e do LLM para
  os resumos; `scripts/01`–`07` estão fora do que posso rodar. Não confirmei que as 8 URLs de
  `config.ARTIGOS_CORPUS:32-42` ainda respondem, nem que os PDFs baixados hoje são os mesmos que foram
  indexados.
- **Causa raiz do A1-00** — continua indeterminada. Não encontrei no repositório nenhum script,
  hook ou comando que apague `site-packages` seletivamente; a busca não é prova de ausência.
- **`arquivosPDF/Curso-*.pdf`** — `CLAUDE.md:44` e `docs/ESTADO_ATUAL.md:134` mandam não apagá-los,
  mas a pasta hoje só contém `arquivosPDF/artigos/` com os 8 PDFs do corpus. Não transformei isso em
  achado porque não consigo distinguir "foram apagados" de "nunca estiveram nesta máquina", e nenhum
  código do repositório os referencia — fica registrado para o eixo A5, dono dos dois documentos.
- **Comportamento do `rodar_scripts.sh` quando não existe `.venv`** — `ferramentas/rodar_scripts.sh:5-6`
  cai para `.venv/bin/python` sem checar se existe; não exercitei o caso, que exigiria mexer na `.venv`.
