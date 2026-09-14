# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Verificação obrigatória

**Toda tarefa começa e termina em [docs/VERIFICACAO.md](docs/VERIFICACAO.md).** Antes: identificar a etapa (E0–E10), ler os critérios e conferir os pré-requisitos. Depois: rodar as verificações, salvar a evidência em `docs/evidencias/EN/`, atualizar os status, reverificar as etapas dependentes e adicionar uma linha no registro de execuções. Nenhum critério vira ✅ sem evidência, e nenhum critério é afrouxado para passar.

## Propósito

Material do webinário CIIA **Encontro 2 — "Construindo um Assistente com RAG, Ollama e Streamlit"**, conduzido por Roger Quinelato (suporte: João Victor Rikio Enomoto). Turmas: 21/09/2026 (CIIA, ensaio) e 28/09/2026 (público aberto), online, mesmo material. O Encontro 1 foi só teoria: todo o código prático nasce aqui.

Formato: demonstração ao vivo; participantes (nível intermediário/avançado) replicam depois pelo notebook, pelos scripts e pelo vídeo de instalação no YouTube do CIIA. O código precisa rodar sozinho, de ponta a ponta, na máquina de quem assiste.

## Estado atual

Implementado e verificado nas etapas E0–E9 (status em `docs/VERIFICACAO.md`). O git está na branch `main` e **ainda não tem commits**. O `.gitignore` exclui `.venv/`, `Ollama/models/`, `chroma_db/` e todos os PDFs de `arquivosPDF/`.
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
| `ferramentas/verificar.py e3` | Roda a verificação de uma etapa; também aceita e1_resumos, e2, e2_sobreposicao, e2_reabrir, e4, e6_ollama_desligado, e7_duplicadas e e7_estrutura |
| `ferramentas/medir.py nome_do_cenario` | Mede os tempos (E9) |
