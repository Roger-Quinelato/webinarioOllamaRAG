# Eixo A1 — Pipeline RAG — achados (RODADA-1)

**Escopo:** `rag.py`, `config.py` · **Data:** 2026-09-16 · **HEAD:** `4d6a16b` · **Modo:** só leitura

**Pergunta central:** o pipeline faz o que diz fazer, inclusive nos casos de borda?

Comandos usados nesta auditoria, todos sem efeito colateral sobre o índice ou sobre as saídas
versionadas: sonda de funções puras de `rag.py` (sem Ollama, sem ChromaDB),
`ferramentas/verificar.py e6_fontes`, `e7_duplicadas`, `e7_estrutura`, `e4`, `e4_limiar` e
`py_compile` dos 21 arquivos `.py`. Nenhuma reindexação, nenhuma reexecução do notebook.

A saída bruta da sonda está em [`A1-sonda.txt`](A1-sonda.txt).

---

### A1-00 — Ambiente encontrado quebrado: `.venv` sem os arquivos de 31 distribuições

- **severidade:** crítica
- **categoria:** reprodutibilidade
- **onde:** `.venv/Lib/site-packages/` (fora do controle de versão), `requirements.lock`
- **criterio:** 0.5, 0.6
- **o-que-observei:** no estado em que o repositório foi encontrado, `import chromadb` falhava.
  `pip list` mostrava os pacotes como instalados, mas os diretórios de código tinham sido apagados;
  os `dist-info` continuavam intactos, então o `pip` considerava tudo presente. Atingiu ao menos 31
  distribuições (`chromadb`, `python-dotenv`, `certifi`, `anyio`, `click`, `filelock`, `fsspec`,
  `comm`, `debugpy`, `colorama`, `attrs`, `aiohttp`, `altair`…). Nenhum script do repositório rodava.
- **como-reproduzir:** já não é reproduzível — o ambiente foi reparado para permitir a auditoria (ver
  "Ação tomada"). O estado original está registrado na evidência.
- **saida-obtida:**
  ```
  ModuleNotFoundError: No module named 'chromadb'
  httpcore 1.0.9 requires certifi, which is not installed.
  huggingface-hub 1.31.0 requires click, which is not installed.
  ipykernel 7.3.0 requires comm, which is not installed.
  ```
- **por-que-importa:** é o pior modo de falha possível para este material. `pip list` e
  `pip check` (parcialmente) mentem, então o participante que reinstalar seguindo o README pode ver um
  ambiente "completo" que não importa nada. Se acontecer na máquina de demo às 19h do dia 21/09, a aula
  não começa.
- **ação tomada:** `pip install --force-reinstall --no-deps -r requirements.lock` (sem `pip`,
  `setuptools` e `wheel`), seguido de `pip check` e `scripts/00_checar_ambiente.py`, ambos limpos.
  Evidência em [`docs/evidencias/E0/reverificacao_ambiente_2026-09-16.txt`](../../../evidencias/E0/reverificacao_ambiente_2026-09-16.txt).
  A causa raiz não foi determinada: nenhum `dist-info` do Python global foi tocado, então não houve
  instalação fora da `.venv`.
- **confianca:** alta
- **relacionado:** eixo A6 (reprodutibilidade) é o dono deste achado; registrado aqui porque bloqueava
  a auditoria de A1.

### A1-01 — Recusa no fim do texto não é reconhecida, e a resposta ganha fontes

- **severidade:** média
- **categoria:** correcao
- **onde:** `rag.py:347-355` (`eh_recusa`), `rag.py:358-366` (`fontes_da_resposta`)
- **criterio:** 6.4, 6.5
- **o-que-observei:** `eh_recusa` usa `startswith`. Quando o modelo escreve qualquer coisa antes da
  frase de recusa, a recusa não é detectada e `fontes_da_resposta` devolve o top-k inteiro pelo
  fallback de "não citou nada".
- **como-reproduzir:** sonda A1-01 (`rag.eh_recusa` e `rag.fontes_da_resposta` sobre
  `f"Os trechos falam de outra coisa. {config.RESPOSTA_NAO_ENCONTRADA}"`).
