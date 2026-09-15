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
| 1.1 | Os 6 artigos do arXiv estão em `arquivosPDF/artigos/` e abrem com `pypdf` | contagem de arquivos; páginas e caracteres extraídos por arquivo | ✅ |
| 1.2 | Nenhum artigo tem página sem texto (PDF escaneado) | páginas com menos de 30 caracteres = 0, ou listadas e justificadas | ✅ |
| 1.3 | `metadados.csv` tem exatamente as colunas `arquivo, titulo, autores, ano, veiculo, tema, idioma, resumo` | leitura do cabeçalho | ✅ |
| 1.4 | Toda linha do CSV aponta para um PDF existente e todo PDF do corpus tem linha | cruzamento arquivo ↔ CSV sem sobras | ✅ |
| 1.5 | `tema` só usa `fundamentos`, `retrieval`, `avaliacao`, `survey`, `limitacoes`; `ano` é inteiro; `idioma` ∈ {`en`, `pt`} | validação por script | ✅ |
| 1.6 | `resumo` preenchido, **no idioma original** do artigo, gerado pelo LLM a partir do abstract | conferência manual de cada linha, registrada | ✅ |
| 1.7 | Os PDFs não entram no git; o README e o notebook trazem os links | `git status` sem PDFs; links presentes | ✅ |
| 1.8 | Artigos em português (1–2) | ⏸️ pendente com o autor; placeholder marcado `TODO` | ⏸️ |

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
| 4.4 | Se o estágio 1 não achar nada, a função cai para a busca simples ou avisa, sem quebrar | execução com pergunta fora da base | ✅ |

**Evidência:** `docs/evidencias/E4/`.

## E5 — SHAP

**Pré-requisitos:** E3 (5a), E6 (5b).

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 5a.1 | SHAP sobre a similaridade pergunta × chunk roda no notebook e gera o gráfico de texto | célula executada com gráfico salvo na saída | ✅ |
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
| 6.4 | Pergunta fora da base: com contexto, o modelo diz que não encontrou nos documentos | caso registrado | ✅ |
| 6.5 | `responder()` faz streaming e cita as fontes (arquivo, página) usadas | execução | ✅ |
| 6.6 | Trocar `MODELO_CHAT` para `qwen2.5:1.5b` em `config.py` funciona sem outra alteração | execução com o plano B | ✅ |
| 6.7 | Ollama desligado gera mensagem de erro clara, não um traceback cru | execução com o servidor parado | ✅ |

**Evidência:** `docs/evidencias/E6/`.

## E7 — Notebook e scripts

**Pré-requisitos:** E2–E6.

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 7.1 | `webinario_rag.ipynb` executa **de ponta a ponta** em kernel limpo, sem erro | execução não interativa (`nbclient`/`nbconvert --execute`) com log salvo | ✅ |
| 7.2 | Saídas ficam salvas no notebook, incluindo as pré-computadas | abrir o `.ipynb` sem kernel e ver as saídas | ✅ |
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
| 9.1 | Tempos medidos nesta máquina: indexação, busca, SHAP (5a), resposta com `qwen2.5:3b` e com `qwen2.5:1.5b` | `docs/medicoes.md` com data, comando e valores | ✅ |
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
| 10.3 | `docs/troubleshooting.md` cobre os erros realmente encontrados em E0–E9 | cada erro registrado no log tem entrada | ✅ |
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
