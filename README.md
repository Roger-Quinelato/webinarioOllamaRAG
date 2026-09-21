# Assistente híbrido com RAG, Ollama e providers remotos

Um assistente que recupera trechos de artigos localmente e gera respostas fundamentadas (grounded) com providers remotos:

- **Ollama** gera somente os embeddings, com `granite-embedding:278m` (768 dimensões) por padrão — configurável por `MODELO_EMBEDDING` (ex.: `bge-m3`, mais pesado e também multilíngue).
- **NVIDIA**, **Gemini** e **OpenAI** geram as respostas com streaming. Ordem padrão: NVIDIA, Gemini, OpenAI, configurável por `GENERATION_PROVIDERS_ORDER`.
- **ChromaDB** guarda o índice vetorial persistente do corpus.
- **Streamlit** fornece a interface de chat.

Não usamos LangChain nem LlamaIndex: o código é Python puro, para você enxergar cada peça do RAG.

**Quer testar com os seus próprios documentos?** O notebook para o público,
[`notebooks/rag_com_seus_documentos.ipynb`](notebooks/rag_com_seus_documentos.ipynb),
roda no Google Colab sem instalar nada: você envia seus PDFs e ajusta os parâmetros de cada etapa.
[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Roger-Quinelato/webinarioOllamaRAG/blob/main/notebooks/rag_com_seus_documentos.ipynb)
Ele é material de treinamento separado do app e usa LangChain de propósito, para dar foco aos conceitos.
Para editá-lo, altere `notebooks/gerar_notebook_publico.py` e rode `python notebooks/gerar_notebook_publico.py`.

## Como funciona

```
PDFs → texto por página → chunks → embeddings (granite-embedding:278m) → ChromaDB
pergunta → embedding → top-k (+ filtros) → prompt com trechos → LLM remoto → resposta com fontes
```

O assistente responde apenas com base nos trechos recuperados. Se o contexto não basta, ele recusa a resposta em vez de usar conhecimento externo. O roteador troca de provider somente antes do primeiro token; não há fallback para geração local.

## Requisitos

| Item | Mínimo |
|---|---|
| Python | 3.10 ou superior |
| RAM | 8 GB |
| Disco | Espaço para `granite-embedding:278m`, corpus e ambiente Python |
| Chave de API | Pelo menos uma: NVIDIA, Gemini ou OpenAI |

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

Por padrão, os modelos ficam em `~/.ollama/models`. Para usar outra pasta, defina `OLLAMA_MODELS` antes de baixar o modelo e reinicie o Ollama.

### 2. Baixar o modelo de embeddings

```bash
ollama pull granite-embedding:278m
```

### 3. Obter o código e criar o ambiente Python

```bash
git clone https://github.com/Roger-Quinelato/webinario-rag.git
cd webinario-rag
python -m venv .venv
```

Ative o ambiente:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **macOS e Linux:** `source .venv/bin/activate`

Instale as dependências (versões fixadas; `requirements.lock` lista o ambiente completo testado):

```bash
python -m pip install -r requirements.txt
```

> A instalação é demorada: numa máquina com Windows, i5 e 8 GB de RAM, passou de 50 minutos.
> No PowerShell, rode `$env:PYTHONIOENCODING='utf-8'` antes dos scripts para os acentos aparecerem certos.

### 4. Checar o ambiente

```bash
python scripts/00_checar_ambiente.py
```

A última linha deve ser `Ambiente pronto.`

### 5. Baixar os artigos e validar os metadados

```bash
python scripts/01_preparar_corpus.py
```

O script baixa os artigos para `artigos/` (os PDFs não ficam no repositório) e valida o `metadados.csv`.

| Arquivo | Artigo |
|---|---|
| `rocha2025_ragsft.pdf` | Olivera et al. (2025). *Aprimorando Geração Aumentada por Recuperação via Ajuste Fino Sequencial de Modelos de Linguagem Pequenos* (SBBD) — <https://sol.sbc.org.br/index.php/sbbd/article/view/37242> |
| `medeiros2025_embeddings_pt.pdf` | Medeiros & Oliveira (2025). *Comparação de Modelos de Embeddings e LLMs para Geração Aumentada por Recuperação em Português* (SEMISH) — <https://sol.sbc.org.br/index.php/semish/article/view/36829> |
| `brakes2025_rag_juridico.pdf` | Brakes et al. (2025). *Uma Arquitetura de RAG com Busca Semântica e Filtros Estruturados para Perguntas e Respostas no Domínio Jurídico* (ERI-GO) — <https://sol.sbc.org.br/index.php/erigo/article/view/39531> |
| `xavier2024_rag_grafos.pdf` | Xavier & Soares (2024). *Geração com Recuperação Aumentada (RAG) em Grafos de Conhecimento* (Minicursos do SBBD) — <https://books-sol.sbc.org.br/index.php/sbc/catalog/book/153> |

