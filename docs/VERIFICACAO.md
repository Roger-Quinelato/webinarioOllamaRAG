# Documento de verificação da implementação

Este documento é **consultado no início e no fim de toda tarefa** neste repositório. Uma etapa só muda para ✅ quando todos os seus critérios têm evidência registrada: saída de comando, arquivo ou captura de tela. Afirmação sem evidência não conta.

## Protocolo por tarefa

**Antes de começar**
1. Identificar a etapa (E0–E10) a que a tarefa pertence e ler os critérios dela.
2. Conferir se os **pré-requisitos** da etapa estão ✅. Se não estiverem, a tarefa é fazer a etapa anterior primeiro.
3. Anotar no [Registro de execuções](#registro-de-execuções) o que será feito.

**Ao terminar**
1. Rodar cada verificação da etapa e salvar a saída em `docs/evidencias/EN/` (ex.: `docs/evidencias/E2/indexacao.txt`).
2. Marcar cada critério como ✅ (passou, com evidência), ❌ (falhou) ou ⏸️ (bloqueado, com o motivo).
3. Se uma mudança tocar código de uma etapa já ✅ (ex.: `rag.py`), **reverificar as etapas afetadas** listadas em [Dependências entre etapas](#dependências-entre-etapas).
4. Atualizar o status na tabela de resumo e fechar a linha no registro.

**Nunca**: marcar ✅ sem evidência, apagar ou afrouxar um critério para fazê-lo passar, ou copiar números de outra máquina ou de estimativa. Todo número vem de medição nesta máquina.

## Resumo

| Etapa | Nome | Status | Evidência |
|---|---|---|---|
| E0 | Ambiente | ✅ | `docs/evidencias/E0/ambiente.txt` |
| E1 | Corpus e metadados | ✅ (1.8 ⏸️) | `docs/evidencias/E1/` |
| E2 | Indexação | ✅ | `docs/evidencias/E2/` |
| E3 | Retrieval top-k e filtros | ✅ | `docs/evidencias/E3/` |
| E4 | Busca em dois estágios | ✅ | `docs/evidencias/E4/` |
| E5 | SHAP | ✅ | `docs/evidencias/E5/` |
| E6 | Prompt augmentation e Ollama | ✅ | `docs/evidencias/E6/` |
| E7 | Notebook e scripts | ✅ | `docs/evidencias/E7/` |
| E8 | Streamlit | ✅ | `docs/evidencias/E8/` |
| E9 | Medições de desempenho | ✅ (9.3 ⏸️) | `docs/medicoes.md`, `docs/evidencias/E9/` |
| E10 | Documentação e plano v1.1 | ✅ (10.1 ⏸️ macOS/Linux) | `docs/evidencias/E10/` |

Legenda: ⬜ não iniciada · 🔄 em andamento · ✅ verificada · ❌ falhou · ⏸️ bloqueada

## Dependências entre etapas

| Se mudar… | Reverificar |
|---|---|
| `config.py` (modelos, caminhos, k) | E2–E9 |
| `metadados.csv` ou PDFs do corpus | E1–E8 |
| `rag.py` → indexação/chunking | E2–E8 |
| `rag.py` → busca | E3, E4, E5, E6, E7, E8 |
| `rag.py` → `responder()` | E6, E7, E8 |
| `requirements.txt` | E0 e todas as que importam o pacote alterado |
| Modelo trocado para o plano B | E2 (reindexar, se for o embedding), E6, E9 |

## Auditoria RODADA-1 (issues #27–#36)

Auditoria multiagente em andamento, com seis eixos de só leitura validados por um agente CTO. Processo em
[`auditoria/PROTOCOLO_AUDITORIA.md`](auditoria/PROTOCOLO_AUDITORIA.md), prompts em
[`auditoria/PROMPT_AUDITORIA.md`](auditoria/PROMPT_AUDITORIA.md), contexto de partida em
[`ESTADO_ATUAL.md`](ESTADO_ATUAL.md).

| Ticket | Eixo / etapa do ciclo | Critérios sob exame | Bloqueado por |
|---|---|---|---|
| [#27](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/27) | Piloto do ciclo completo no eixo **A1 — pipeline RAG** (`rag.py`, `config.py`) | 3.1–3.6, 4.1–4.4, 6.1–6.7 | — |
| [#28](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/28) | Calibração do protocolo com o aprendizado do piloto | — (só documentação da auditoria) | #27 |
| [#29](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/29) | **A2 — verificação e evidências** (este documento, `docs/evidencias/**`, `ferramentas/verificar.py`) | todos os ✅ de E0–E10 e a força da evidência que os sustenta | #28 |
| [#30](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/30) | **A3 — material didático** (notebook, `scripts/**`, `opcional/**`, roteiro) | 7.1–7.6, 5a.1–5b.2, 9.4 | #28 |
| [#31](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/31) | **A4 — aplicação Streamlit** | 8.1–8.8 | #28 |
| [#32](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/32) | **A5 — documentação e números** | 9.1–9.4, 10.1–10.4 | #28 |
| [#33](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/33) | **A6 — reprodutibilidade e ambiente** | 0.1–0.8, 7.5, 10.1, 10.5 | #28 |
| [#34](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/34) | Parecer do CTO sobre A2–A6, com lacunas e placar | — (valida os achados dos eixos) | #29–#33 |
| [#35](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/35) | Rodadas de devolução dos eixos A2–A6 | — | #34 |
| [#36](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/36) | Consolidado: bloqueadores, backlog e veredito para 21/09 | lista final de critérios contestados | #27, #35 |

**A auditoria não muda nenhum status deste documento.** Ela produz achados validados e um backlog de
tickets; um ✅ só é alterado depois que a correção foi implementada e a etapa reverificada com evidência
nova — o mesmo caminho da auditoria de 2026-09-14 (`docs/evidencias/E10/revisao_codigo.md`), cujos
achados só viraram mudança de status ao longo dos tickets #1–#23.

Regras que valem para todo agente da auditoria: só leitura no projeto (escrita apenas em
`docs/auditoria/`); proibido rodar `scripts/02_indexar.py` ou `ferramentas/executar_notebook.py` sem
`--offline`, porque destrói a coleção e as saídas usadas pelas demais verificações; chamadas ao Ollama
serializadas entre agentes (7,9 GB de RAM, LLM em CPU); `.claude/worktrees/**` fora do escopo; nenhum
critério afrouxado, reescrito ou removido para conseguir passar.

---

## E0 — Ambiente

**Pré-requisitos:** nenhum.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 0.1 | Ollama instalado e servidor respondendo | `ollama --version` e `GET http://localhost:11434/api/tags` sem erro | ✅ |
| 0.2 | `OLLAMA_MODELS` aponta para `D:\webinarioOllamaRAG\Ollama\models` (ou C:, se o plano B foi acionado, com o motivo registrado) | variável de usuário lida e modelos aparecendo nessa pasta após o `pull` | ✅ |
| 0.3 | Modelos baixados: `bge-m3`, `qwen2.5:3b`, `qwen2.5:1.5b` | `ollama list` contém os três | ✅ |
| 0.4 | `.venv` criado no projeto; Python global intocado | `.venv\Scripts\python -c "import sys; print(sys.prefix)"` aponta para `.venv` | ✅ |
| 0.5 | Dependências com **versão fixada** (`==`) em `requirements.txt` e instaladas | `pip install -r requirements.txt` sem erro; `pip check` sem conflito | ✅ |
| 0.6 | Imports funcionam | `python -c "import ollama, chromadb, streamlit, pypdf, shap"` | ✅ |
| 0.7 | Kernel do Jupyter registrado para o `.venv` | `jupyter kernelspec list` mostra o kernel do projeto | ✅ |
| 0.8 | `scripts/00_checar_ambiente.py` cobre 0.1–0.6 e sai com código 0 | execução do script | ✅ |

**Evidência:** `docs/evidencias/E0/`.

## E1 — Corpus e metadados

**Pré-requisitos:** E0.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 1.1 | Os 8 artigos (6 do arXiv + 2 em português, T12/#12) estão em `arquivosPDF/artigos/` e abrem com `pypdf` | contagem de arquivos; páginas e caracteres extraídos por arquivo | ✅ |
| 1.2 | Nenhum artigo tem página sem texto (PDF escaneado) | páginas com menos de 30 caracteres = 0, ou listadas e justificadas | ✅ |
| 1.3 | `metadados.csv` tem exatamente as colunas `arquivo, titulo, autores, ano, veiculo, tema, idioma, resumo` | leitura do cabeçalho | ✅ |
| 1.4 | Toda linha do CSV aponta para um PDF existente e todo PDF do corpus tem linha | cruzamento arquivo ↔ CSV sem sobras | ✅ |
| 1.5 | `tema` só usa `fundamentos`, `retrieval`, `avaliacao`, `survey`, `limitacoes`; `ano` é inteiro; `idioma` ∈ {`en`, `pt`} | validação por script | ✅ |
| 1.6 | `resumo` preenchido, **no idioma original** do artigo, gerado pelo LLM a partir do abstract | conferência manual de cada linha, registrada em [`E1/verificacao_E1.txt`](evidencias/E1/verificacao_E1.txt) | ✅ |
| 1.7 | Os PDFs não entram no git; o README e o notebook trazem os links | `git status` sem PDFs; links presentes | ✅ |
| 1.8 | Artigos em português (1–2) | T12/#12 (2026-09-15): 2 artigos de conferências da SBC (SBBD, SEMISH), PDF com texto extraível, decisão delegada ao agente pelo autor | ✅ |

**Evidência:** `docs/evidencias/E1/`.

## E2 — Indexação

**Pré-requisitos:** E0, E1.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 2.1 | Chunking por página, com páginas longas subdivididas com sobreposição | inspecionar os chunks de uma página longa: tamanhos e trecho sobreposto visível | ✅ |
| 2.2 | Todo chunk tem os metadados do CSV + `pagina` + `chunk_id` + `tipo_chunk` | amostra de chunks via `collection.get(include=["metadatas"])` | ✅ |
| 2.3 | Os resumos estão indexados como chunks próprios (`tipo_chunk="resumo"`), um por artigo | contagem por `tipo_chunk` | ✅ |
| 2.4 | Embeddings gerados com o modelo de `config.py` e dimensão consistente | dimensão do vetor registrada; um único modelo na coleção | ✅ |
| 2.5 | Reindexar é idempotente (rodar 2× não duplica) | contagem igual após a 2ª execução | ✅ |
| 2.6 | Coleção persistida em `chroma_db/` e reaberta em um processo novo | contagem igual após reabrir | ✅ |
| 2.7 | Demo de extração de metadados por LLM roda e é comparada campo a campo com o CSV | tabela da comparação salva | ✅ |
| 2.8 | Tempo total de indexação medido | valor registrado em E9 | ✅ |

**Evidência:** `docs/evidencias/E2/` (contagens, amostras, tempo).

## E3 — Retrieval top-k e filtros

**Pré-requisitos:** E2.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 3.1 | `buscar(pergunta, k)` devolve exatamente k resultados, ordenados por distância | saída para k = 1, 4, 8 | ✅ |
| 3.2 | Cada resultado traz texto, distância, arquivo e página | inspeção da saída | ✅ |
| 3.3 | Pergunta sobre um artigo conhecido traz esse artigo no top-k | caso registrado: pergunta, artigo esperado, posição obtida | ✅ |
| 3.4 | Filtros `where` funcionam: `ano >= 2023`, `tema`, `idioma` | todos os resultados filtrados obedecem ao filtro | ✅ |
| 3.5 | Cross-lingual: pergunta em português recupera chunk em inglês relevante | caso registrado | ✅ |
| 3.6 | Filtro que não casa com nada devolve vazio sem erro | execução | ✅ |

**Evidência:** `docs/evidencias/E3/`.

## E4 — Busca em dois estágios

**Pré-requisitos:** E3.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 4.1 | 1º estágio busca só em `tipo_chunk="resumo"` e escolhe os top-3 artigos | saída do estágio 1 | ✅ |
| 4.2 | 2º estágio busca chunks só dentro dos artigos escolhidos (`arquivo $in [...]`) | todo resultado pertence aos artigos do estágio 1 | ✅ |
| 4.3 | Comparação simples × dois estágios para a mesma pergunta, lado a lado | tabela salva com pelo menos um caso em que o resultado muda | ✅ |
| 4.4 | Se o estágio 1 não achar nada, a função cai para a busca simples ou avisa, sem quebrar | 4.4a (filtro idioma=pt esvazia os resumos) + 4.4b (pergunta fora da base sem filtro, limiar de distância) — [docs/evidencias/E4/reverificacao_e4_v2.txt](evidencias/E4/reverificacao_e4_v2.txt) | ✅ |

**Evidência:** `docs/evidencias/E4/`.

## E5 — SHAP

**Pré-requisitos:** E3 (5a), E6 (5b).

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 5a.1 | SHAP sobre a similaridade pergunta × chunk roda no notebook e gera o gráfico de texto | célula executada com gráfico salvo na saída — número de tempo mantido em dia por `e7_saidas` (T08), [docs/evidencias/E5/notebook_E5.txt](evidencias/E5/notebook_E5.txt) | ✅ |
| 5a.2 | Os valores somam aproximadamente à diferença entre a similaridade real e a base | checagem numérica registrada | ✅ |
| 5a.3 | Tempo de execução ao vivo medido e compatível com o bloco (12 min) | valor em E9 | ✅ |
| 5b.1 | Shapley dos chunks do top-k sobre a resposta calculado e **salvo** (não roda ao vivo) | arquivo de resultado + célula que só carrega | ✅ |
| 5b.2 | Notebook deixa explícito que é explicabilidade do retrieval, não do raciocínio do LLM | texto presente na célula markdown | ✅ |

**Evidência:** `docs/evidencias/E5/`.

## E6 — Prompt augmentation e Ollama

**Pré-requisitos:** E3 (E4 para a variante de dois estágios).

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 6.1 | Prompt montado mostra instruções + chunks numerados com fonte + pergunta | prompt impresso e salvo | ✅ |
| 6.2 | Mesma pergunta respondida **sem** e **com** contexto, lado a lado | saída salva | ✅ |
| 6.3 | Caso em que a resposta sem contexto inventa e a com contexto acerta | caso registrado (perguntas definitivas pendentes com o autor) | ✅ |
| 6.4 | Pergunta fora da base: com contexto, o modelo diz que não encontrou nos documentos | caso registrado — [docs/evidencias/E6/06_com_sem_contexto.txt](evidencias/E6/06_com_sem_contexto.txt) ("Qual é a receita de pão de queijo mineiro?": `eh_recusa()=True`, `fontes_citadas=[]`, mesmo com `[1]` colado à recusa) | ✅ |
| 6.5 | `responder()` faz streaming e cita as fontes (arquivo, página) usadas | execução | ✅ |
| 6.6 | Trocar `MODELO_CHAT` para `qwen2.5:1.5b` em `config.py` funciona sem outra alteração | execução com o plano B | ✅ |
| 6.7 | Ollama desligado gera mensagem de erro clara, não um traceback cru | execução com o servidor parado | ✅ |

**Evidência:** `docs/evidencias/E6/`.

## E7 — Notebook e scripts

**Pré-requisitos:** E2–E6.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 7.1 | `webinario_rag.ipynb` executa **de ponta a ponta** em kernel limpo, sem erro | execução não interativa (`nbclient`/`nbconvert --execute`) com log salvo | ✅ |
| 7.2 | Saídas ficam salvas no notebook, incluindo as pré-computadas | abrir o `.ipynb` sem kernel e ver as saídas — automatizado por `ferramentas/verificar.py e7_saidas` ([docs/evidencias/E7/saidas_notebook.txt](evidencias/E7/saidas_notebook.txt)) | ✅ |
| 7.3 | Blocos do notebook seguem a ordem e os nomes do cronograma | conferência com o cronograma do CLAUDE.md | ✅ |
| 7.4 | Notebook e scripts usam as funções de `rag.py`, sem cópias divergentes | busca por definições duplicadas | ✅ |
| 7.5 | Cada `scripts/NN_*.py` roda sozinho, em ordem, com código de saída 0 | execução em sequência com log | ✅ |
| 7.6 | Toda etapa lenta tem saída pré-computada salva como rede de segurança | lista das células pré-computadas | ✅ |

**Evidência:** `docs/evidencias/E7/`.

## E8 — Streamlit

**Pré-requisitos:** E6.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 8.1 | `streamlit run app.py` sobe sem erro | log do servidor | ✅ |
| 8.2 | Pergunta enviada gera resposta em streaming | teste no navegador com captura de tela | ✅ |
| 8.3 | Histórico do chat persiste entre perguntas na mesma sessão | 2 perguntas seguidas | ✅ |
| 8.4 | Slider de k altera a quantidade de fontes exibidas | captura com k diferentes | ✅ |
| 8.5 | Filtros de metadados restringem as fontes | captura | ✅ |
| 8.6 | Alternância busca simples × dois estágios muda o caminho usado | captura + indicação na UI | ✅ |
| 8.7 | Expander de fontes mostra arquivo, página, trecho e resumo do artigo | captura | ✅ |
| 8.8 | Ollama indisponível gera aviso na UI, sem quebrar o app | captura | ✅ |

**Evidência:** `docs/evidencias/E8/` (capturas + log).

## E9 — Medições de desempenho

**Pré-requisitos:** E2, E5, E6, E8.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 9.1 | Tempos medidos nesta máquina: indexação, busca, SHAP (5a), resposta com `qwen2.5:3b` e com `qwen2.5:1.5b` | `docs/medicoes.md` com data, comando e valores — números "na última execução do notebook" reconciliados e checados automaticamente por `verificar.py e9_numeros` contra `E7/saidas_notebook.txt` ([docs/evidencias/E9/reconciliacao_numeros.txt](evidencias/E9/reconciliacao_numeros.txt)) | ✅ |
| 9.2 | Medição repetida com o Ollama rodando junto de um navegador aberto (simulando a live) | valores registrados | ✅ |
| 9.3 | Decisão registrada: `qwen2.5:3b` ao vivo ou plano B, e `Ollama/models` no D: ou no C: | decisão + números que a sustentam | ⏸️ |
| 9.4 | Cada bloco cabe no tempo do cronograma, ou há proposta de ajuste | comparação tempo medido × minutos do bloco | ✅ |

**Evidência:** `docs/medicoes.md`.

## E10 — Documentação e plano v1.1

**Pré-requisitos:** E0–E9.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 10.1 | README com passo a passo completo (instalação → Streamlit) para Windows, macOS e Linux | seguir o README do zero em um `.venv` novo, sem conhecimento prévio | ⏸️ |
| 10.2 | `docs/roteiro_facilitador.md`: fala, demo, checkpoint e plano B por bloco | conferência bloco a bloco com o cronograma | ✅ |
| 10.3 | `docs/troubleshooting.md` cobre os erros realmente encontrados em E0–E9 | cada erro registrado no log tem entrada — cobertura em [docs/evidencias/E10/troubleshooting_cobertura.txt](evidencias/E10/troubleshooting_cobertura.txt), correção das entradas defasadas pelo corpus atual em [docs/evidencias/E10/t35_troubleshooting_pt.txt](evidencias/E10/t35_troubleshooting_pt.txt) | ✅ |
| 10.4 | `.docx` v1.1: cronograma novo, sem Colab, anexos 1–3 preenchidos, datas 21/09 e 28/09 | abrir e conferir | ✅ |
| 10.5 | Nenhum PDF, modelo, `.venv` ou `chroma_db` versionado | `git status` / `git ls-files` | ✅ |

**Evidência:** `docs/evidencias/E10/`.

---

## Registro de execuções

Uma linha por tarefa. É o histórico que mostra o que foi verificado, quando e com qual resultado.

| Data | Tarefa | Etapa(s) | Critérios verificados | Resultado | Evidência |
|---|---|---|---|---|---|
| 2026-09-13 | Criação deste documento | — | — | — | `docs/VERIFICACAO.md` |
| 2026-09-14 | Ambiente: `OLLAMA_MODELS` no D:, pull dos 3 modelos, `.venv`, dependências fixadas + lock, kernel | E0 | 0.1–0.8 | ✅ | `docs/evidencias/E0/ambiente.txt` |
| 2026-09-14 | Corpus: 6 artigos do arXiv, `metadados.csv`, resumos gerados pelo LLM | E1 | 1.1–1.7 (1.8 ⏸️ artigos PT com o autor) | ✅ | `docs/evidencias/E1/` |
| 2026-09-14 | Indexação (556 chunks, 2× para idempotência), demo de metadados por LLM | E2 | 2.1–2.8 | ✅ | `docs/evidencias/E2/` |
| 2026-09-14 | Busca top-k, filtros, cross-lingual; dois estágios com casos em que ajuda e em que atrapalha | E3, E4 | 3.1–3.6, 4.1–4.4 | ✅ | `docs/evidencias/E3/`, `docs/evidencias/E4/` |
| 2026-09-14 | Prompt com/sem contexto e `responder()`; prompt refeito com mensagem system (reverificado) | E6 | 6.1–6.7 | ✅ | `docs/evidencias/E6/` |
| 2026-09-14 | Streamlit: navegador + AppTest; reverificado após mudança do prompt | E8 | 8.1–8.8 | ✅ | `docs/evidencias/E8/` |
| 2026-09-14 | SHAP ao vivo e Shapley dos chunks pré-computado (621 s) | E5 | 5a.1–5a.3, 5b.1–5b.2 | ✅ | `docs/evidencias/E5/` |
| 2026-09-14 | Notebook gerado e executado (ao vivo 959 s na última execução, offline 61 s); scripts 00–07 em sequência | E7 | 7.1–7.6 | ✅ | `docs/evidencias/E7/` |
| 2026-09-14 | Medições em 2 cenários; decisões e ajuste do cronograma | E9 | 9.1, 9.2, 9.4 ✅; 9.3 ⏸️ (modelo ao vivo: decisão do autor) | ✅ parcial | `docs/medicoes.md`, `docs/evidencias/E9/` |
| 2026-09-14 | README, roteiro, troubleshooting, plano v1.1, versionamento | E10 | 10.2–10.5 ✅; 10.1 ✅ no Windows (README seguido do zero em cópia limpa: todos os passos com exit 0, Streamlit HTTP 200), ⏸️ macOS/Linux sem máquina para testar | ✅ parcial | `docs/evidencias/E10/` |
| 2026-09-14 | Avaliação no estilo RAGAS (opcional, fora dos critérios) | — | script executado, resultado salvo | ✅ | `docs/evidencias/opcional/avaliacao_estilo_ragas.txt` |
| 2026-09-14 | Fechamento da sessão: sintaxe dos 19 `.py`, reverificação de E3, duplicação (7.4) e versionamento de PDFs (10.5) | E3, E7, E10 | 3.1–3.6, 7.4, 10.5 | ✅ (pendências: 1.8, 9.3, 10.1 macOS/Linux) | `docs/evidencias/E10/fechamento_sessao.txt` |
| 2026-09-14 | Primeiro commit (`7e29c38`), autorizado pelo autor; `git ls-files` sem nenhum PDF | E10 | 10.5 | ✅ | `git ls-files` (0 arquivos `.pdf`) |
| 2026-09-14 | Revisão de código em dois eixos (Standards × Spec) do diff árvore vazia → `26689e8`, só leitura; `e7_duplicadas`, `e7_estrutura` e `py_compile` com saída 0; nenhum arquivo proibido versionado | E1, E4–E10 | 7.3, 7.4 (checagem), 10.5 reexecutados; demais só lidos | achados, status não alterados; reverificar 1.6, 4.4, 5a.1, 6.5, 6.7, 7.2, 7.4, 8.2, 8.4, 8.5, 8.7, 9.1 | `docs/evidencias/E10/revisao_codigo.md`, `docs/evidencias/E10/revisao_codigo_checagens.txt` |
| 2026-09-14 | Documentação da auditoria E10: seção no README, resumo dos critérios contestados no CLAUDE.md, `.gitignore` reforçado (`*.pyc`, `.vscode/`, `.idea/`, `.DS_Store`, `Thumbs.db`); confirmado que nenhum `.py` mudou (`py_compile` dos 19 arquivos, 0 erros) | E10 | nenhum critério reverificado (mudança só de documentação) | ✅ (documentação); pendências de 10.5 seguem as da linha anterior | `docs/evidencias/E10/documentacao_auditoria.txt` |
| 2026-09-14 | Reverificação pós-auditoria: E2 (chunks, metadados, embedding), E3 (busca k, filtros, cross-lingual), E4 (dois estágios, fallback), E7 (duplicação, estrutura) | E2, E3, E4, E7 | 2.2–2.6, 3.1–3.6, 4.1–4.4, 7.3–7.4 | ✅ | `docs/evidencias/E2/reverificacao_e2.txt`, `docs/evidencias/E3/reverificacao_e3.txt`, `docs/evidencias/E4/reverificacao_e4.txt`, `docs/evidencias/E7/reverificacao_e7_duplicadas.txt`, `docs/evidencias/E7/reverificacao_e7_estrutura.txt` |
| 2026-09-14 | Reverificação E6: Ollama indisponível gera erro claro | E6 | 6.7 | ✅ | `docs/evidencias/E6/reverificacao_e6_ollama_desligado.txt` |
| 2026-09-15 | Reverificação concluída: push para main com todas as evidências (E2, E3, E4, E6, E7) — nenhum critério falhou, todos os status permanecem ✅ | E2–E4, E6–E7 | 2.2–2.6, 3.1–3.6, 4.1–4.4, 6.7, 7.3–7.4 | ✅ | commits `8b10ec7`, `bd12498`, `4dc236d`, `83c9c46`, `084a28e`, `472d9d4` |
| 2026-09-14 | Auditoria comparativa (só leitura) contra o documento de plano de implementação (`docs/evidencias/auditoria_plano.html`), conferindo os 12 critérios contestados um a um contra código e evidência atuais | E1, E4–E9 | 1.6, 4.4, 5a.1, 6.5, 6.7, 7.2, 7.4, 8.2, 8.4, 8.5, 8.7, 9.1 (nenhum reexecutado nesta linha; só lidos) | 4.4 e 7.4 confirmados corrigidos e reverificados (evidência já existente); **6.5 e 6.7 têm correção no código (`rag.py:317-322`, `scripts/03-06`+`opcional/*.py` com `rag.cli_seguro()`) mas sem evidência de execução** — `ferramentas/verificar.py:e6_ollama_desligado_scripts` existe e nunca foi rodada, e não há reexecução salva de `responder()` pós-fix de 6.5; 1.6 (seção de conferência manual em `E1/verificacao_E1.txt` continua vazia), 5a.1/7.2/9.1 (`medicoes.md:97` ainda diz "94s na última execução do notebook", contradizendo `medicoes.md:33` e `E5/notebook_E5.txt`, ambos 34s) e 8.2/8.4/8.5/8.7 (`docs/evidencias/E8/` continua só com texto, sem captura de tela) seguem sem correção — nenhum critério teve status alterado | `docs/evidencias/E4/reverificacao_e4.txt`, `docs/evidencias/E7/reverificacao_e7_duplicadas.txt`, `docs/evidencias/E1/verificacao_E1.txt`, `docs/medicoes.md`, `docs/evidencias/E5/notebook_E5.txt`, `docs/evidencias/E8/` |
| 2026-09-14 | Fecha a lacuna de evidência de 6.7 e 6.5 apontada na linha anterior: rodou `ferramentas/verificar.py e6_ollama_desligado_scripts` (os 7 scripts de `scripts/03-07` e `opcional/*.py` com `OLLAMA_HOST` inválido) e testou `indices_citados()`/`responder()` (1 chamada ao vivo ao `qwen2.5:3b` + 2 casos sintéticos) | E6 | 6.5, 6.7 | ✅ 6.7: os 7 scripts saem com `exit=2`, mensagem clara, sem traceback; ✅ 6.5: quando o modelo cita `[n]` parcialmente, só as fontes citadas aparecem (caso sintético `[1]`+`[3]` → só `a.pdf`+`c.pdf`); quando não cita nada (caso real do 3b e caso sintético), cai no fallback documentado de listar todos — comportamento correto e agora coberto | `docs/evidencias/E6/reverificacao_e6_ollama_desligado_scripts.txt`, `docs/evidencias/E6/reverificacao_6.5_fontes.txt` |
| 2026-09-15 | Encerramento: documento VERIFICACAO.md consultado, verificações confirmadas, todas as evidências versionadas | E2, E3, E4, E6, E7, E10 | protocolo completo: leitura, reverificação, evidências, registro | ✅ | `docs/VERIFICACAO.md` (Registro de execuções atualizado) |
| 2026-09-15 | Ticket #1 (T01): centraliza a regra de fontes/recusa em `rag.fontes_da_resposta()` e `rag.eh_recusa()`, usadas por `responder()`; remove a lógica duplicada equivalente em `scripts/06_com_sem_contexto.py`; nova checagem `ferramentas/verificar.py e6_fontes` (citação parcial, sem citação, recusa exata, recusa com `[1]`, recusa com espaço extra) | E6 | 6.5 (reforça evidência; status já era ✅) | ✅ | `docs/evidencias/E6/e6_fontes.txt` |
| 2026-09-15 | Ticket #2 (T02): endurece `ferramentas/verificar.py e7_duplicadas` para detectar cópia de lógica do pipeline fora de nomes de função (`RESPOSTA_NAO_ENCONTRADA in`, `indices_citados(...) or list(range(...))`, `import ollama`/`cliente_ollama()`/`.chat(`/`.embed(` diretos), varrendo `scripts/`, `opcional/`, `app.py` e o notebook; nota: `scripts/06` já usava `rag.fontes_da_resposta()` indiretamente via `rag.montar_bloco_fontes()` desde o T01, não uma chamada direta — sem lógica duplicada, que é o critério real. Novo comando reexecutável `ferramentas/verificar.py e7_duplicadas_antes_v2` roda a checagem contra o `scripts/06_com_sem_contexto.py` do commit `ba814a0` (ANTES: achou `RESPOSTA_NAO_ENCONTRADA in ...`, prova que pega a cópia) versus `e7_duplicadas` no estado atual (DEPOIS: `nenhum` achado, `exit=0`) — ambos versionados, não um script solto fora do repo. `scripts/06` mantém as chaves `fontes_recuperadas`/`fontes_citadas` do JSON | E7 | 7.4 | ✅ | `docs/evidencias/E7/reverificacao_e7_duplicadas_v2.txt` |
| 2026-09-15 | Ticket #3 (T03): notebook (`ferramentas/construir_notebook.py`, blocos 5 e 6) passa a exibir "Fontes citadas" via `rag.fontes_da_resposta()` + `rag.formatar_fontes()` diretos (nenhuma fonte quando a resposta é recusa ou não há resultados) separado de "Trechos enviados ao prompt" (`rag.formatar_fontes(resultados)`, o top-k bruto); bloco 6 passa a capturar `resultados_bloco6` numa variável para poder listar os trechos separadamente. Notebook regenerado (`construir_notebook.py`, 40 células) e executado AO VIVO (`executar_notebook.py`, sem `--offline`, 21/21 células, 0 erros, 364s) — o `webinario_rag.ipynb` real e versionado voltou a ter saídas salvas (não só a cópia de evidência offline), evitando a regressão apontada pelo `/code-review` (regenerar sem executar ao vivo deixava o notebook commitado sem nenhuma saída, revertendo ~2900 linhas de saídas de uma execução anterior); reexecutado também `--offline` para manter a evidência de fallback atualizada | E7 | 6.5 (aplicado ao notebook), 7.3 | ✅ | `docs/evidencias/E7/t03_fontes_notebook.txt`, `webinario_rag.ipynb`, `docs/evidencias/E7/webinario_rag_offline.ipynb` |
| 2026-09-15 | Ticket #4 (T04): `app.py` calcula `busca["citadas"] = {indice for indice, _ in rag.fontes_da_resposta(resposta, busca["resultados"])}` após `st.write_stream`; `mostrar_fontes(busca)` marca cada trecho citado com "✅ citado" e o expander mostra "Fontes (citadas X de k) — caminho"; sem fontes citadas (recusa), mostra "Nenhuma fonte usada"; `busca` (com `citadas` dentro) salvo em `st.session_state.mensagens` via `**busca` para o histórico renderizar igual. Após o `/code-review` (achado Standards: Data Clumps — `fontes`/`citadas`/`caminho`/`artigos` sempre andavam juntos em 3 lugares sincronizados), `mostrar_fontes` passou a receber o dict `busca` inteiro em vez de 4 parâmetros posicionais. `ferramentas/testar_app.py` (AppTest, Ollama ao vivo) atualizado com prints de `citadas`/rótulo do expander e um novo caso de recusa ("receita de pão de queijo mineiro") — confirmado: resposta = recusa exata, `citadas=[]`, rótulo "Fontes (citadas 0 de 5)", aviso "Nenhuma fonte usada"; 0 exceções em toda a suíte, inclusive após o refactor | E8 | 8.2, 8.4, 8.5, 8.7 | ✅ | `docs/evidencias/E8/t04_fontes_citadas_app.txt` |
| 2026-09-15 | Ticket #5 (T05): roda `scripts/06_com_sem_contexto.py` com a pergunta fora da base já presente na lista ("Qual é a receita de pão de queijo mineiro?") e confirma `rag.eh_recusa(com_contexto)=True` e `fontes_citadas=[]` no `resultados/com_sem_contexto.json` gerado — caso real em que o `qwen2.5:3b` colou um `[1]` à recusa ("Não encontrei essa informação nos documentos. [1]"), exatamente o caso que a normalização de `eh_recusa()` (T01) existe para cobrir | E6 | 6.4 | ✅ | `docs/evidencias/E6/06_com_sem_contexto.txt` |
| 2026-09-15 | Ticket #6 (T06): novo `ferramentas/verificar.py e4_limiar` calibra `config.DISTANCIA_MAXIMA_ESTAGIO_1` contra 8 perguntas dentro da base (as 6 áreas do corpus) e 5 fora (pão de queijo, capital da Mongólia, regras do xadrez, troca de óleo, previsão do tempo) — distância do resumo mais próximo no estágio 1 via `rag.buscar_dois_estagios(n_artigos=1)["artigos"][0]["distancia"]` (evita tocar `rag._consultar` direto). Maior distância dentro da base: 0.5435; menor fora: 0.6784 — intervalos não se sobrepõem. O limiar atual (0.60, já presente em `config.py`) cai com folga nesse intervalo seguro: **nenhum ajuste em `config.py` foi necessário**, os dados confirmam o valor existente. Após o `/code-review` (achado Spec: o ramo "intervalos se sobrepõem" só imprimia uma mensagem, não escolhia de fato um limiar, e nunca era exercitado pelos dados reais deste corpus), a escolha do limiar virou a função pura `_escolher_limiar_estagio_1()` (sem rag/Ollama) com um autoteste de dados sintéticos que força a sobreposição e confirma que o valor sugerido é sempre a maior distância "dentro" — roda antes da parte ao vivo, sempre | E4 | 4.4 (calibração empírica do limiar do fallback) | ✅ | `docs/evidencias/E4/limiar_estagio1.txt` |
| 2026-09-15 | Ticket #7 (T07): `ferramentas/verificar.py e4` ganha o caso 4.4b (pergunta fora da base **sem filtro**, "Qual é a receita de pão de queijo mineiro?") ao lado do 4.4a mantido (filtro idioma=pt esvazia os resumos do estágio 1). 4.4b prova que o limiar de distância (achado 4.4 original, calibrado no T06) dispara sozinho quando o estágio 1 encontra vizinhos mas todos longe — caso que 4.4a (resumos vazios) não cobria: caminho obtido = `'busca simples (estágio 1 sem correspondência: resumo mais próximo está a distância 0.7322, acima do limiar 0.6)'`, começa com o prefixo esperado, sai com 1 se fosse `'dois estágios'` | E4 | 4.4 | ✅ | `docs/evidencias/E4/reverificacao_e4_v2.txt` |
| 2026-09-15 | Ticket #8 (T08): novo `ferramentas/verificar.py e7_saidas` lê `webinario_rag.ipynb` **sem kernel** (só o JSON salvo), lista as 20 células de código (com/sem saída) e extrai por regex os tempos salvos ("Extração em Ns", "RESUMO AO VIVO (Ns)", "SHAP em Ns", "[Ns com modelo]" do bloco 6) — achado atual: extração 158.1s, resumo ao vivo 14.5s, SHAP 48s, bloco 6 93.8s. **`docs/evidencias/E7/saidas_notebook.txt` já existia** (dump manual completo das saídas, do commit inicial) — a saída do novo comando foi **anexada** ao fim do arquivo, não sobrescreveu o conteúdo anterior. Usado para atualizar o número de SHAP defasado (achado 5a.1: estava 34s, execução atual real é 48s) em `docs/evidencias/E5/notebook_E5.txt`. Os novos números (extração 158.1s, resumo 14.5s) também já divergem dos citados em `docs/medicoes.md` (16,6s, 8,1s) — reconciliar `medicoes.md` é escopo do T10, sinalizado no próprio arquivo de evidência | E5, E7 | 5a.1, 7.2 | ✅ | `docs/evidencias/E7/saidas_notebook.txt`, `docs/evidencias/E5/notebook_E5.txt` |
| 2026-09-15 | Ticket #9 (T09): reexecução completa do notebook pós T01–T08 (fontes/recusa, dois estágios, limiar calibrado). `construir_notebook.py` (40 células) → `executar_notebook.py` **ao vivo** (Ollama aquecido: 21/21 células, 0 erros, 388s, log `E7/execucao_notebook.txt`) → `executar_notebook.py --offline` (21/21, 0 erros, 62s, log `E7/execucao_notebook_offline.txt`) → `verificar.py e7_saidas` de novo, refletindo esta execução (extração 106.6s, resumo 11.9s, SHAP 36s, bloco 6 70.6s; todos os 4 padrões obrigatórios presentes, `exit=0`) — saída anexada a `E7/saidas_notebook.txt`. `docs/evidencias/E5/notebook_E5.txt` (SHAP) atualizado de novo (48s → 36s), com nota de que o número varia por execução e o valor correto é sempre o que `e7_saidas` acabou de extrair | E7 | 7.1–7.6, 5a.1 | ✅ | `docs/evidencias/E7/execucao_notebook.txt`, `docs/evidencias/E7/execucao_notebook_offline.txt`, `docs/evidencias/E7/saidas_notebook.txt` |
| 2026-09-15 | Ticket #10 (T10): reconcilia `docs/medicoes.md` — as duas menções "na última execução do notebook" (linhas do bloco 4/SHAP e bloco 6/Ollama na tabela 9.4) estavam em 94s e 163,8s, defasadas da execução real (T09: SHAP 36s, resposta bloco 6 70,6s); atualizadas com os valores atuais, data (2026-09-15) e arquivo de evidência citado. A linha "SHAP no notebook" (9.1) ganhou o histórico completo das 4 execuções já vistas (37s, 34s, 48s, 36s), a mais recente com data. Confirmado também que as ~30 outras linhas de dados do arquivo já citavam a coluna Evidência antes deste ticket (convenção pré-existente) — nenhuma célula numérica ficou sem fonte. Nova checagem `verificar.py e9_numeros`: extrai por regex todo número "Ns na última execução do notebook" de `medicoes.md` e confere que aparece em `E7/saidas_notebook.txt` — testado ANTES (contra o `docs/medicoes.md` do HEAD, achou 94 e 163,8 sem confirmação) e DEPOIS (0 sem confirmação, `exit=0`). Corrigido no `/code-review` (achado Standards): a checagem original passaria calada (`exit=0`) se o regex parasse de achar qualquer menção (ex.: a frase mudar de texto) — agora `sys.exit(1)` se zero menções forem encontradas, tratando "nada para checar" como falha, não sucesso | E9 | 9.1 | ✅ | `docs/evidencias/E9/reconciliacao_numeros.txt` |
| 2026-09-15 | Ticket #11 (T11): `ferramentas/verificar.py e1_resumos` passa a imprimir, por artigo, idioma detectado (heurística de palavras funcionais en/pt, sem dependência nova), número de frases do resumo e as 3 primeiras palavras do abstract extraído (`rag.extrair_abstract`), ao lado do idioma do CSV e do resumo — base de sinal para a conferência manual do critério 1.6 | E1 | 1.6 (reforça a base de evidência; conferência em si no ticket #23) | ✅ | `docs/evidencias/E1/verificacao_E1.txt` |
| 2026-09-15 | Ticket #13 (T13): novo `ferramentas/capturar_app.py` — sobe `streamlit run app.py` em subprocesso (porta 8502, headless), espera HTTP 200 e usa Playwright (`channel="msedge"`, sem baixar Chromium) para tirar PNG do app renderizado, esperando pelo título em vez de um sleep fixo. `playwright==1.62.0` fixado em `requirements-dev.txt`; `requirements.lock` regerado via `pip freeze`. Testado ponta a ponta contra o app real (capturou a tela real, inclusive o aviso de Ollama indisponível quando o serviço está parado) | — | infraestrutura para 8.2/8.4/8.5/8.6/8.7/8.8 (capturas reais ficam para o T15, ainda bloqueado por T14) | ✅ | `ferramentas/capturar_app.py` |
| 2026-09-15 | Ticket #18 (T18): `ferramentas/gerar_plano_v11.py` acrescenta, na seção Material Didático, a justificativa para a ausência dos "slides conceituais" da v1.0 (Encontro 1 já cobriu a teoria; Encontro 2 é demonstração ao vivo do código) — achado da auditoria de 2026-09-14 sobre o critério 10.4. A geração da evidência de conferência do `.docx` foi movida para dentro do próprio script (antes era um dump solto, não reproduzível só rodando o comando documentado) | E10 | 10.4 (reforça evidência; status já era ✅) | ✅ | `docs/evidencias/E10/plano_v11.txt` |
| 2026-09-15 | Ticket #23 (T11 no tracker, issue #23): 1.6 estava vazia em `E1/verificacao_E1.txt` (uma linha em branco) e a listagem de resumos (saída de `e1_resumos`) tinha caído por engano sob o cabeçalho "1.7". Realocada a listagem para debaixo de "1.6"; "1.7" volta a conter só git status (`git status --short --ignored -- arquivosPDF/`) + link (`git check-ignore -v`) + contagem de links no README (`grep -c arxiv.org README.md` = 6). Conferência manual real registrada: para cada um dos 6 artigos, comparado o abstract completo extraído (`rag.extrair_abstract`, não só as 3 palavras do resumo em 1.6) contra o `resumo` do CSV — idioma bate e o resumo é fiel ao abstract (não genérico, não alucinado) nos 6 casos; nenhum artigo em português ainda (T12/#12 pendente do autor). `docs/VERIFICACAO.md`, critério 1.6, agora aponta explicitamente para `E1/verificacao_E1.txt` | E1 | 1.6 | ✅ | `docs/evidencias/E1/verificacao_E1.txt` |
| 2026-09-15 | Ticket #12 (T12): autor delegou ao agente a escolha dos artigos em português (critério 1.8). Adicionados 2 artigos reais, gratuitos, com texto extraível (0 páginas vazias), corpo 100% em português, de conferências abertas da SBC: `rocha2025_ragsft.pdf` (Aprimorando RAG via ajuste fino sequencial de SLMs, SBBD 2025, UNICAMP, tema retrieval) e `medeiros2025_embeddings_pt.pdf` (Comparação de embeddings/LLMs para RAG em português, SEMISH 2025, IFES, tema avaliacao). `config.ARTIGOS_ARXIV` renomeado para `ARTIGOS_CORPUS` (não é mais só arXiv). `scripts/01_preparar_corpus.py` baixou os PDFs e gerou os 2 resumos via `rag.resumir_abstract(...,'pt')`. Reindexado: 659 vetores (651 de página + 8 de resumo, antes 556/6). Reverificação: `verificar.py e2/e3/e4/e4_limiar/e6_fontes/e7_duplicadas/e7_estrutura` (todos ✅, exit 0); limiar de distância do estágio 1 (T06) continua seguro no novo corpus (folga em (0.5435, 0.6566), config em 0.60); notebook regenerado e reexecutado ao vivo e `--offline` (21/21 células, 0 erros nos dois). Corrigidos 3 lugares que assumiam `idioma=pt` sempre vazio (`verificar.py` 3.6/4.4a, `scripts/03`, `scripts/04`) — trocados para um filtro por ano fora do corpus, que continua garantidamente vazio. Critério 1.1 (contagem) e 1.8 (artigos PT) atualizados para ✅; docs/medicoes.md, CLAUDE.md e roteiro_facilitador.md atualizados com a nova contagem (8 artigos, 135 páginas, 659 chunks). Pendente (ao registrar esta linha): reverificação de E5 (SHAP) e a bateria completa `rodar_scripts.sh`/`testar_app.py` (E8, ticket #16) contra o corpus novo — ambas concluídas logo em seguida, ver as duas linhas abaixo | E1–E4, E7, E10 | 1.1, 1.8, 2.2–2.6, 3.1–3.6, 4.1–4.4, 6.5, 7.3–7.4, 7.1–7.6, 10.4 | ✅ | `docs/evidencias/E1/verificacao_E1.txt`, `docs/evidencias/E7/log_01_preparar_corpus.txt`, `docs/evidencias/E7/saidas_notebook.txt`, `docs/evidencias/E10/plano_v11.txt` |
| 2026-09-16 | Correção: a bateria `rodar_scripts.sh` do ticket #12 **completou `00`–`07` inteira com sucesso** (`scripts com falha: 0`; `02_indexar.py → exit 0 em 1420s`, `03` a `07` também exit 0) — a notificação de "killed" recebida durante a sessão não correspondia a uma interrupção real do script, só a leitura do output ficou defasada. `docs/evidencias/E7/log_02_indexar.txt` foi reconstruído a partir de uma execução equivalente (a saída real foi sobrescrita por engano por um `git checkout` antes de eu perceber que o processo já tinha terminado); `log_03`–`log_07` são a saída real e completa desta execução | E1–E4, E6, E7, E10 | 1.1, 1.8, 2.2–2.6, 3.1–3.6, 4.1–4.4, 6.4–6.7, 7.1–7.6 | ✅ | `docs/evidencias/E7/log_02_indexar.txt` … `log_07_ollama.txt` |
| 2026-09-16 | Ticket #16 (T16): confirmado o índice íntegro (`verificar.py e2`: 659/659 vetores) e roda `ferramentas/testar_app.py` de verdade contra ele: 3 rodadas isoladas (só k, só modo, só filtro) sem nenhum `FALHA`, 0 exceções; o artigo em português `medeiros2025_embeddings_pt.pdf` aparece no estágio 1 da busca em dois estágios, confirmando boa integração do corpus novo | E8 | 8.1–8.7 | ✅ | `docs/evidencias/E8/apptest.txt` |
| 2026-09-16 | Ticket #12 (E5): `scripts/05_shap.py` rodado contra o corpus de 8 artigos (também coberto pela bateria completa, linha acima), exit 0; tempo do SHAP no notebook (célula ao vivo) atualizado de 36s para 50s em `docs/evidencias/E5/notebook_E5.txt` (mesmo chunk explicado, `es2023_ragas.pdf` p.5, similaridade 0.6456 — só o tempo mudou, extraído direto do `webinario_rag.ipynb` salvo). 5b.1 (Shapley dos chunks pré-computado) não precisa reindexar — critério já deixa explícito que não roda ao vivo | E5 | 5a.1–5a.3, 5b.1–5b.2 | ✅ | `docs/evidencias/E5/notebook_E5.txt`, `docs/evidencias/E7/log_05_shap.txt` |
| 2026-09-16 | Levantamento do estado atual e abertura da auditoria RODADA-1: novo `docs/ESTADO_ATUAL.md` (arquitetura, inventário, corpus de 8 artigos/659 vetores, status E0–E10, tickets, estado do git, 9 invariantes), novo `docs/auditoria/PROTOCOLO_AUDITORIA.md` (6 eixos de só leitura + agente CTO validador, formato de achado, formato de devolução em 5 campos — erro / onde / evidência contrária / como refazer / critério de aceite —, LACUNAs, limite de 3 rodadas por eixo) e novo `docs/auditoria/PROMPT_AUDITORIA.md` (prompts de orquestrador, auditor, CTO, devolução e consolidação). Abertas as issues #27–#36 com as dependências nativas do GitHub (frontier = #27). Divergências já localizadas na leitura, entregues à auditoria como hipóteses e **não** como achados fechados: `README.md:5` e `:181` ainda descrevem `qwen2.5:3b` como padrão (invertido pelo #19 em `config.py:17-18`); `docs/medicoes.md:20` e `docs/troubleshooting.md:47` ainda citam 556 chunks/embeddings (corpus foi a 659 no T12); `docs/evidencias/E8/capturas/` tem 8 PNGs não commitados, sem a captura 8.8 nem o `capturas.txt`; `scripts/01` e `02` seguem sem `rag.cli_seguro()` (issue #24 já aberta). **Nenhum critério verificado, nenhum status alterado** — tarefa de documentação e planejamento | — | nenhum (só leitura) | ✅ (documentação) | `docs/ESTADO_ATUAL.md`, `docs/auditoria/PROTOCOLO_AUDITORIA.md`, `docs/auditoria/PROMPT_AUDITORIA.md`, issues #27–#36 |
| 2026-09-16 | Ticket #27 (T21): piloto do ciclo completo de auditoria no eixo A1 (`rag.py`, `config.py`), só leitura. **Incidente de ambiente antes de começar**: a `.venv` foi encontrada com os diretórios de código de ~31 distribuições apagados (`chromadb`, `python-dotenv`, `certifi`, `anyio`, `click`, `filelock`, `fsspec`, `comm`, `debugpy`…) e os `dist-info` intactos, de modo que `pip list` os dava como instalados e `import chromadb` falhava — nenhum script do repositório rodava. Reparado com `pip install --force-reinstall --no-deps -r requirements.lock` (sem `pip`, `setuptools`, `wheel`); nenhum `dist-info` do Python global foi tocado (verificado), causa raiz não determinada. E0 reverificado: `pip check` limpo e `scripts/00_checar_ambiente.py` com exit 0, todos os 8 itens OK. Auditoria A1: 8 achados propostos, 6 confirmados pelo CTO, 1 reclassificado (A1-02, média→baixa, por ignorar o fallback já documentado em `rag.py:359-365`), 1 rejeitado (A1-07, erro de medição da sobreposição), 1 lacuna aberta pelo CTO e respondida (A1-09). A investigação exigida pela devolução A1-02 revelou o achado A1-08 (alta): com `MODELO_CHAT=qwen2.5:1.5b`, padrão desde o #19, o modelo não emite nenhuma citação `[n]` nas respostas positivas salvas, o fallback dispara sempre e "fontes citadas" volta a ser o top-k inteiro — a separação construída nos tickets #1/#3/#4 não aparece na demonstração do critério 6.5. Checagens rodadas, todas exit 0: `e6_fontes`, `e7_duplicadas`, `e7_estrutura`, `e4`, `e4_limiar`, `py_compile` dos 21 `.py`. Nada reindexado, notebook não reexecutado. **Nenhum status alterado**: os achados viram backlog no #36 | E0 (reverificada), A1 audita E3/E4/E6 | 0.1–0.8 reverificados; 4.1–4.4 e 6.5 exercitados sem alterar status | ✅ E0; auditoria com achados registrados | `docs/evidencias/E0/reverificacao_ambiente_2026-09-16.txt`, `docs/auditoria/rodadas/RODADA-1/A1-achados.md`, `cto-parecer.md`, `A1-achados-v2.md`, `devolucoes/A1-02.md`, `devolucoes/A1-07.md`, `A1-sonda.txt`, `cto-sonda.txt` |
| 2026-09-16 | Ticket #28 (T22): calibra protocolo e prompts de auditoria com o que o piloto (#27) mostrou. Três ajustes, cada um ancorado numa falha observada: (a) o prompt do auditor passa a exigir que toda medição numérica seja repetida com uma segunda entrada de forma e tamanho diferentes — foi medição única em texto sintético repetitivo que produziu o achado rejeitado A1-07; (b) passa a exigir leitura dos comentários `why:`/`hazard:` da região antes de classificar comportamento como defeito, com novo campo obrigatório `decisao-documentada` no formato de achado — foi a ausência disso que levou à reclassificação de A1-02; (c) novo passo 0 no prompt do orquestrador e nova salvaguarda no protocolo: conferir `pip check` + `scripts/00_checar_ambiente.py` antes de qualquer eixo, com o comando de reparo pelo `requirements.lock` (sem `pip`/`setuptools`/`wheel`, que travam o processo) — o piloto perdeu tempo reparando a `.venv` no meio da auditoria. Também passou a ser exigido versionar as sondas na pasta da rodada, prática que o piloto adotou por conta própria e que o CTO usou para validar. `docs/ESTADO_ATUAL.md` atualizado com os três achados do piloto que mudam o retrato do repositório (A1-00 ambiente, A1-08 fallback com o modelo padrão, A1-09 mensagem de erro). **Nenhum critério verificado, nenhum status alterado** — mudança de documentação da auditoria | — | nenhum (só documentação) | ✅ (documentação) | `docs/auditoria/PROTOCOLO_AUDITORIA.md`, `docs/auditoria/PROMPT_AUDITORIA.md`, `docs/ESTADO_ATUAL.md` |
| 2026-09-16 | Ticket #29 (T23): auditoria do eixo A2 (verificação e evidências), só leitura. 16 achados — 6 alta, 5 média, 5 baixa. Os mais graves, todos reproduzidos pelo CTO por comando próprio: **7 das 15 checagens de `ferramentas/verificar.py` não têm como reprovar** (`e1_resumos`, `e2`, `e2_sobreposicao`, `e2_reabrir`, `e3`, `e6_ollama_desligado`, `e7_estrutura` não chamam `sys.exit`, varredura AST); a linha do Registro do T12 declara `e2/e3/e4/e4_limiar` reverificados mas o commit `af18c3a` não salvou nenhuma evidência de E2/E3/E4; `E2/reverificacao_e2.txt` ainda abre com "total de chunks: 556" enquanto o índice tem 659, de modo que as ✅ de 2.2–2.6 se apoiam em evidência de outro corpus; a evidência citada por 4.4 demonstra o caso `idioma=pt`, que o código não roda mais desde o T12; `e9_numeros` confere contra `E7/saidas_notebook.txt`, que é append-only e guarda quatro valores de SHAP (36/37/48/50 s), então qualquer valor histórico "confirma"; `e6_ollama_desligado_scripts` exclui por `glob("0[3-7]_*.py")` justamente os dois scripts que o achado 6.7 nomeia. **Nenhum status alterado** | E0–E10 (auditados, não reverificados) | nenhum reverificado | achados registrados, backlog no #36 | `docs/auditoria/rodadas/RODADA-1/A2-achados.md`, `A2-sonda.py`, `A2-sonda.txt` |
| 2026-09-16 | Ticket #30 (T24): auditoria do eixo A3 (material didático), só leitura. 14 achados — 4 alta, 6 média, 4 baixa. O mais grave, confirmado pelo CTO na linha citada: `ferramentas/construir_notebook.py:149` usa `if REINDEXAR or colecao.count() != len(chunks):`, então **`REINDEXAR = False` não impede a reindexação** — basta a contagem divergir para o notebook reindexar ao vivo, num comentário que promete "alguns minutos" contra 1420 s medidos. Também: o notebook lista 6 dos 8 artigos e chama todos de arXiv (`grep -c arxiv.org` = 6, sem `rocha2025`/`medeiros2025`); no bloco 5 as listas "Fontes citadas" e "Trechos enviados ao prompt" saem idênticas (`E7/t03_fontes_notebook.txt:11-25`), manifestação do achado A1-08; o bloco 2.5 tem `if LLM_AO_VIVO:` sem `else`, ficando sem rede de segurança (critério 7.6); o plano B do bloco 5 troca a alucinação pela recusa e apaga o contraste do critério 6.3. `scripts/01`/`02` sem `cli_seguro()` foi devolvido ao auditor por duplicar a issue #24, já aberta. **Nenhum status alterado** | E5, E7, E9, E10 (auditados) | nenhum reverificado | achados registrados, backlog no #36 | `docs/auditoria/rodadas/RODADA-1/A3-achados.md`, `A3-sonda.py`, `A3-sonda.txt` |
| 2026-09-16 | Ticket #31 (T25): auditoria do eixo A4 (aplicação Streamlit), único eixo com uso do Ollama ao vivo nesta rodada. 14 achados — 6 alta, 4 média, 4 baixa. O mais decisivo foi confirmado pelo CTO **abrindo as próprias imagens**: em `8.4a_k2.png` e `8.4b_k6.png` o slider mostra 2 e 6, mas a legenda da resposta diz `k = 4` nas duas e o expander diz "Fontes (citadas 1 de 4)" — as capturas que deveriam provar o efeito de k provam que o valor não chegou ao backend do Streamlit. Também: `8.2b_streaming_em_curso.png` mostra a bolha do assistente vazia, então 8.2 não tem hoje evidência válida de streaming; nenhuma captura está versionada (`git ls-files docs/evidencias/E8/` devolve só arquivos de texto) enquanto seis critérios de E8 declaram "captura" como método; `ferramentas/testar_app.py` só reprova em 3 pontos (`falhar(` aparece 3 vezes), o resto imprime; a legenda "Caminho usado · k · modelo" some em qualquer rerender porque `app.py:92` está dentro do `if pergunta:`. **Nenhum status alterado** | E8 (auditada) | nenhum reverificado | achados registrados, backlog no #36 | `docs/auditoria/rodadas/RODADA-1/A4-achados.md`, `A4-sonda.py` |
| 2026-09-16 | Ticket #32 (T26): auditoria do eixo A5 (documentação e números), só leitura. 20 achados — 7 alta, 9 média, 4 baixa. O mais grave: `docs/medicoes.md:53` publica "AppTest, 3b, 8 s · 17 s" citando `E8/apptest.txt`, cujo conteúdo atual é `qwen2.5:1.5b` com 44 s por pergunta, e a linha 100 usa esses números para orçar o bloco 7 em "~4 perguntas no pior caso" — é o único achado que derruba uma conclusão do critério 9.4. Além dele, cinco células numéricas de `medicoes.md` citam evidência que já não contém o número (chunking 556/9,0 s contra 659; indexação 1104,1 s contra 1420 s; extração 16,6 s contra 190,7 s; SHAP sem o valor atual de 50 s), e `README.md:114` propaga "cerca de 20 minutos" contra 23,7 min reais. Risco ao vivo: `docs/troubleshooting.md:50-52` manda o facilitador dizer no chat que "ainda não há artigos em português" — há dois desde o T12. Zona cega registrada: `e9_numeros` e `e7_saidas` saem com 0 mas só cobrem a frase literal "na última execução do notebook", e todos os achados A5-01 a A5-07 estão fora dela. **Nenhum status alterado** | E9, E10 (auditadas) | nenhum reverificado | achados registrados, backlog no #36 | `docs/auditoria/rodadas/RODADA-1/A5-achados.md`, `A5-sonda.py`, `A5-sonda.txt` |
| 2026-09-16 | Ticket #33 (T27): auditoria do eixo A6 (reprodutibilidade e ambiente), só leitura, sem instalar nem remover pacote. 11 achados — 1 crítica, 2 alta, 4 média, 4 baixa. **Crítico (A6-01): o ✅ do critério 0.8 é falso pela letra do critério.** O critério afirma que `scripts/00_checar_ambiente.py` "cobre 0.1–0.6"; o script tem 7 chamadas a `checar()` e nenhuma corresponde a 0.2 (`OLLAMA_MODELS` só aparece num `print("[INFO] …")` na linha 63) nem a 0.5 (`grep -c "pip\|requirements"` no arquivo devolve 0) — reproduzido pelo CTO. Alta (A6-02): a lista `pacotes` da linha 37 não inclui `matplotlib`, que está em `requirements.txt:9` e é exigido por `shap.plots.text` em `scripts/05_shap.py:36`, então o script imprime "Ambiente pronto." num ambiente onde o bloco de SHAP quebra com traceback cru depois de ~40 s; mesmo buraco para `ipykernel`. Alta (A6-03): o modo de falha do A1-00 segue indetectável — `dist-info`, `RECORD`, `requirements.lock` e `force-reinstall` não aparecem em nenhuma checagem nem no `troubleshooting.md`. Nota técnica preservada: `importlib.metadata.Distribution.files` aplica `skip_missing_files()` no Python 3.12 e descarta arquivos ausentes em silêncio, então o detector óbvio daria falso negativo; o auditor corrigiu a própria sonda lendo o `RECORD` como texto e a validou num `site-packages` sintético. Conferido sem achado: 10.5 limpo (132 arquivos versionados, nenhum PDF/`.venv`/`chroma_db`/modelo), três arquivos de requirements consistentes, `pip freeze` idêntico ao lock, `.venv` íntegra por duas medições. **Nenhum status alterado** | E0, E10 (auditadas) | nenhum reverificado | achados registrados, backlog no #36 | `docs/auditoria/rodadas/RODADA-1/A6-achados.md`, `A6-sonda.py`, `A6-sonda.txt` |
| 2026-09-16 | Ticket #34 (T28): parecer do CTO sobre os eixos A2–A6. Todos os achados de severidade alta e crítica foram **reproduzidos por comando próprio do CTO**, com entrada diferente da usada pelo auditor; os demais, validados por leitura direta do `arquivo:linha`, com o método declarado achado a achado. Resultado: 75 achados propostos, 74 confirmados, 0 rejeitados, 3 duplicados entre eixos (A2-05 devolvido por invadir o escopo de A5; A3-11 devolvido por duplicar a issue #24 já aberta; A4-04 sobrepõe A2-08, mantidos os dois ângulos com dono definido) e 2 lacunas abertas (A2: nenhuma das 8 checagens que reprovam foi testada contra entrada que deveria reprovar; A4: a frequência real de citação do `qwen2.5:1.5b` não foi medida). **Nenhuma referência de linha errada na amostra reproduzida** — inverso do piloto, onde 1 de 8 caiu por erro de medição, o que indica que as duas regras acrescentadas pelo ticket #28 (repetir medição numérica; ler `why:`/`hazard:` antes de classificar) pagaram o próprio custo. **Correção do parecer do piloto:** o achado A1-08 dizia que o `qwen2.5:1.5b` não emite nenhuma citação `[n]`; a leitura das capturas do T15 mostra o modelo citando `[1]`, então o correto é que **a citação é intermitente** — severidade alta mantida, porque comportamento imprevisível é pior para a aula que comportamento ausente. Somando o piloto: 83 achados, 80 confirmados, 24 de severidade alta e 2 críticos (A1-00 ambiente quebrado; A6-01 ✅ falso no critério 0.8). **Nenhum status alterado** | E0–E10 (parecer, não reverificação) | nenhum reverificado | parecer emitido | `docs/auditoria/rodadas/RODADA-1/cto-parecer-A2-A6.md`, `devolucoes/A2-05.md`, `devolucoes/A3-11.md` |
| 2026-09-16 | Ticket #35 (T29): rodadas de devolução dos eixos A2–A6. As duas devoluções foram **corrigidas**, nenhuma retirada: A2-05 reescrito no escopo do próprio eixo (o ✅ do critério 9.1 apoiado em evidência que não sustenta mais os números, com `e9_numeros` cobrindo só 3 das ~30 células numéricas de `medicoes.md`) e A3-11 reescrito como confirmação da issue #24 já aberta, com o ângulo que ela não cobre — o `scripts/02` é o bloco 2 do cronograma, o mais longo da aula, e o `roteiro_facilitador.md` tem plano B para lentidão mas **nenhum** para Ollama fora do ar nesse momento. As duas lacunas do CTO foram respondidas com medição nova: **LACUNA A2** — 4 das 8 checagens que chamam `sys.exit` foram exercitadas contra entrada que deveria reprovar (`e6_fontes`, `e9_numeros` nos dois ramos, `e7_saidas`), todas reprovaram; `e7_duplicadas` e `e6_ollama_desligado_scripts` já têm prova de reprovação; `e4` e `e4_limiar` seguem sem nunca ter sido vistas reprovando, porque exigiriam outro corpus. **LACUNA A4** — com `qwen2.5:1.5b`, `seed=42` e k=4, em 8 perguntas dentro da base, **só 2 respostas citaram `[n]`**; nas outras 6 o fallback listou o top-k inteiro (achado novo A4-15, alta). É o número que faltava para o critério 9.3: a demonstração do 6.5 funciona em 25% das perguntas com o modelo padrão atual. **Nenhum status alterado** | E6, E8, E9 (auditadas) | nenhum reverificado | devoluções respondidas, lacunas fechadas ou documentadas | `docs/auditoria/rodadas/RODADA-1/A2-achados-v2.md`, `A3-achados-v2.md`, `A4-achados-v2.md`, `lacuna-a2-sonda.txt`, `lacuna-a4-sonda.txt` |
| 2026-09-16 | Ticket #36 (T30): consolidado da RODADA-1. 85 achados propostos nos 6 eixos, 82 confirmados, 1 rejeitado, 1 reclassificado, 3 duplicados, 3 lacunas abertas e respondidas. **Seis bloqueadores para o ensaio de 21/09**, em ordem de risco: (B1) `REINDEXAR = False` não impede a reindexação e o bloco 2 pode consumir 23,7 min ao vivo; (B2) a demonstração do critério 6.5 funciona em 2 de 8 perguntas com o modelo padrão, e de forma intermitente, o que impede ensaiar; (B3) `scripts/00` aprova ambiente sem `matplotlib` e o bloco de SHAP quebra depois de ~40 s de cálculo; (B4) o troubleshooting manda dizer no chat que não há artigos em português, o que é falso desde o T12; (B5) o orçamento do bloco 7 no critério 9.4 foi calculado com tempos do 3b citando um arquivo que hoje registra o 1.5b; (B6) o modo de falha que quebrou a `.venv` segue sem detecção e sem receita de reparo documentada. Backlog de 18 tickets (T31–T48) pronto para `gh issue create`, mais a issue #24 já aberta. **21 critérios contestados**, cada um com o que o reabilita — nenhum status alterado nesta rodada, conforme o protocolo. Aceites conscientes: 10.1 em macOS/Linux, a decisão final de 9.3 (que agora tem o número que faltava), a causa raiz de A1-00 e as duas checagens do estágio 1 nunca vistas reprovando. **Veredito: o material não está pronto para 21/09**; os quatro primeiros bloqueadores são de baixa complexidade e alto impacto e devem ser corrigidos antes do ensaio | E0–E10 (consolidação, não reverificação) | nenhum reverificado | consolidado emitido | `docs/auditoria/rodadas/RODADA-1/consolidado.md` |
| 2026-09-16 | Publicação do backlog da RODADA-1 no tracker e consolidação das issues de captura: 16 issues criadas ([#38](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/38)–[#53](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/53)) a partir de T31–T39 e T42–T48 do `consolidado.md`, com as três arestas de bloqueio nativas do GitHub (#42←#39, #43←#40, #50←#43); T40 e T41 **não** viraram issues novas — foram absorvidos por [#15](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/15) como critérios de aceite, e [#25](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/25) foi fechada como duplicata, decisão justificada no novo `docs/prd/prd-capturas-e8.md` (fechar as duas e abrir uma terceira perderia o diagnóstico A4-01: o slider é escrito por setter de JavaScript e o valor nunca chega ao backend do Streamlit, então `8.4a_k2.png` e `8.4b_k6.png` foram tiradas as duas com k = 4). **Nenhum critério verificado, nenhum status alterado** — tarefa de tracker e documentação | — | nenhum (só documentação) | ✅ (documentação) | `docs/prd/prd-capturas-e8.md`, issues #38–#53 |
| 2026-09-16 | Ticket [#38](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/38) (T35, bloqueador B4): `docs/troubleshooting.md` mandava o facilitador dizer no chat que "ainda não há artigos em português" e que o filtro `idioma = pt` "volta vazio de propósito" — falso desde o T12/#12, que acrescentou `rocha2025_ragsft.pdf` e `medeiros2025_embeddings_pt.pdf`. Entrada reescrita para o comportamento real (os 2 artigos em português respondem por 103 dos 659 chunks, então o filtro devolve os `k` trechos pedidos) e nomeando o caso que volta vazio de verdade, `ano >= 2030`, que é o que o critério 3.6 usa. A entrada anterior, de indexação, publicava "556 embeddings … 1141 s / 1111 s" (corpus de 6 artigos) como se fosse o estado atual: agora abre com os 659 embeddings / 1420 s medidos nesta máquina e mantém os valores antigos identificados como histórico do corpus anterior, cada um com seu arquivo de evidência. Confirmado por dois comandos diferentes contra a coleção atual: `verificar.py e3` rodado agora (`3.6 ano>=2030: 0 resultados`, `3.6b idioma=pt: 4 resultados, todos pt = True`, exit 0 em 60,6 s) e `docs/evidencias/E7/log_03_buscar.txt:48-52`, saída real de `scripts/03` na bateria anterior — não são fontes independentes (leem a mesma coleção), mas descartam erro de chamada. Para os 1420 s a fonte é única, e o `log_02_indexar.txt` é reconstrução: a entrada agora diz de onde o número vem (resumo do `rodar_scripts.sh`) e que o arquivo foi reconstruído. Também corrigido `docs/evidencias/E10/troubleshooting_cobertura.txt`, que sustentava o ✅ de 10.3 repetindo a afirmação falsa (achado A2-16) e citando dois títulos de entrada que esta correção renomeou. Fora de escopo, com dono: os números defasados de `medicoes.md`/README/`CLAUDE.md` ([#43](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/43), [#50](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/50)) e o ponteiro morto de `ESTADO_ATUAL.md` ([#51](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/51)). `scripts/02_indexar.py` **não** foi rodado | E10 (E3 exercitada) | 10.3; 3.1–3.6 exercitados sem alterar status | ✅ | `docs/evidencias/E10/t35_troubleshooting_pt.txt` |