- **saida-obtida:**
  ```
  == A1-01 eh_recusa: recusa no FIM do texto ==
    eh_recusa=False fontes=[1, 2, 3]
    recusa+continuacao: eh_recusa=True fontes=[]
  ```
- **por-que-importa:** o critério 6.4 é demonstrado ao vivo com a pergunta fora da base. Se o modelo
  prefaciar a recusa, a tela mostra "Nenhuma fonte usada" virando "Fontes (citadas 3 de 4)" numa
  resposta que não respondeu nada — exatamente a confusão entre "contexto enviado" e "fonte usada" que
  o achado 6.5 existe para evitar.
- **confianca:** alta
- **relacionado:** A1-02

### A1-02 — Citação apenas a índices inexistentes cai no fallback e lista todos os trechos

- **severidade:** média
- **categoria:** correcao
- **onde:** `rag.py:337-344` (`indices_citados`), `rag.py:365`
- **criterio:** 6.5
- **o-que-observei:** `indices_citados` descarta índices fora de `1..n`. Quando o modelo cita **apenas**
  índices inválidos, a lista fica vazia e o `or list(range(...))` lista todos os trechos como fonte.
- **como-reproduzir:** sonda A1-02 (`"Segundo [7] e [9], nada."` com 3 resultados).
- **saida-obtida:**
  ```
  == A1-02 indices_citados: citacao fora do intervalo ==
    indices_citados=[] fontes=[1, 2, 3] (fallback lista todos)
  ```
- **por-que-importa:** citar `[7]` com k=4 é sinal de que o modelo alucinou a numeração; tratar isso
  como "não citou nada" e listar tudo dá ao espectador a impressão de que as quatro fontes sustentam a
  resposta.
- **confianca:** alta
- **relacionado:** A1-01

### A1-03 — A validação de `ano` do critério 1.5 é inalcançável pelo caminho documentado

- **severidade:** média
- **categoria:** correcao
- **onde:** `rag.py:71` (`carregar_metadados`), `rag.py:96` (`validar_metadados`)
- **criterio:** 1.5
- **o-que-observei:** `carregar_metadados` converte com `int(linha["ano"])` **antes** de qualquer
  validação. Um `ano` não numérico no CSV estoura `ValueError` cru ali, e a mensagem amigável de
  `validar_metadados` nunca roda. Depois da conversão, `str(linha["ano"]).isdigit()` só consegue falhar
  para inteiros negativos.
- **como-reproduzir:** sonda A1-03.
- **saida-obtida:**
  ```
  == A1-03 validar_metadados: campo ano ==
    ano int 2020 -> erros=['Linha sem PDF: x.pdf']
    ano -2020 -> erros=["x.pdf: ano '-2020' não é inteiro"]
  ```
- **por-que-importa:** `scripts/01_preparar_corpus.py` existe para validar o CSV com mensagem legível
  (é o bloco de corpus da aula). Um typo em `ano` entrega traceback em vez da mensagem, na frente da
  turma.
- **confianca:** alta

### A1-04 — `extrair_abstract` depende de texto não normalizado e falha em silêncio

- **severidade:** média
- **categoria:** correcao
- **onde:** `rag.py:116-125`
- **criterio:** 1.6
- **o-que-observei:** o lookahead do regex procura `\n` antes de "Introduction"/"Keywords". Se o texto
  já passou por `limpar_texto` (que colapsa todo espaço em branco), o lookahead nunca casa e a função
  devolve até 3000 caracteres, incluindo a introdução. Não há erro nem aviso. Hoje os chamadores usam
  `extrair_paginas(..., limpar=False)`, mas nada no código impede o outro uso.
- **como-reproduzir:** sonda A1-04.
- **saida-obtida:**
  ```
  == A1-04 extrair_abstract com texto ja normalizado ==
    com quebras de linha: 52 caracteres -> 'Este artigo apresenta um metodo novo de recuperacao.'
    ja passado por limpar_texto: 145 caracteres -> 'Este artigo apresenta um metodo novo de recuperacao. 1 Introduction O restante d'
  ```
- **por-que-importa:** o resumo do CSV é gerado a partir deste abstract. Um abstract contaminado com a
  introdução gera resumo pior, e o critério 1.6 é conferência manual — não pega o dia em que alguém
  passar texto limpo.
- **confianca:** alta