### 6. Indexar

```bash
python scripts/02_indexar_hibrido.py
```

O script gera os chunks, cria os embeddings com o modelo configurado em `MODELO_EMBEDDING` (`granite-embedding:278m` por padrão) e publica a coleção no ChromaDB (`chroma_db/`).

### 7. (Opcional) Medir a recuperação

```bash
python scripts/calibrar_retrieval_hibrido.py
```

Roda perguntas positivas e negativas de referência contra o índice e mostra, em JSON, se o limiar de distância (`DISTANCIA_MAXIMA_RETRIEVAL` em `config.py`) separa bem as perguntas respondíveis das que devem ser recusadas.

### 8. Configurar as chaves e abrir o chatbot

Configure pelo menos uma chave. Provider omitido de `GENERATION_PROVIDERS_ORDER` fica desativado.

**Windows (PowerShell):**

```powershell
$env:GENERATION_PROVIDERS_ORDER = "nvidia,gemini,openai" # opcional
$env:NVIDIA_API_KEY = "..."
$env:NVIDIA_MODEL = "meta/llama-3.2-11b-vision-instruct"
$env:GEMINI_API_KEY = "..."
$env:GEMINI_MODEL = "gemini-3.5-flash"
$env:OPENAI_API_KEY = "..."
```

**macOS e Linux:** use `export NOME="valor"` com as mesmas variáveis.

Opcionais: `NVIDIA_TIMEOUT`, `GEMINI_TIMEOUT` e `OPENAI_TIMEOUT` (segundos) e `NVIDIA_BASE_URL` (outro endpoint NIM compatível). Também é possível colocar as chaves em `.streamlit/secrets.toml`, que o `.gitignore` já ignora. Nunca versione suas chaves.

```bash
streamlit run app.py
```

O navegador abre em <http://localhost:8501>. A interface separa as fontes citadas, os chunks recuperados, as recusas e as respostas parciais.

## Estrutura

| Caminho | Função |
|---|---|
| `config.py` | Modelos, caminhos, tamanho de chunk e `k` padrão |
| `corpus.py` | Extração de texto dos PDFs, limpeza e divisão em chunks |
| `metadados.csv` | Metadados e resumos dos artigos do corpus |
| `ollama_embedding_provider.py` | Embeddings locais via Ollama (`MODELO_EMBEDDING`, `granite-embedding:278m` por padrão) |
| `hybrid_index.py` | Publicação e abertura da coleção no ChromaDB |
| `openai_rag.py` | Núcleo do RAG: retrieval, prompt, fontes, recusa e streaming |
| `generation_router.py` | Troca de provider antes do primeiro token |
| `generation_providers.py` | Monta a ordem de providers a partir do ambiente |
| `nvidia_provider.py`, `gemini_provider.py`, `openai_provider.py` | Clientes de geração de cada provider |
| `retrieval_calibration.py` | Perguntas e métricas usadas na medição da recuperação |
| `rag.py` | Utilitários de corpus e verificação do Ollama usados pelos scripts 00 e 01 |
| `scripts/` | Etapas da pipeline, em ordem |
| `app.py` | Chatbot Streamlit |

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| Modelo de embedding não encontrado | Rode `ollama pull granite-embedding:278m` (ou o modelo em `MODELO_EMBEDDING`) e confira se o Ollama está aberto |
| Erro de conexão com o Ollama | Abra o aplicativo do Ollama (ou `ollama serve` no Linux) |
| App diz que a coleção não existe | Rode `python scripts/02_indexar_hibrido.py` antes de `streamlit run app.py` |
| Nenhum provider disponível | Defina pelo menos uma chave de API no mesmo terminal do `streamlit run` |
| HTTP 429 de um provider | Limite ou saldo esgotado; o roteador tenta o próximo provider da ordem |
| Acentos quebrados no PowerShell | `$env:PYTHONIOENCODING='utf-8'` |
