# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Verificação obrigatória

**Toda tarefa começa e termina em [docs/VERIFICACAO.md](docs/VERIFICACAO.md).** Antes: identificar a etapa (E0–E10), ler os critérios e conferir os pré-requisitos. Depois: rodar as verificações, salvar a evidência em `docs/evidencias/EN/`, atualizar os status, reverificar as etapas dependentes e adicionar uma linha no registro de execuções. Nenhum critério vira ✅ sem evidência, e nenhum critério é afrouxado para passar.

## Fluxo de implementação por ticket

Tickets (GitHub Issues, ver [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md)) são implementados **um de cada vez**, nesta ordem fixa:

1. Implementar o ticket (com `/tdd` nos pontos que fizerem sentido).
2. Rodar `/code-review` sobre o diff do ticket.
3. Só commitar depois que a revisão não apontar nada pendente — achado real vira correção antes do commit, não é adiado.
4. Commitar (mensagem referenciando o número do ticket) e só então seguir para o próximo.

Não acumular vários tickets num commit, e não pular a revisão para "economizar tempo".

## Propósito

Material do webinário CIIA **Encontro 2 — "Construindo um Assistente com RAG, Ollama e Streamlit"**, conduzido por Roger Quinelato (suporte: João Victor Rikio Enomoto). Turmas: 21/09/2026 (CIIA, ensaio) e 28/09/2026 (público aberto), online, mesmo material. O Encontro 1 foi só teoria: todo o código prático nasce aqui.

Formato: demonstração ao vivo; participantes (nível intermediário/avançado) replicam depois pelo notebook, pelos scripts e pelo vídeo de instalação no YouTube do CIIA. O código precisa rodar sozinho, de ponta a ponta, na máquina de quem assiste.

## Estado atual

Implementado e verificado nas etapas E0–E9 (status em `docs/VERIFICACAO.md`). O git está na branch `main`. O `.gitignore` exclui `.venv/`, `Ollama/models/`, `chroma_db/` e todos os PDFs de `arquivosPDF/`.

Em 2026-09-14, `docs/evidencias/E10/revisao_codigo.md` registrou uma auditoria de código em dois eixos (Standards × Spec, dois sub-agentes de só leitura, achados conferidos no código; checagens estáticas em `docs/evidencias/E10/revisao_codigo_checagens.txt`, versão navegável em `docs/evidencias/auditoria_plano.html`). **Nenhum ✅ de `docs/VERIFICACAO.md` mudou** — a auditoria só lista achados e os critérios abaixo, contestados e pendentes de reverificação:

