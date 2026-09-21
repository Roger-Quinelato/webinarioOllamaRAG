# Assistente híbrido com RAG, Ollama e OpenAI

Material prático do **Webinário CIIA — Encontro 2**. Um assistente que recupera artigos localmente e gera respostas grounded com providers remotos:

- **Ollama** serve somente embeddings `bge-m3` (1024 dimensões).
- **OpenAI**, **NVIDIA** e **Gemini** geram respostas com streaming. Ordem padrão: OpenAI, NVIDIA, Gemini.
- **ChromaDB** guarda o **Corpus Oficial** persistente e o **Índice de Sessão** efêmero.
- **Streamlit** fornece a interface de chat.
- **SHAP** explica o retrieval.

Não usamos LangChain nem LlamaIndex: o código é Python puro, para você enxergar cada peça do RAG.

## Arquitetura vigente

`bge-m3` via Ollama cria e consulta vetores. Providers remotos geram texto. Cada pergunta usa uma única **Base Ativa**: **Corpus Oficial** ou **Índice de Sessão**. Contexto insuficiente produz **Recusa**. O roteador troca entre OpenAI, NVIDIA e Gemini somente antes do primeiro token. Não existe fallback automático para geração local; rollback exige a tag `legacy-pre-openai`.

```
PDFs → texto por página → chunks → embeddings → ChromaDB
pergunta → embedding → top-k (+ filtros) → prompt com trechos → LLM → resposta com fontes
```

## Requisitos

| Item | Mínimo |
|---|---|
| Python | 3.10 ou superior |
| RAM | 8 GB |
| Disco | Espaço para `bge-m3`, corpus e ambiente Python |
| Editor | VS Code com as extensões *Python* e *Jupyter* (ou JupyterLab) |

## Passo a passo

### 1. Instalar o Ollama

- **Windows e macOS:** baixe o instalador em <https://ollama.com/download> e abra o aplicativo.
- **Linux:**
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

Confira a instalação:
```bash
ollama --version
```

### 2. (Opcional) Escolher onde os modelos ficam

Por padrão, os modelos vão para `~/.ollama/models`. Para usar outra pasta, defina `OLLAMA_MODELS` **antes** de baixar os modelos e reinicie o Ollama.

- **Windows (PowerShell):**
  ```powershell
  [Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "D:\webinarioOllamaRAG\Ollama\models", "User")
  ```
  Depois feche o Ollama pelo ícone da bandeja e abra de novo.
- **macOS e Linux:** adicione `export OLLAMA_MODELS=/caminho/models` ao `~/.zshrc` ou `~/.bashrc`, abra um novo terminal e reinicie o Ollama.

### 3. Baixar os modelos

```bash
ollama pull bge-m3
```

### 4. Obter o código e criar o ambiente Python

```bash
git clone <url-do-repositorio> webinarioOllamaRAG
cd webinarioOllamaRAG
python -m venv .venv
```

Ative o ambiente:
- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **macOS e Linux:** `source .venv/bin/activate`

Instale as dependências (as versões estão fixadas; `requirements.lock` lista o ambiente completo testado) e registre o kernel do Jupyter:
```bash
python -m pip install -r requirements.txt
python -m ipykernel install --user --name webinario-rag --display-name "Python (webinario-rag)"
```

> A instalação é demorada: numa máquina com Windows, i5 e 8 GB de RAM, passou de 50 minutos. Deixe rodando até o fim.
> No PowerShell, rode `$env:PYTHONIOENCODING='utf-8'` antes dos scripts para os acentos aparecerem certos.

### 5. Checar o ambiente

```bash
python scripts/00_checar_ambiente.py
```

A última linha deve ser `Ambiente pronto.`

### 6. Baixar os artigos e preparar os metadados

```bash
python scripts/01_preparar_corpus.py
```

O script baixa os artigos para `arquivosPDF/artigos/` (os PDFs não ficam no repositório) e valida o `metadados.csv`. A apresentação não depende de geração por modelo local.

| Arquivo | Artigo |
|---|---|
| `lewis2020_rag.pdf` | Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* — <https://arxiv.org/abs/2005.11401> |
| `karpukhin2020_dpr.pdf` | Karpukhin et al. (2020). *Dense Passage Retrieval for Open-Domain Question Answering* — <https://arxiv.org/abs/2004.04906> |
| `gao2023_survey.pdf` | Gao et al. (2023). *Retrieval-Augmented Generation for Large Language Models: A Survey* — <https://arxiv.org/abs/2312.10997> |
| `es2023_ragas.pdf` | Es et al. (2023). *Ragas: Automated Evaluation of Retrieval Augmented Generation* — <https://arxiv.org/abs/2309.15217> |
| `asai2023_selfrag.pdf` | Asai et al. (2023). *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* — <https://arxiv.org/abs/2310.11511> |
| `liu2023_lost_middle.pdf` | Liu et al. (2023). *Lost in the Middle: How Language Models Use Long Contexts* — <https://arxiv.org/abs/2307.03172> |
| `rocha2025_ragsft.pdf` | Rocha et al. (2025). *Aprimorando Geração Aumentada por Recuperação via Ajuste Fino Sequencial de Modelos de Linguagem Pequenos* (SBBD) — <https://sol.sbc.org.br/index.php/sbbd/article/view/37242> |
| `medeiros2025_embeddings_pt.pdf` | Medeiros & Oliveira (2025). *Comparação de Modelos de Embeddings e LLMs para Geração Aumentada por Recuperação em Português* (SEMISH) — <https://sol.sbc.org.br/index.php/semish/article/view/36829> |

