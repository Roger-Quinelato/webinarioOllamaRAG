# Medições de desempenho

Todos os números abaixo foram medidos **nesta máquina**, entre 13 e 14/09/2026. Cada um aponta para o arquivo de evidência de onde saiu.

| Item | Valor |
|---|---|
| CPU | Intel Core i5-8250U, só GPU integrada (UHD 620) |
| RAM | 7,9 GB. **Livre durante os testes: 0,22 a 0,68 GB** (Claude, Chrome e Streamlit abertos) |
| Ollama | 0.34.0, modelos em `D:\webinarioOllamaRAG\Ollama\models` |
| Corpus | 6 artigos, 109 páginas, 556 chunks (550 de página + 6 de resumo), vetores de 1024 dimensões |

Ferramenta principal: `ferramentas/medir.py <cenario>`. Os tokens por segundo vêm dos campos `prompt_eval_*`, `eval_*` e `load_duration` que o próprio Ollama devolve.

## 9.1 — Tempos por etapa

### Indexação e busca

| Etapa | Medições | Evidência |
|---|---|---|
| Chunking (556 chunks) | 9,0 s | `E7/log_02_indexar.txt` |
| Indexação completa com `bge-m3` (embeddings + ChromaDB) | 1141,1 s · 1111,0 s · 1104,1 s | `E2/02_indexar_execucao1.txt`, `E2/02_indexar_execucao2.txt`, `E7/log_02_indexar.txt` |
| Embedding de uma pergunta, 1ª chamada (carrega o `bge-m3`) | 58,84 s · 4,56 s | `E9/medicao_*.json` |
| Embedding de uma pergunta, já carregado | 0,54 s · 0,53 s | `E9/medicao_*.json` |
| Busca top-4 (embedding + consulta), 1ª e 2ª rodada | 8,52 s → 3,84 s · 3,91 s → 0,22 s | `E9/medicao_*.json` |
| Busca em dois estágios | 1,16 s · 0,24 s | `E9/medicao_*.json` |

### SHAP e Shapley

| Etapa | Medições | Evidência |
|---|---|---|
| SHAP de 1 chunk (`max_evals=200`), frio | 112,0 s · 81,6 s | `E5/05_shap.txt`, `E7/log_05_shap.txt` |
| SHAP de 1 chunk, `bge-m3` já carregado | 18,9 s · 19,7 s | `E5/05_shap.txt`, `E7/log_05_shap.txt` |
| SHAP no notebook | 37 s · 34 s · 48 s · 36 s (última execução: 2026-09-15) | `E7/saidas_notebook.txt`, `E5/notebook_E5.txt` |
| SHAP no `medir.py` (RAM livre < 0,6 GB) | 74,0 s · 89,3 s | `E9/medicao_*.json` |
| Shapley exato dos 4 chunks (16 gerações com o 3b) | 621 s | `E5/calcular_shapley_chunks.txt` |

### LLM

| Etapa | Medições | Evidência |
|---|---|---|
| Cargas de modelo registradas pelo servidor Ollama (3b, 1.5b e bge-m3) | 40,2 a 79,5 s | `E9/ollama_server_carga_modelos.txt` |
| Carregar o `qwen2.5:1.5b` | 43,2 s · 42,1 s · 41,0 s | `E9/medicao_*.json` (`carga_modelo_s`) |
| `qwen2.5:3b`: processamento do prompt, sem cache | 41,4 · 27,2 · 24,8 · 13,5 tokens/s | `E9/medicao_*.json` |
| `qwen2.5:3b`: geração | 5,6 a 7,4 tokens/s (caiu para 3,0 e 4,1 logo depois de trocar de modelo) | `E9/medicao_*.json` |
| `qwen2.5:1.5b`: processamento do prompt | 51,8 · 52,8 · 57,7 · 58,6 tokens/s | `E9/medicao_*.json` |
| `qwen2.5:1.5b`: geração | 13,1 a 14,5 tokens/s | `E9/medicao_*.json` |
| Resposta RAG k=4 com o 3b (~1000 tokens de prompt), sem cache | 42,4 s · 117,8 s · 89,96 s | `E9/medicao_*.json` |
| Resposta RAG k=4 com o 3b logo após voltar do 1.5b | **156,8 s** | `E9/medicao_sem_streamlit.json` |
| Resposta RAG k=4 com o 1.5b, já carregado | 20,4 s · 20,2 s | `E9/medicao_*.json` |
| Resumo de um abstract (3b), frio → quente | 232,2 s → 14,7 a 37,6 s | `E1/01_preparar_corpus.txt` |
| Resumo ao vivo no notebook | 8,1 s | `E7/saidas_notebook.txt` |
| Extração de metadados por LLM, frio → quente | 134,9 s · 136,9 s → 16,6 s | `E2/02_indexar_execucao1.txt`, `E7/log_02_indexar.txt`, `E7/saidas_notebook.txt` |
| Pergunta no Streamlit (AppTest, 3b, k=2 e k=5) | 8 s · 17 s | `E8/apptest.txt` |
| Streaming no navegador (3b, k=4) | texto começou ~9,5 s após a legenda "Caminho usado" e ainda crescia 15 s depois | `E8/ui_navegador.txt` |

### Notebook e instalação

