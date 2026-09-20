# Estado atual do repositório

> **Atualização da migração (20 de setembro de 2026):** a arquitetura vigente é
> híbrida. Ollama fornece apenas `bge-m3` para embeddings; OpenAI, NVIDIA e
> Gemini fornecem geração remota via router. MIG-04 (`f8ec561`) e o fallback
> remoto de MIG-05 estão mergeados. O gate CTO ainda exige AppTests adicionais
> e validação real; MIG-06/MIG-07 aguardam liberação.
> Consulte `docs/evidencias/MIG-04/validacao.md`,
> `docs/evidencias/MIG-05/validacao.md` e o handoff atual.

**Data do levantamento:** 2026-09-16 (retrato estático, não atualizado a cada commit)

Este documento é o retrato do repositório **como ele estava na data do levantamento**, não como deveria estar. Ele existe para
dar contexto de partida a quem audita o material (ver [`auditoria/PROTOCOLO_AUDITORIA.md`](auditoria/PROTOCOLO_AUDITORIA.md))
sem precisar reconstruir todo o histórico e dezenas de linhas de registro de execuções.

Regra de leitura: tudo aqui é **afirmação a ser conferida**, não evidência. A fonte única de verdade sobre
os status de verificação continua sendo [`VERIFICACAO.md`](VERIFICACAO.md) + os arquivos em `docs/evidencias/`.

---

## 1. O que é o projeto

Material prático do **Webinário CIIA — Encontro 2, "Construindo um Assistente com RAG, Ollama e
Streamlit"**, conduzido por Roger Quinelato (suporte: João Victor Rikio Enomoto).
Turmas: **21/09/2026** (CIIA, ensaio) e **28/09/2026** (público aberto), online, mesmo material.

O formato é demonstração ao vivo; os participantes (intermediário/avançado) replicam depois pelo
notebook, pelos scripts e pelo vídeo de instalação. O critério de sucesso do código não é "roda na
máquina do autor": é **rodar sozinho, de ponta a ponta, na máquina de quem assiste**.

Restrição de hardware que condiciona quase todas as decisões: máquina de demo com **7,9 GB de RAM,
i5-8250U, sem GPU dedicada**, rodando o LLM em CPU e dividindo recursos com a transmissão ao vivo.

Cronograma da aula (~1h54): recap 10 · indexação 18 · retrieval top-k 15 · dois estágios 7 · SHAP 12 ·
com/sem contexto 12 · Ollama 12 · Streamlit 15 · RAGAS/reranking/encerramento 8 · folga 5.

## 2. Decisões de arquitetura vigentes