- **1.6** — seção de conferência manual dos resumos vazia em `E1/verificacao_E1.txt`.
- **4.4** — ~~o fallback do estágio 1 vazio (`rag.py:234-238`) nunca dispara com pergunta fora da base (a busca vetorial sempre devolve vizinhos); com filtro `where`, o fallback devolve vazio porque herda o mesmo `where`.~~ Resolvido: `rag.buscar_dois_estagios()` usa `config.DISTANCIA_MAXIMA_ESTAGIO_1` (limiar de distância do resumo mais próximo) para decidir o fallback, não mais "achou algum vizinho". Calibrado empiricamente no ticket [#6](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/6) (T06): 8 perguntas dentro da base (máx. distância 0.5435) × 5 fora (mín. 0.6784), sem sobreposição — o limiar 0.60 já em `config.py` cai com folga no intervalo seguro, nenhum ajuste necessário; evidência em `docs/evidencias/E4/limiar_estagio1.txt`. Coberto por teste automatizado no ticket [#7](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/7) (T07): `verificar.py e4` ganhou o caso 4.4b (pergunta fora da base sem filtro, dispara pelo limiar de distância) ao lado do 4.4a mantido (filtro que esvazia os resumos); evidência em `docs/evidencias/E4/reverificacao_e4_v2.txt`.
- **6.5** — ~~`responder()` (`rag.py:317-318`) lista os k trechos recuperados como fontes, não os efetivamente citados.~~ Resolvido no ticket [#1](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/1) (T01): `rag.fontes_da_resposta()`/`rag.eh_recusa()` centralizam a regra, usadas por `responder()` e por `scripts/06` via `rag.montar_bloco_fontes()`; evidência em `docs/evidencias/E6/e6_fontes.txt`. Estendido ao notebook no ticket [#3](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/3) (T03, blocos 5 e 6 de `ferramentas/construir_notebook.py`): "Fontes citadas" (via `rag.fontes_da_resposta()` + `rag.formatar_fontes()` diretos, sem depender do formato interno de `rag.montar_bloco_fontes()`) agora aparece separado de "Trechos enviados ao prompt" (o top-k bruto); notebook reexecutado ao vivo para manter `webinario_rag.ipynb` com saídas reais; evidência em `docs/evidencias/E7/t03_fontes_notebook.txt`. Estendido ao `app.py` no ticket [#4](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/4) (T04): `mostrar_fontes()` marca "✅ citado" nos trechos de `rag.fontes_da_resposta()` e mostra "Fontes (citadas X de k)"; recusa mostra "Nenhuma fonte usada"; confirmado com AppTest ao vivo, inclusive um caso real de recusa; evidência em `docs/evidencias/E8/t04_fontes_citadas_app.txt`.
- **6.7** — só `app.py` e `scripts/07_ollama.py` capturam `OllamaIndisponivel`; `scripts/03`–`06` e `opcional/*.py` não; a checagem `e6_ollama_desligado` só testa `rag.py`.
- **7.4** — ~~`ferramentas/verificar.py:e7_duplicadas` só compara nomes de função, não varre `ferramentas/`, ignora `opcional/` e nunca falha (só imprime).~~ Resolvido no ticket [#2](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/2) (T02): `e7_duplicadas` também varre `scripts/`, `opcional/`, `app.py` e o notebook por padrões de cópia de lógica do pipeline fora de nomes de função (`RESPOSTA_NAO_ENCONTRADA in`, `indices_citados(...) or list(range(...))`, `.chat(`/`.embed(`/`cliente_ollama()` diretos) e sai com `sys.exit(1)` em qualquer achado; evidência (antes/depois) em `docs/evidencias/E7/reverificacao_e7_duplicadas_v2.txt`.
- **8.2, 8.4, 8.5, 8.7** — sem captura de tela salva; evidência é texto de DOM/AppTest.
- **5a.1, 7.2, 9.1** — números de evidência (ex.: tempo do SHAP) defasados em relação ao notebook versionado.

Reverificar esses critérios com `ferramentas/verificar.py` antes de fechar E10, sem afrouxar os critérios para passar.
- `arquivosPDF/artigos/`: os 6 PDFs do corpus, baixados por `scripts/01_preparar_corpus.py`.
- `arquivosPDF/Curso-*.pdf`: cursos do CIIA. **Não fazem parte do corpus**; não apagar.
- `OLLAMA_MODELS` (variável de usuário) = `D:\webinarioOllamaRAG\Ollama\models`. Nessa pasta também há um `gemma4:26b` que não foi baixado pelo projeto; não apagar.
- O plano de aula v1.0 original está em `C:\Users\roger\Downloads\`. A v1.1 é gerada em `docs/` por `ferramentas/gerar_plano_v11.py`.

## Decisões de arquitetura (já acordadas com o autor)

- **Sem framework** (nada de LangChain/LlamaIndex): Python puro, para o mecanismo do RAG ficar visível. Dependências fixadas com `==` em `requirements.txt` (`requirements.lock` = `pip freeze` do ambiente testado; `requirements-dev.txt` = ferramentas). A avaliação é `opcional/avaliacao_estilo_ragas.py`: implementa as métricas do artigo do Ragas usando o próprio Ollama como juiz, sem a biblioteca `ragas`, e nunca roda ao vivo.
- **Sem Colab.** Tudo local, em `.venv` dentro do projeto; nunca instalar no Python global.
- **Ollama para embeddings e chat**: embedding `bge-m3` (plano B `nomic-embed-text`); chat `qwen2.5:3b` (plano B `qwen2.5:1.5b`), selecionável por variável de configuração. A máquina de demo tem 7,9 GB de RAM, i5-8250U e só GPU integrada: o LLM roda em CPU dividindo recursos com a transmissão. Por isso toda etapa lenta precisa de saída pré-computada salva no notebook.
- **Corpus**: ~6 artigos do arXiv em inglês (Lewis 2020 RAG, Karpukhin 2020 DPR, Gao 2023 survey, Es 2023 RAGAS, Asai 2023 Self-RAG, Liu 2023 Lost in the Middle) + 1–2 artigos em português escolhidos pelo autor (pendente). PDFs dos artigos **não são versionados**: o README e o notebook trazem os links.
- **Metadados**: `metadados.csv` escrito à mão, com as colunas `arquivo, titulo, autores, ano, veiculo, tema, idioma, resumo`. O `tema` usa vocabulário fechado (`fundamentos`, `retrieval`, `avaliacao`, `survey`, `limitacoes`). A `pagina` e o `chunk_id` são gerados na indexação. O notebook também demonstra a extração de metadados por LLM comparada com o CSV. O `resumo` é gerado pelo LLM a partir do abstract, **no idioma original do artigo**: 1 ao vivo, os demais pré-computados no CSV.
- **Chunking**: por página, subdividindo as páginas longas por tamanho fixo com sobreposição.
- **Busca**: top-k simples → filtros `where` do ChromaDB → **busca em dois estágios** (1º estágio nos resumos escolhe os artigos; 2º estágio busca os chunks com `where={"arquivo": {"$in": [...]}}`).
- **SHAP**: (a) quais palavras da pergunta explicam a similaridade com cada chunk, ao vivo; (b) Shapley dos chunks do top-k na resposta, pré-computado. É explicabilidade do retrieval, não do raciocínio do LLM. Fica só no notebook.
- **Streamlit** (`app.py`): chat com histórico, slider de k, filtros de metadados, alternância busca simples × dois estágios e fontes com resumo.

- **Prompt**: `rag.montar_mensagens()` separa as instruções numa mensagem `system` e manda os trechos + pergunta na `user`. Com tudo numa mensagem só, o `qwen2.5:3b` respondia em inglês ou recusava perguntas que os trechos respondiam (testado; ver `docs/troubleshooting.md`). Não voltar ao prompt único sem reverificar E6.

## Arquitetura

`rag.py` é a única implementação do pipeline. O notebook, os scripts `scripts/00`–`07` e o `app.py` só chamam funções dele, e o `ferramentas/verificar.py e7_duplicadas` confere isso. `config.py` guarda modelos, caminhos, tamanho de chunk e k; os modelos também podem vir das variáveis de ambiente `MODELO_CHAT` e `MODELO_EMBEDDING`.

- **Não edite `webinario_rag.ipynb` à mão.** Ele é gerado por `ferramentas/construir_notebook.py` e executado por `ferramentas/executar_notebook.py`, que salva as saídas.
- As chaves `REINDEXAR`, `LLM_AO_VIVO` e `SHAP_AO_VIVO` na 1ª célula alternam entre rodar ao vivo e carregar `resultados/` (versionado). `--offline` testa esse caminho.
- `resultados/` é gerado pelos scripts 02, 05 e 06, por `opcional/calcular_shapley_chunks.py` (~10 min) e pela célula do bloco 6.
- A coleção do ChromaDB é recriada do zero a cada `indexar()`: é idempotente e leva ~19 min em CPU. Nunca rode isso durante uma medição.
- Máquina de demo com pouca RAM livre (< 0,7 GB): trocar de modelo custa 40–80 s e degrada o 3b. Em medições, não rode outra carga pesada ao mesmo tempo (`docs/medicoes.md`).

Cronograma (~1h54): recap 10 · indexação 18 · retrieval top-k 15 · dois estágios 7 · SHAP 12 · com/sem contexto 12 · Ollama 12 · Streamlit 15 · RAGAS/reranking/encerramento 8 · folga 5.

## Pendências do autor

- Escolha dos 1–2 artigos em português (E1 critério 1.8).
- Perguntas-teste definitivas (marcadas com `TODO(autor)` em `scripts/06_com_sem_contexto.py`, `opcional/avaliacao_estilo_ragas.py` e no notebook).
- Decisão do modelo ao vivo, 3b ou 1.5b (E9 critério 9.3), no ensaio de 21/09.

## Comandos

No Windows, use Git Bash ou PowerShell com `PYTHONIOENCODING=utf-8`.

```bash
.venv/Scripts/python scripts/00_checar_ambiente.py
.venv/Scripts/python scripts/02_indexar.py
.venv/Scripts/streamlit run app.py
bash ferramentas/rodar_scripts.sh
.venv/Scripts/python ferramentas/construir_notebook.py
.venv/Scripts/python ferramentas/executar_notebook.py
.venv/Scripts/python ferramentas/executar_notebook.py --offline
.venv/Scripts/python ferramentas/testar_app.py
.venv/Scripts/python ferramentas/verificar.py e3
.venv/Scripts/python ferramentas/medir.py nome_do_cenario
```

| Comando | O que faz |
|---|---|
| `scripts/00_checar_ambiente.py` | Checa o ambiente |
| `scripts/02_indexar.py` | Reindexa (~19 min) |
| `streamlit run app.py` | Sobe o app |
| `ferramentas/rodar_scripts.sh` | Roda `scripts/00`–`07` em sequência, com log em `docs/evidencias/E7/` |
| `ferramentas/construir_notebook.py` | Regenera o notebook |
| `ferramentas/executar_notebook.py` | Executa o notebook e salva as saídas |
| `ferramentas/executar_notebook.py --offline` | Testa as saídas pré-computadas |
| `ferramentas/testar_app.py` | Testa o Streamlit com `AppTest` (E8) |
| `ferramentas/verificar.py e3` | Roda a verificação de uma etapa; também aceita e1_resumos, e2, e2_sobreposicao, e2_reabrir, e4, e6_ollama_desligado, e6_fontes, e7_duplicadas e e7_estrutura |
| `ferramentas/medir.py nome_do_cenario` | Mede os tempos (E9) |

## Agent skills

### Issue tracker

Issues vivem no GitHub (`Roger-Quinelato/webinarioOllamaRAG`), via `gh` CLI. Ver [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md).

### Triage labels

Vocabulário padrão (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). Ver [docs/agents/triage-labels.md](docs/agents/triage-labels.md).

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` na raiz (ainda não existem; criados sob demanda pelo `/domain-modeling`). Ver [docs/agents/domain.md](docs/agents/domain.md).