### 7. Indexar

```bash
python scripts/02_indexar_hibrido.py
```

O script publica a coleção híbrida com `bge-m3` e preserva coleções existentes.

### 8. Consultar

Use o aplicativo para consultar o Corpus Oficial:

```bash
streamlit run app.py
```

O material CLI híbrido pertence à MIG-06 e não está disponível nesta base até
ser mergeado. Não use scripts legados de geração Ollama para validar a
arquitetura atual.

### 9. Abrir o chatbot

Configure pelo menos uma chave antes de iniciar. A ordem padrão é OpenAI,
NVIDIA e Gemini:

```powershell
$env:OPENAI_API_KEY = "..."
$env:NVIDIA_API_KEY = "..."
$env:NVIDIA_MODEL = "..."
$env:NVIDIA_TIMEOUT = "30" # segundos; opcional
$env:GEMINI_API_KEY = "..."
$env:GEMINI_MODEL = "..."
$env:GEMINI_TIMEOUT = "30" # segundos; opcional
```

```bash
streamlit run app.py
```

O navegador abre em <http://localhost:8501>. Durante o treino, a UI consulta somente o **Corpus Oficial**. `UPLOADS_STREAMLIT_HABILITADOS=False` mantém upload de PDFs para implementação futura. A interface separa **Fontes Citadas**, **Chunks Recuperados**, **Recusa** e **Resposta Parcial**. `NVIDIA_BASE_URL` pode apontar para outro endpoint NIM compatível.

## Estrutura

| Caminho | Função |
|---|---|
| `config.py` | Modelos, caminhos, tamanho de chunk e `k` padrão |
| `openai_rag.py` | Fachada grounded: Base Ativa, retrieval, fontes, recusa e streaming |
| `hybrid_index.py` | Publicação e abertura do Corpus Oficial híbrido |
| `metadados.csv` | Metadados e resumos versionados do Corpus Oficial |
| `scripts/` | Um script por bloco da aula, em ordem |
| `webinario_rag.ipynb` | Material histórico do Encontro 2, baseado em Ollama; não é executado na aula híbrida atual |
| `app.py` | Chatbot Streamlit |
| `opcional/` | Shapley dos chunks e avaliação no estilo RAGAS (lentos; não rodam ao vivo) |
| `resultados/` | Saídas pré-computadas usadas como rede de segurança na aula |
| `docs/` | Roteiro do facilitador, troubleshooting, medições e verificação |

## Para quem mantém o material

```bash
python -m pip install -r requirements-dev.txt
python ferramentas/construir_notebook.py
python ferramentas/executar_notebook.py --offline
bash ferramentas/rodar_scripts.sh
python -m unittest tests.test_app -v
python ferramentas/medir.py nome_do_cenario
python ferramentas/gerar_plano_v11.py
```

| Comando | O que faz |
|---|---|
| `construir_notebook.py` | Gera o `webinario_rag.ipynb` a partir do código-fonte das células |
| `executar_notebook.py` | Executa o notebook em kernel limpo; `--offline` não chama Ollama nem OpenAI |
| `rodar_scripts.sh` | Roda `02_indexar_hibrido.py` e `calibrar_retrieval_hibrido.py`; grava logs locais ignorados em `logs/rodar_scripts/` |
| `python -m unittest tests.test_app` | Testa o Streamlit com `AppTest` (dono único em `tests/test_app.py`) |
| `medir.py` | Mede os tempos desta máquina |
| `gerar_plano_v11.py` | Gera o plano de aula v1.1 em `docs/` |

Critérios e evidências legadas foram removidos durante a migração OpenAI.

### Auditoria de código (E10)

O registro histórico `docs/evidencias/E10/revisao_codigo.md` mantém a auditoria
legada em dois eixos. As checagens estáticas estão em
`docs/evidencias/E10/revisao_codigo_checagens.txt`.

A auditoria histórica lista achados e critérios contestados; ela não valida a
migração OpenAI atual.

## Problemas comuns

Consulte o [troubleshooting](docs/troubleshooting.md) e o handoff da migração.
