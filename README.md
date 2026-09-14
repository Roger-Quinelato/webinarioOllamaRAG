# Assistente com RAG, Ollama e Streamlit

Material prático do **Webinário CIIA — Encontro 2**. Um assistente que responde perguntas sobre artigos científicos de RAG usando só ferramentas locais:

- **Ollama** serve o modelo de embedding (`bge-m3`) e o modelo de chat (`qwen2.5:3b`, com plano B `qwen2.5:1.5b`).
- **ChromaDB** guarda os vetores em disco.
- **Streamlit** fornece a interface de chat.
- **SHAP** explica o retrieval.

Não usamos LangChain nem LlamaIndex: o código é Python puro, para você enxergar cada peça do RAG.

```
PDFs → texto por página → chunks → embeddings → ChromaDB
pergunta → embedding → top-k (+ filtros) → prompt com trechos → LLM → resposta com fontes
```

## Requisitos

| Item | Mínimo |
|---|---|
| Python | 3.10 ou superior |
| RAM | 8 GB (o LLM roda na CPU se não houver GPU) |
| Disco | ~5 GB para os modelos + ~1 GB para o ambiente Python |
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
ollama pull qwen2.5:3b
ollama pull qwen2.5:1.5b
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

O script baixa os artigos do arXiv para `arquivosPDF/artigos/` (os PDFs não ficam no repositório), valida o `metadados.csv` e gera com o LLM os resumos que estiverem vazios.

| Arquivo | Artigo |
|---|---|
| `lewis2020_rag.pdf` | Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* — <https://arxiv.org/abs/2005.11401> |
| `karpukhin2020_dpr.pdf` | Karpukhin et al. (2020). *Dense Passage Retrieval for Open-Domain Question Answering* — <https://arxiv.org/abs/2004.04906> |
| `gao2023_survey.pdf` | Gao et al. (2023). *Retrieval-Augmented Generation for Large Language Models: A Survey* — <https://arxiv.org/abs/2312.10997> |
| `es2023_ragas.pdf` | Es et al. (2023). *Ragas: Automated Evaluation of Retrieval Augmented Generation* — <https://arxiv.org/abs/2309.15217> |
| `asai2023_selfrag.pdf` | Asai et al. (2023). *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* — <https://arxiv.org/abs/2310.11511> |
| `liu2023_lost_middle.pdf` | Liu et al. (2023). *Lost in the Middle: How Language Models Use Long Contexts* — <https://arxiv.org/abs/2307.03172> |

### 7. Indexar

```bash
python scripts/02_indexar.py
```

O script cria a coleção em `chroma_db/`. Pode rodar de novo quantas vezes quiser: a coleção é recriada do zero, sem duplicar chunks. Sem GPU, espere cerca de 20 minutos (1104 a 1141 s na máquina de teste, ver [docs/medicoes.md](docs/medicoes.md)).

### 8. Explorar a busca, o SHAP e o LLM

```bash
python scripts/03_buscar.py
python scripts/04_dois_estagios.py
python scripts/05_shap.py
python scripts/06_com_sem_contexto.py
python scripts/07_ollama.py "Como o Self-RAG decide quando buscar documentos?"
```

Você também pode abrir o `webinario_rag.ipynb` no VS Code, escolher o kernel **Python (webinario-rag)** e seguir os blocos da aula. As saídas já vêm salvas no notebook, então dá para acompanhar sem rodar nada.

### 9. Abrir o chatbot

```bash
streamlit run app.py
```

O navegador abre em <http://localhost:8501>. Na barra lateral você escolhe o modelo, o `k`, a busca simples ou em dois estágios, e os filtros de ano, tema e idioma.

## Estrutura

| Caminho | Função |
|---|---|
| `config.py` | Modelos, caminhos, tamanho de chunk e `k` padrão |
| `rag.py` | Todas as funções do pipeline, usadas pelo notebook, pelos scripts e pelo app |
| `metadados.csv` | Metadados escritos à mão (+ resumo gerado pelo LLM) |
| `scripts/` | Um script por bloco da aula, em ordem |
| `webinario_rag.ipynb` | Notebook da aula (gerado por `ferramentas/construir_notebook.py`) |
| `app.py` | Chatbot Streamlit |
| `opcional/` | Shapley dos chunks e avaliação no estilo RAGAS (lentos; não rodam ao vivo) |
| `resultados/` | Saídas pré-computadas usadas como rede de segurança na aula |
| `docs/` | Roteiro do facilitador, troubleshooting, medições e verificação |

## Para quem mantém o material

```bash
python -m pip install -r requirements-dev.txt
python ferramentas/construir_notebook.py
python ferramentas/executar_notebook.py
bash ferramentas/rodar_scripts.sh
python ferramentas/testar_app.py
python ferramentas/medir.py nome_do_cenario
python ferramentas/gerar_plano_v11.py
```

| Comando | O que faz |
|---|---|
| `construir_notebook.py` | Gera o `webinario_rag.ipynb` a partir do código-fonte das células |
| `executar_notebook.py` | Executa o notebook em kernel limpo e salva as saídas (`--offline` testa as saídas pré-computadas) |
| `rodar_scripts.sh` | Roda `scripts/00`–`07` em sequência, com log |
| `testar_app.py` | Testa o Streamlit com `AppTest` |
| `medir.py` | Mede os tempos desta máquina |
| `gerar_plano_v11.py` | Gera o plano de aula v1.1 em `docs/` |

Critérios e evidências de cada etapa: [docs/VERIFICACAO.md](docs/VERIFICACAO.md).

### Auditoria de código (E10)

Além da verificação por etapa (E0–E9), o `docs/evidencias/E10/revisao_codigo.md` registra uma revisão em dois eixos — **Standards** (o código segue o `CLAUDE.md` e o `docs/VERIFICACAO.md`?) e **Spec** (o resultado bate com o que cada critério pede?) — feita por dois sub-agentes de só leitura, com os achados conferidos manualmente no código. As checagens estáticas que a acompanham estão em `docs/evidencias/E10/revisao_codigo_checagens.txt`, e uma versão navegável em `docs/evidencias/auditoria_plano.html`.

A auditoria **não mudou nenhum ✅** de `docs/VERIFICACAO.md`: ela lista achados e um conjunto de critérios contestados (1.6, 4.4, 6.5, 6.7, 7.4, 8.2/8.4/8.5/8.7, 5a.1/7.2/9.1) para reverificar antes da próxima etapa, sem afrouxar nenhum critério para passar.

## Trocar para o modelo menor

Se as respostas estiverem lentas, mude `MODELO_CHAT` em `config.py` para `"qwen2.5:1.5b"`, ou defina a variável de ambiente `MODELO_CHAT=qwen2.5:1.5b`. Nada mais precisa mudar.

## Problemas comuns

Veja [docs/troubleshooting.md](docs/troubleshooting.md).