| Etapa | Medições | Evidência |
|---|---|---|
| Notebook inteiro ao vivo (21 células) | 959 s na última execução, com pouca RAM livre; uma execução anterior levou 188 s, mas o log dela foi sobrescrito | `E7/execucao_notebook.txt` |
| Notebook inteiro offline (`LLM_AO_VIVO = SHAP_AO_VIVO = False`) | 61 s | `E7/execucao_notebook_offline.txt` |
| `pip install` das dependências | mais de 50 min na 1ª vez (23h58 → antes de 01h01); 1311 s num `.venv` novo com cache | `E0/ambiente.txt`, `E10/readme_do_zero.txt` |
| Avaliação no estilo RAGAS (opcional, 2 perguntas) | 402 s · 203 s | `opcional/avaliacao_estilo_ragas.txt` |

> Observação sobre o cache: o Ollama reaproveita o prefixo de um prompt idêntico. Por isso algumas rodadas registram mais de 7000 tokens/s de prompt: foram perguntas repetidas entre os cenários. Esses valores não entram nas faixas acima.

## 9.2 — Com navegador e Streamlit abertos (simulando a live)

| Etapa | Sem Streamlit | Com Streamlit + navegador |
|---|---|---|
| RAM livre no início | 0,61 GB | 0,59 GB |
| Busca top-4 (já carregado) | 3,84 s | 0,22 s |
| SHAP de 1 chunk | 74,0 s | 89,3 s |
| 3b, 1ª pergunta sem cache | 42,4 s (41,4 tokens/s de prompt) | 89,96 s (13,5 tokens/s de prompt) |
| 1.5b, carga + 1ª resposta | 72,5 s | 71,8 s |
| 1.5b, já carregado | 20,4 s | 20,2 s |

Arquivos: `docs/evidencias/E9/medicao_sem_streamlit.json` e `medicao_com_streamlit_e_navegador.json`. Nos dois cenários o gargalo é a **RAM**, não o disco. Com menos de 0,7 GB livres, o processamento do prompt do 3b variou de 13,5 a 41,4 tokens/s.

## 9.3 — Decisões

| Decisão | Situação | Base |
|---|---|---|
| `Ollama/models` no D: ou no C: | **Manter no D:.** O tempo de carga (40–80 s) e as quedas de desempenho acompanham a RAM livre, e nenhuma medição apontou o disco como gargalo. Não houve comparação direta com o C:. | Seções 9.1 e 9.2 |
| `qwen2.5:3b` ao vivo ou plano B | **Decisão parcial do autor, 2026-09-15 (ticket #19):** `config.MODELO_CHAT` agora é `qwen2.5:1.5b`, para validar a pipeline inteira primeiro. Ele processa o prompt ~2× mais rápido (52–59 contra 13–41 tokens/s) e gera ~2× mais rápido (13–14,5 contra 7 tokens/s), e respondeu em ~20 s contra 42–164 s do 3b. O `qwen2.5:3b` vira `config.MODELO_CHAT_PLANO_B`, para testar depois se a máquina/o notebook aguenta bem — decisão final (e as perguntas-teste) seguem para o ensaio de 21/09. | Seção 9.1 |
| Alternar entre os modelos durante a live | **Não alternar.** Cada troca custa 40–80 s de carga, e voltar ao 3b logo depois derrubou a geração para 3,0 tokens/s (156,8 s de resposta). | `E9/medicao_sem_streamlit.json` |
| Reindexar ao vivo | **Não.** São 1104–1141 s, maior que o bloco 2 inteiro (18 min = 1080 s). O notebook usa `REINDEXAR = False`. | Seção 9.1 |

## 9.4 — Cada bloco cabe no cronograma?

| Bloco | Min | Operações lentas ao vivo (medido) | Cabe? | Ajuste proposto |
|---|---|---|---|---|
| 1 Recap | 10 | `verificar_ollama` (< 1 s) | Sim | Aquecer os modelos **antes** da live (carga de 40–80 s) |
| 2 Indexação | 18 | Reabrir a coleção (< 5 s); extração por LLM 16,6 s quente / 135 s frio; resumo 8,1 s quente / 232 s frio | Sim, **se aquecido** | Não reindexar; com o modelo frio, `LLM_AO_VIVO = False` |
| 3 Retrieval | 15 | 7 buscas × 0,2–8,5 s | Sim | — |
| 3b Dois estágios | 7 | 2 comparações × < 2 s | Sim | — |
| 4 SHAP | 12 | SHAP 19–112 s (36 s na última execução do notebook, 2026-09-15, `E7/saidas_notebook.txt`); Shapley só carregado | Sim | Com RAM baixa (> 90 s), `SHAP_AO_VIVO = False` |
| 5 Com × sem contexto | 12 | 2 gerações: 1,6–51 s cada (3b) | Sim | — |
| 6 Ollama | 12 | 1 resposta em streaming: 8–164 s (3b; 70,6 s na última execução do notebook, 2026-09-15, `E7/saidas_notebook.txt`) | Sim, com folga curta no pior caso | Preferir o 1.5b ao vivo (~20 s) |
| 7 Streamlit | 15 | 8–17 s por pergunta com cache quente (AppTest); 42–118 s por resposta sem cache (3b) | ~4 perguntas no pior caso | Limitar a 4 perguntas; 1.5b se estiver lento |
| 8 Avaliação | 8 | Só carrega resultados | Sim | — |

Resumo: o cronograma de ~1h54 cabe **com os modelos aquecidos e sem trocar de modelo**. O maior risco é a RAM livre abaixo de 1 GB. Antes da live, feche o que não for necessário.