| Decisão | Estado | Onde está registrada |
|---|---|---|
| Sem framework (nada de LangChain/LlamaIndex); Python puro | vigente | `CLAUDE.md`, `README.md:10` |
| Sem Colab; tudo local em `.venv` dentro do projeto | vigente | `CLAUDE.md`, `README.md` passo 4 |
| Ollama para embeddings (`bge-m3`) e chat | vigente | `config.py:13-17` |
| Chat `qwen2.5:1.5b` por padrão, `qwen2.5:3b` como plano B | **invertido em 2026-09-15** (ticket #19) | `config.py:17-18` |
| Chunking por página, subdividindo páginas longas com sobreposição | vigente | `rag.dividir_texto`, `rag.gerar_chunks` |
| Busca: top-k → filtros `where` → dois estágios (resumos → chunks) | vigente | `rag.buscar`, `rag.buscar_dois_estagios` |
| SHAP como explicabilidade **do retrieval**, só no notebook | vigente | bloco 4 do notebook |
| Prompt separado em mensagem `system` + `user` | vigente, **não reverter sem reverificar E6** | `rag.montar_mensagens`, `docs/troubleshooting.md:61` |
| Dependências fixadas com `==`; `requirements.lock` = `pip freeze` | vigente | `requirements.txt`, `requirements.lock` |
| Avaliação estilo RAGAS implementada à mão, sem a lib `ragas`, nunca ao vivo | vigente | `opcional/avaliacao_estilo_ragas.py` |

## 3. Arquitetura do código

`rag.py` é a **única** implementação do pipeline. Notebook, `scripts/00`–`07` e `app.py` apenas
chamam funções dele; `ferramentas/verificar.py e7_duplicadas` é a checagem automatizada que impede
cópia de lógica para fora (procura `RESPOSTA_NAO_ENCONTRADA in`, `indices_citados(...) or list(range(...))`,
`import ollama`, `cliente_ollama()`, `.chat(`/`.embed(` diretos fora de `rag.py`).

```
PDFs → extrair_paginas → limpar_texto → dividir_texto → gerar_chunks (+ chunk de resumo por artigo)
     → gerar_embeddings (Ollama bge-m3) → indexar (ChromaDB, coleção recriada do zero)

pergunta → gerar_embeddings → buscar (top-k, where, tipo_chunk=pagina)
                            └→ buscar_dois_estagios (estágio 1 nos resumos, limiar de distância,
                               estágio 2 com where arquivo $in [...])
         → montar_mensagens (system + user) → responder (streaming)
         → fontes_da_resposta / eh_recusa → montar_bloco_fontes
```

### 3.1 Superfície pública de `rag.py` (485 linhas)

| Grupo | Funções |
|---|---|
| Infra Ollama | `cliente_ollama`, `verificar_ollama`, `OllamaIndisponivel`, `cli_seguro` (context manager de saída amigável para CLI) |
| Metadados | `carregar_metadados`, `salvar_metadados`, `validar_metadados`, `extrair_metadados_llm`, `comparar_metadados` |
| Ingestão | `limpar_texto`, `extrair_paginas`, `extrair_abstract`, `dividir_texto`, `gerar_chunks` |
| Índice | `gerar_embeddings`, `abrir_colecao`, `indexar` |
| Busca | `combinar_filtros`, `_consultar`, `buscar`, `buscar_dois_estagios`, `tabela_resultados` |
| Prompt/LLM | `INSTRUCOES_SISTEMA`, `montar_prompt`, `montar_prompt_sem_contexto`, `montar_mensagens`, `formatar_mensagens`, `chat`, `gerar_texto`, `responder`, `resumir_abstract` |
| Fontes/recusa | `indices_citados`, `eh_recusa`, `fontes_da_resposta`, `formatar_fontes`, `montar_bloco_fontes` |
| Explicabilidade | `similaridade_cosseno`, `explicar_similaridade` (SHAP), `shapley_chunks` |

Pontos de comportamento que a auditoria precisa conhecer:

- **Fallback do estágio 1** (`rag.py:250`): dispara por **limiar de distância**
  (`config.DISTANCIA_MAXIMA_ESTAGIO_1 = 0.60`), não por "não achou vizinho" — a busca vetorial sempre
  devolve vizinhos. Limiar calibrado empiricamente (T06/#6): 8 perguntas dentro da base (máx. 0,5435)
  × 5 fora (mín. 0,6784), sem sobreposição.
- **Fontes citadas** (`rag.py:358-366`): só entram os `[n]` que aparecem no texto gerado; se o modelo
  não citou nada, cai para o top-k inteiro; em recusa, lista vazia.
- **`eh_recusa`** (`rag.py:347`) normaliza espaços, remove citações e pontuação duplicada antes de
  comparar com `config.RESPOSTA_NAO_ENCONTRADA` — existe porque o modelo real colou `[1]` na recusa.
- **`responder()`** é um gerador com `stream=True`; o bloco de fontes é emitido ao final (`incluir_fontes`).
- **`indexar()`** recria a coleção do zero (idempotente, ~19–24 min em CPU). Nunca rodar durante medição.

### 3.2 Inventário de arquivos

| Caminho | Linhas | Papel |
|---|---:|---|
| `config.py` | 44 | Modelos, caminhos, chunk, k, limiar, vocabulários fechados, URLs do corpus |
| `rag.py` | 485 | Pipeline inteiro (única implementação) |
| `app.py` | 105 | Chat Streamlit: histórico, slider k, filtros, modo de busca, fontes com "✅ citado" |
| `scripts/00_checar_ambiente.py` | 69 | Checagem de ambiente (E0) |
| `scripts/01_preparar_corpus.py` | 65 | Download dos PDFs, validação do CSV, resumos via LLM |
| `scripts/02_indexar.py` | 60 | Chunking + embeddings + Chroma + demo de metadados por LLM |
| `scripts/03_buscar.py` | 36 | top-k, filtros `where`, cross-lingual |
| `scripts/04_dois_estagios.py` | 49 | Simples × dois estágios + os dois casos de fallback |
| `scripts/05_shap.py` | 43 | SHAP da similaridade pergunta × chunk |
| `scripts/06_com_sem_contexto.py` | 51 | Resposta com e sem contexto + fontes citadas |
| `scripts/07_ollama.py` | 31 | Resposta RAG completa em streaming |
| `opcional/calcular_shapley_chunks.py` | 38 | Shapley dos chunks (~10 min, pré-computado) |
| `opcional/avaliacao_estilo_ragas.py` | 88 | Métricas estilo Ragas com o Ollama como juiz |
| `ferramentas/verificar.py` | 499 | 15 checagens automatizadas por critério (ver 3.3) |
| `ferramentas/construir_notebook.py` | 404 | Gera `webinario_rag.ipynb` (40 células, blocos 1–8) |
| `ferramentas/executar_notebook.py` | 39 | Executa o notebook e salva saídas (`--offline` testa o fallback) |
| `ferramentas/testar_app.py` | 103 | AppTest do Streamlit (E8) |
| `ferramentas/capturar_app.py` | 66 | Sobe o app e tira captura via Playwright (msedge) |
| `ferramentas/capturar_evidencias_e8.py` | 165 | **não commitado** — cenários 8.2/8.4–8.8 de captura |
| `ferramentas/medir.py` | 80 | Medições de desempenho (E9) |
| `ferramentas/gerar_plano_v11.py` | 195 | Gera o plano de aula v1.1 `.docx` |
| `ferramentas/rodar_scripts.sh` | 17 | Roda `scripts/00`–`07` em sequência com log em `docs/evidencias/E7/` |

### 3.3 Checagens disponíveis em `ferramentas/verificar.py`

`e1_resumos`, `e2`, `e2_sobreposicao`, `e2_reabrir`, `e3`, `e4`, `e4_limiar`, `e6_ollama_desligado`,
`e6_ollama_desligado_scripts`, `e6_fontes`, `e7_duplicadas`, `e7_duplicadas_antes_v2`, `e7_estrutura`,
`e7_saidas`, `e9_numeros`.

Todas saem com código ≠ 0 quando falham (inclusive `e9_numeros`, que trata "nenhuma menção encontrada"
como falha, não como sucesso silencioso).

## 4. Dados e corpus

- **8 artigos** em `arquivosPDF/artigos/` (não versionados; links no `README.md:99-106` e no notebook):
  6 em inglês (Lewis 2020 RAG, Karpukhin 2020 DPR, Gao 2023 survey, Es 2023 RAGAS, Asai 2023 Self-RAG,
  Liu 2023 Lost in the Middle) + 2 em português da SBC (Rocha et al. 2025 SBBD; Medeiros & Oliveira 2025 SEMISH).
- `metadados.csv`: colunas `arquivo, titulo, autores, ano, veiculo, tema, idioma, resumo`.
  `tema` ∈ {`fundamentos`, `retrieval`, `avaliacao`, `survey`, `limitacoes`}; `idioma` ∈ {`en`, `pt`}.
  `resumo` gerado pelo LLM a partir do abstract, **no idioma original do artigo**.
- **Índice atual:** 659 vetores (651 de página + 8 de resumo), dimensão 1024. Antes do T12 eram 556/6.
- `arquivosPDF/Curso-*.pdf` são cursos do CIIA, **fora do corpus** — não apagar.
- `resultados/` é versionado (rede de segurança para as etapas lentas da aula).

## 5. Estado da verificação (E0–E10)

| Etapa | Status declarado | Pendências |
|---|---|---|
| E0 Ambiente | ✅ | — |
| E1 Corpus e metadados | ✅ (1.8 ⏸️) | — (1.8 fechada pelo T12) |
| E2 Indexação | ✅ | — |
| E3 Retrieval top-k e filtros | ✅ | — |
| E4 Dois estágios | ✅ | — (4.4 fechada por T06/T07) |
| E5 SHAP | ✅ | — |
| E6 Prompt e Ollama | ✅ | 6.7 contestado: `scripts/01` e `02` ainda sem `cli_seguro()` (issue #24) |
| E7 Notebook e scripts | ✅ | — |
| E8 Streamlit | ✅ | 8.2/8.4/8.5/8.7 contestados: evidência era só texto; capturas geradas mas **não commitadas** (issues #15, #25) |
| E9 Medições | ✅ (9.3 ⏸️) | 9.3 depende de decisão do autor no ensaio de 21/09 |
| E10 Documentação | ✅ (10.1 ⏸️ macOS/Linux) | 10.1 verificado só no Windows; macOS/Linux sem máquina (issue #17) |

O `Registro de execuções` do `VERIFICACAO.md` tem ~30 linhas datadas, uma por tarefa — é o histórico
canônico e deve ser a primeira leitura de qualquer auditor.

## 6. Tickets (GitHub, `Roger-Quinelato/webinarioOllamaRAG`)

**Fechados:** #1–#14, #16, #18, #23 (lote T01–T18 de correções da auditoria de 2026-09-14).

**Abertos:**

| # | Label | Assunto |
|---|---|---|
| 25 | `ready-for-agent` | T13: capturar screenshots reais do Streamlit (8.2, 8.4, 8.5, 8.7) |
| 24 | `ready-for-agent` | T12: proteger `scripts/01` e `scripts/02` contra Ollama indisponível (6.7) |
| 20 | `ready-for-agent` | T20: fechamento — bateria completa + documentos-mestre |
| 19 | `needs-info` | Perguntas-teste definitivas e modelo ao vivo (9.3) — decisão do autor |
| 17 | `needs-info` | README do zero em Linux (WSL) |
| 15 | `ready-for-agent` | T15: capturas reais 8.2/8.4/8.5/8.6/8.7/8.8 |

Fluxo obrigatório por ticket (`CLAUDE.md`): implementar → `/code-review` do diff → corrigir achados →
commitar citando o número → só então o próximo. Um ticket por commit. Issues com `needs-info` são
puladas até o autor responder e não travam as demais.

## 7. Estado do git

- Branch base do levantamento: `chore/agent-skills-setup`; `main` também existe no remoto.
- Duas worktrees em `.claude/worktrees/` (`abstract-wishing-sparkle`, `humble-painting-spindle`) com
  cópias antigas do repo — **não são a árvore de trabalho ativa**; auditar só a raiz.
- **Trabalho não commitado** (T15/#15 em andamento):
  - `M ferramentas/capturar_app.py` — parâmetro `env` para subir o app com `OLLAMA_HOST` inválido (8.8).
  - `?? ferramentas/capturar_evidencias_e8.py` — script dos cenários de captura.
  - `?? docs/evidencias/E8/capturas/` — 8 PNGs (8.2a/b/c, 8.4a/b, 8.5, 8.6, 8.7).
  - `D .tlc/harness/*` — remoção staged do harness TLC.
  - **Faltando nesse conjunto:** a captura `8.8_ollama_indisponivel.png` e o `capturas.txt` que o
    script escreve ao final — indício de que a execução não chegou ao fim.

## 8. Divergências já identificadas neste levantamento

Achados textuais, conferidos por leitura direta. Entram na auditoria como **hipóteses já localizadas**,
não como achados fechados — cada um ainda precisa de verificação e de decisão sobre severidade.

| Onde | O que diz | Por que destoa |
|---|---|---|
| `README.md:5` | "modelo de chat (`qwen2.5:3b`, com plano B `qwen2.5:1.5b`)" | Invertido desde o ticket #19; `config.py:17-18` tem 1.5b como padrão |
| `README.md:179-181` | "Se as respostas estiverem lentas, mude `MODELO_CHAT` … para `qwen2.5:1.5b`" | Já é o padrão; a instrução perdeu o sentido |
| `docs/medicoes.md:20` | "Chunking (556 chunks) \| 9,0 s" | Corpus passou a 659 chunks no T12; o tempo é de outro corpus |
| `docs/troubleshooting.md:47` | "gerar os 556 embeddings" | Idem |
| `docs/evidencias/E8/capturas/` | 8 PNGs presentes | Não commitados e sem a captura 8.8; `VERIFICACAO.md` 8.2–8.8 ainda não os cita como evidência |
| `scripts/01`, `scripts/02` | sem `with rag.cli_seguro():` | `scripts/03`–`07` e `opcional/*` têm; é exatamente o achado 6.7 (issue #24) |

Acrescentado pelo piloto de auditoria (#27, 2026-09-16), já com evidência:

| Onde | O que foi verificado | Consequência |
|---|---|---|
| `rag.py:365`, `config.py:17`, `resultados/com_sem_contexto.json` | Com `qwen2.5:1.5b` (padrão desde o #19), o modelo não emite nenhuma citação `[n]` nas respostas positivas salvas | O fallback dispara sempre e "fontes citadas" volta a ser o top-k inteiro; a separação dos tickets #1/#3/#4 não aparece na demonstração de 6.5 (achado A1-08, alta) |
| `.venv/Lib/site-packages/` | Diretórios de código de ~31 distribuições apagados, `dist-info` intactos; `pip list` dava tudo como instalado e `import chromadb` falhava | Nenhum script rodava. Reparado pelo `requirements.lock` e E0 reverificada (achado A1-00, crítica) |
| `rag.py:33-43` | `ollama.ResponseError` 500 cai na mensagem de servidor fora do ar | Instrução errada justamente no erro mais provável ao vivo, falta de memória (achado A1-09, média) |

## 9. Invariantes que a auditoria não deve propor violar

1. Nenhum ✅ em `VERIFICACAO.md` sem evidência salva em `docs/evidencias/EN/`.
2. Nenhum critério afrouxado, reescrito ou removido para conseguir passar.
3. `webinario_rag.ipynb` **não é editado à mão** — é gerado por `construir_notebook.py` e executado por
   `executar_notebook.py`; regenerar sem executar ao vivo apaga as saídas versionadas.
4. `rag.py` é a única implementação do pipeline; nada de lógica copiada para scripts/app/notebook.
5. PDFs do corpus, `.venv/`, `chroma_db/` e `Ollama/models/` não entram no git.
6. Todo número publicado vem de medição **nesta** máquina, com data e comando.
7. Não introduzir framework de RAG, nem Colab, nem dependência sem `==`.
8. Toda etapa lenta precisa de saída pré-computada em `resultados/`.

## 10. Comandos

```bash
.venv/Scripts/python scripts/00_checar_ambiente.py
.venv/Scripts/python scripts/02_indexar.py
.venv/Scripts/streamlit run app.py
bash ferramentas/rodar_scripts.sh
.venv/Scripts/python ferramentas/construir_notebook.py
.venv/Scripts/python ferramentas/executar_notebook.py
.venv/Scripts/python ferramentas/executar_notebook.py --offline
.venv/Scripts/python ferramentas/testar_app.py
.venv/Scripts/python ferramentas/verificar.py e4
.venv/Scripts/python ferramentas/medir.py nome_do_cenario
```

`scripts/02_indexar.py` leva ~19–24 min e recria a coleção; `executar_notebook.py` sem `--offline`
roda ao vivo. No Windows, use Git Bash ou PowerShell com `PYTHONIOENCODING=utf-8`.