### A1-05 — Artigo com `resumo` vazio some do estágio 1 sem nenhum aviso

- **severidade:** média
- **categoria:** correcao
- **onde:** `rag.py:162` (`gerar_chunks`), `rag.py:246` (`buscar_dois_estagios`)
- **criterio:** 2.3, 4.1
- **o-que-observei:** o chunk `tipo_chunk="resumo"` só é criado quando `meta["resumo"]` é não vazio. Um
  artigo sem resumo é indexado normalmente em chunks de página, mas fica invisível ao estágio 1, que só
  consulta resumos. Nenhum aviso é emitido na indexação.
- **como-reproduzir:** leitura de `rag.py:162`; a sonda A1-05 registra a consequência.
- **por-que-importa:** a busca em dois estágios passaria a ignorar um artigo inteiro de forma silenciosa.
  Como os resumos são gerados por LLM em `scripts/01`, um abstract não encontrado (ver A1-04) já produz
  exatamente essa situação — o script imprime "preencha o resumo à mão" e segue.
- **confianca:** alta
- **relacionado:** A1-04

### A1-06 — A margem do limiar do estágio 1 encolheu quando o corpus cresceu, e nada vigia isso

- **severidade:** média
- **categoria:** risco-ao-vivo
- **onde:** `config.py:24` (`DISTANCIA_MAXIMA_ESTAGIO_1 = 0.60`), `rag.py:250`
- **criterio:** 4.4
- **o-que-observei:** o limiar foi calibrado no T06 com 6 artigos: menor distância fora da base 0,6784,
  folga de 0,0784 acima do limiar. Com os 8 artigos atuais, a menor distância fora da base é 0,6566 —
  folga de 0,0566. A checagem `e4_limiar` confirma que o limiar continua seguro, mas ela só reprova se
  os intervalos **se sobrepuserem**; não existe margem mínima exigida.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python ferramentas/verificar.py e4_limiar
  ```
- **saida-obtida:**
  ```
  T06 maior distância dentro da base: 0.5435
  T06 menor distância fora da base: 0.6566
  T06 intervalos não se sobrepõem — limiar seguro em qualquer ponto de (0.5435, 0.6566)
  T06 config.DISTANCIA_MAXIMA_ESTAGIO_1 atual: 0.6
  ```
- **por-que-importa:** a tendência é clara: cada artigo novo aproxima o "fora da base" do limiar. Sem um
  piso de margem, a próxima adição de corpus pode derrubar o fallback sem que nenhuma checagem reprove.
- **confianca:** alta

### A1-07 — Sobreposição real entre chunks fica abaixo do valor configurado

- **severidade:** baixa
- **categoria:** correcao
- **onde:** `rag.py:142-144` (`dividir_texto`), `config.py:21` (`SOBREPOSICAO = 150`)
- **criterio:** 2.1
- **o-que-observei:** ao recuar `sobreposicao` caracteres e avançar até o próximo espaço, a sobreposição
  efetiva fica em 142–149 caracteres em vez de 150.
- **como-reproduzir:** sonda A1-06.
- **saida-obtida:**
  ```
  5 partes, tamanhos=[989, 996, 989, 989, 901], sobreposicao real=[149, 142, 142, 142] (config.SOBREPOSICAO=150)
  ```
- **por-que-importa:** o valor de `config.py` é lido como garantia e é mostrado na aula como parâmetro
  do chunking.
- **confianca:** média

---

## Não verificado

- **`shapley_chunks` e `explicar_similaridade`**: exigem 2^k chamadas ao LLM e SHAP ao vivo. Rodar
  durante a auditoria competiria com as demais verificações pelo único Ollama da máquina. A saída
  pré-computada em `resultados/` não foi conferida contra uma reexecução.
- **`indexar()` e `gerar_chunks()` de ponta a ponta**: `indexar` recria a coleção (proibido pelo
  protocolo). Só as funções puras de chunking foram exercitadas.
- **Determinismo de `_opcoes` (`seed=42`, `temperature=0.1`)**: não foi testado se duas chamadas iguais
  produzem a mesma resposta nesta versão do Ollama.
- **Comportamento de `responder()` com o gerador abandonado no meio** (usuário fecha a aba durante o
  streaming): não exercitado.
- **Causa raiz de A1-00**: não determinada.
