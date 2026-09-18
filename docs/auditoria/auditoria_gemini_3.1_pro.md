# Auditoria do Repositório webinarioOllamaRAG

## Sumário Executivo

A auditoria cobriu as 12 frentes definidas para o projeto webinarioOllamaRAG. O repositório encontra-se em bom estado geral, aderente às decisões de arquitetura documentadas, especialmente na centralização da lógica no `rag.py`. Foram identificadas **2 issues** no total: **1 de severidade Alta** e **1 de severidade Média**. 

**Avaliação frente ao `VERIFICACAO.md`:** 
O projeto **não** está inteiramente no estado que o `docs/VERIFICACAO.md` alega, pois o critério E8 carece de evidências versionadas (capturas de tela ausentes no git), invalidando o status ✅. Por outro lado, as pendências legadas citadas no checklist (1.6 e 6.7) já foram devidamente implementadas e verificadas no código atual.

As demais frentes (1, 4, 5, 6, 8, 9, 10, 12) não apresentaram achados.

## Diagrama de Fluxo

```mermaid
flowchart TD
    A[PDFs do corpus<br>8 artigos, arXiv/SBC] --> B(Extração + limpeza<br>pypdf, por página)
    B --> C(Chunking<br>1000 car., overlap 150<br>+ resumo por LLM)
    
    C -->|⚠️ AUD-002: Falha Ollama não tratada| D(Embeddings<br>Ollama · bge-m3)
    D --> E[(ChromaDB<br>coleção persistente,<br>recriada a cada indexação)]
    
    E --> F{Busca}
    F -->|Busca simples| G1[top-k | filtros where]
    F -->|Dois estágios| G2[1º resumos -> 2º artigos]
    G2 -.->|Fallback limiar 0.60| G1
    
    G1 --> H(Prompt system+user<br>+ Ollama chat<br>qwen2.5:1.5b)
    G2 --> H
    
    H --> I[Resposta + fontes citadas<br>CLI · Streamlit · notebook]
    I -.->|⚠️ AUD-001: Capturas não versionadas| J([Documentação / Evidências])
```
*Nota: A coleção do ChromaDB é recriada do zero a cada indexação. O fallback do estágio 1 ocorre quando o resumo mais próximo está acima do limiar configurado (0.60). A citação de fontes reflete estritamente o que foi utilizado na resposta final. O SHAP atua em vias separadas: explicação ao vivo de palavras da pergunta e cálculo Shapley pré-computado.*

## Lista Completa de Issues

### Frente 11: Documentação e consistência

**ID:** AUD-001
**Severidade:** Alta
**Título:** Capturas de tela do E8 não versionadas (untracked) no git
**O que deveria fazer:** As evidências (capturas de tela) devem estar versionadas no repositório para sustentar os critérios 8.2, 8.4, 8.5 e 8.7 do `docs/VERIFICACAO.md`, garantindo que o status de verificação seja reproduzível e rastreável.
**Motivo (causa raiz):** Os arquivos de imagem (PNGs) estão presentes no diretório local `docs/evidencias/E8/capturas/`, mas o comando `git status` revela que este diretório está untracked. Consequentemente, a documentação atesta um status verificado com evidência falsa no histórico do repositório.
**Local exato do fix:** `docs/evidencias/E8/capturas/` (diretório a ser adicionado ao controle de versão).
**Sugestão de correção:** Executar `git add docs/evidencias/E8/capturas/` e commitar as imagens para o repositório.

### Frentes 2 e 3: Ingestão e Indexação

**ID:** AUD-002
**Severidade:** Média
**Título:** Tratamento de indisponibilidade do Ollama ausente nos scripts 01 e 02
**O que deveria fazer:** Scripts CLI que dependem do LLM devem tratar exceções de indisponibilidade do Ollama, convertendo-as em uma mensagem amigável ao usuário com saída de código 2, utilizando o context manager `rag.cli_seguro()` definido pelo projeto.
**Motivo (causa raiz):** Os scripts realizam requisições ao Ollama (`rag.resumir_abstract` e `rag.indexar`), porém não estão envolvidos no gerenciador de contexto `with rag.cli_seguro():`. Na ausência do servidor Ollama, os scripts quebram com um traceback cru (`ConnectionError` / `OllamaIndisponivel`).
**Local exato do fix:**
- `scripts/01_preparar_corpus.py`: linha 17 em diante (bloco principal)
- `scripts/02_indexar.py`: linha 21 em diante (bloco principal)
**Sugestão de correção:** Envolver a execução principal de ambos os scripts em um bloco `with rag.cli_seguro():`.

*(As frentes 1, 4, 5, 6, 7, 8, 9, 10 e 12 foram auditadas e não apresentaram achados. A pendência de lógica duplicada foi refutada pela checagem `e7_duplicadas`. A pendência dos scripts 03-06 (6.7) e da seção de conferência (1.6) já encontram-se devidamente implementadas e validadas no código).*

## Anexo de Rastreabilidade

Arquivos efetivamente inspecionados durante a auditoria:
- `CLAUDE.md`
- `docs/VERIFICACAO.md`
- `config.py`
- `rag.py`
- `app.py`
- `scripts/01_preparar_corpus.py`
- `scripts/02_indexar.py`
- `scripts/03_buscar.py`
- `scripts/04_dois_estagios.py`
- `scripts/05_shap.py`
- `scripts/06_com_sem_contexto.py`
- `opcional/avaliacao_estilo_ragas.py`
- `docs/evidencias/E1/verificacao_E1.txt`
- `docs/evidencias/E8/capturas/` (inspeção via `git status` e listagem de diretório)
