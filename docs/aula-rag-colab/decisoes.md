# Aula prática de RAG no Colab — decisões e benchmarks

> Auditoria de 2026-09-23 · Épico [#137](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/137) ·
> Issues [#131](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/131),
> [#139](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/139),
> [#140](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/140)

## 1. O critério: o que o aluno consegue fazer ao final

Toda escolha técnica respondeu à pergunta *"isso torna mais fácil para alguém aprender RAG?"*, medida por
estes resultados de aprendizagem:

| # | O aluno consegue… | Seção do notebook |
|---|---|---|
| O1 | explicar em uma frase o que é RAG e que problema ele resolve | §0, §2 |
| O2 | ler um PDF e inspecionar o texto extraído por página | §3 |
| O3 | dividir texto em chunks e explicar tamanho e sobreposição | §4 |
| O4 | gerar um embedding, ver o vetor e interpretar similaridade | §5 |
| O5 | criar um banco vetorial e dizer o que ele guarda | §6 |
| O6 | fazer uma busca top-k e ler o resultado (trecho, página, score) | §7 |
| O7 | montar contexto + prompt e ler o prompt real | §8, §9 |
| O8 | rodar um LLM na GPU do Colab e ver a memória usada | §1, §2, §10 |
| O9 | ligar cada `[n]` da resposta ao arquivo e à página | §11 |
| O10 | reconhecer limites: recusa correta, extração ruim, chunk ruim, alucinação residual | §12, §14 |

## 2. Por que um notebook novo

O notebook anterior (`notebooks/rag_com_seus_documentos.ipynb`) foi escrito para quem já programa: 78
células, mediana de 17 linhas por célula de código (7 células com 25 a 52 linhas), cerca de 30 conceitos
(incluindo MMR, HNSW, BM25/RRF, reranking, HyDE, LCEL, avaliação e GraphRAG), blocos 🎓/🔬/🧪 de
aprofundamento e **geração por API externa com chave**. Depois do teste com público, a direção mudou para
uma **aula prática** para público amplo, executada **100% no Colab**. Ele continua no repositório,
inalterado.

| Removido do fluxo | Motivo |
|---|---|
| Provedores remotos, chaves, Secrets, Ollama | a aula roda inteira no runtime do Colab |
| LCEL, `ChatPromptTemplate`, `as_retriever`, classe de prefixos | vocabulário do framework, não de RAG; esconde etapas |
| MMR, limiar, busca híbrida, reranking, HyDE, multi-query | técnicas de otimização; viram "Curiosidade" de 1–2 linhas |
| Memória de chat, reescrita de pergunta, widget | fora do núcleo do RAG |
| Prompt injection, avaliação Hit@k/MRR/LLM-juiz, GraphRAG, checklist de produção | engenharia, não fundamentos |
| DOCX | dependência extra com pouco ganho |

## 3. Framework: stack mínima (sem LangChain/LlamaIndex como espinha)

Versões verificadas no PyPI em 2026-09-23.

| Critério | LangChain 1.x | LlamaIndex 0.14 | **Mínimo (escolhido)** |
|---|---|---|---|
| Ensinar cada etapa separada | boa | fraca (`VectorStoreIndex.from_documents(...).as_query_engine()`) | ótima |
| Células pequenas | boa | média | ótima |
| Transparência | média (retriever/LCEL escondem) | baixa (prompt preenchido só com handler de debug) | total |
| Conceitos do framework a aprender | ~8 | ~9 | ~0 |
| Instalação no Colab | moderada (`langchain` puxa `langgraph`) | pesada (`llama-index-core` tem 29 dependências; o pacote inicial instala integrações OpenAI) | leve (torch/transformers já vêm no Colab) |
| Estabilidade | média (1.0 moveu chains/retrievers para `langchain-classic`; `langchain-community` sem manutenção) | média-baixa (quebras em 0.11, 0.13, 0.14; sem `Settings.embed_model` cai em OpenAI) | alta (APIs de biblioteca) |

**Decisão:** `pypdf` + `RecursiveCharacterTextSplitter` (pacote `langchain-text-splitters`, 1 dependência) +
`sentence-transformers` + `chromadb` + `transformers`. O próprio tutorial oficial do LangChain 1.x deixou de
usar `PyPDFLoader` e lê o PDF com `pypdf`. O único ganho real do LangChain aqui é o splitter, que tem o nome
mais conhecido do mercado. Haystack 3.0 (jul/2026) é transparente, mas centrado em agentes e depende de
`openai`.

## 4. Modelo de embedding

Evidência principal: **MTEB-BR** (jul/2026; 93 modelos, 22 tarefas em PT-BR). "Recup-PT" = média das 6
tarefas de recuperação.

| Modelo | Parâm. | Download | Dims | Prefixo? | Gated? | Licença | Recup-PT / Geral |
|---|---|---|---|---|---|---|---|
| **ibm-granite/granite-embedding-311m-multilingual-r2** | 311M | 623 MB | 768 | não | não | Apache-2.0 | **0,607** / 0,590 |
| BAAI/bge-m3 (alternativa) | 568M | 2,27 GB | 1024 | não | não | MIT | 0,635 / 0,616 |
| granite-embedding-97m-multilingual-r2 (só CPU) | 97M | 195 MB | 384 | não | não | Apache-2.0 | 0,557 / 0,560 |
| intfloat/multilingual-e5-small (notebook anterior) | 118M | 471 MB | 384 | **sim** | não | MIT | 0,507 / 0,561 |
| Qwen/Qwen3-Embedding-0.6B | 596M | 1,19 GB | 1024 | na query | não | Apache-2.0 | 0,603 / 0,623 |
| google/embeddinggemma-300m | 303M | 1,21 GB | 768 | sim | **sim** | Gemma | 0,654 / 0,649 |
| paraphrase-multilingual-MiniLM-L12-v2 | 118M | 471 MB | 384 | não | não | Apache-2.0 | 0,023 / 0,248 |

**Decisão:** granite-r2. Não usa prefixo (acaba com a "pegadinha" do E5, em que esquecer `query:`/`passage:`
piora a busca sem dar erro), recupera ~10 pontos melhor que o e5-small em português, é leve, aberto, não
exige login e é da mesma família do modelo usado no app principal. `max_seq_length = 512` evita uso
excessivo de memória. EmbeddingGemma é o melhor em PT, mas exige login no Hugging Face e não suporta fp16.

## 5. Modelo de linguagem (local, na GPU do Colab)

T4: ~15 GB utilizáveis, compute capability 7.5 (sem bf16 nativo, sem FlashAttention 2).

| Modelo | Parâm. | fp16 | Licença | Gated | Open PT LLM Leaderboard (média · FaQuAD-NLI) | Problema na T4 |
|---|---|---|---|---|---|---|
| **Qwen/Qwen3-4B-Instruct-2507** | 4,0B | 8,0 GB | Apache-2.0 | não | **74,7 · 83,1** | nenhum conhecido; sem modo *thinking* |
| Qwen/Qwen3-1.7B (reserva) | 2,0B | ~4 GB | Apache-2.0 | não | 68,1 · 77,8 | precisa `enable_thinking=False` |
| Gemma 3 4B / GAIA PT-BR 4B | 4,3B | 8,6 GB | Gemma | Gemma: sim | 67,3 / 67,9 | overflow em fp16 (NaN) |
| Qwen3.5-4B | 4,7B | ~9,3 GB | Apache-2.0 | não | — | pensa por padrão; kernels sem suporte oficial na T4 |
| Phi-4-mini | 3,8B | 7,7 GB | MIT | não | 66,5 · 72,9 | — |
| Llama 3.2 3B | 3,2B | 6,4 GB | Llama | sim | 64,8 · 67,0 | login |

| Runtime | Veredito |
|---|---|
| **transformers fp16** | escolhido: já vem no Colab; mostra `.to("cuda")`, memória, template de chat e tokens |
| transformers + bitsandbytes NF4 | desnecessário para 4B; mais lento que fp16 na T4 e +1 conceito |
| llama-cpp-python, vLLM, Ollama no Colab | instalação frágil ou caixa-preta (VRAM fora do `torch`) |

**Decisão:** Qwen3-4B-Instruct-2507 em `float16`, geração com `do_sample=False` e streaming
(`TextStreamer`). Regra de GPU (célula visível na §2): VRAM ≥ 12 GB → 4B; senão → Qwen3-1.7B (na CPU,
em `float32`, com aviso de lentidão). Nunca `bfloat16` na T4. Sem `flash-attn`.

### Orçamento de VRAM estimado (T4) — a confirmar na validação

| Item | GB |
|---|---|
| contexto CUDA + alocador | ~0,5 |
| embedding granite-r2 (fp32) | ~1,2 |
| Qwen3-4B fp16 | 8,05 |
| cache de atenção (~4k tokens) | ~0,6 |
| ativações | 0,5–1,5 |
| **Total** | **~11–12 de 15** |

## 6. Dependências instaladas pelo notebook

`pypdf>=5.0`, `langchain-text-splitters>=0.3`, `sentence-transformers>=5.0`, `chromadb>=1.0`,
`transformers>=4.56` (parâmetro `dtype=` e suporte a Qwen3 e ModernBERT). `torch`, `numpy`, `pandas` e
`matplotlib` já vêm no Colab e **não** são reinstalados.

## 7. Documento de exemplo

Medeiros & Oliveira (2025), *Comparação de Modelos de Embeddings e LLMs para Geração Aumentada por
Recuperação em Português*, SEMISH 2025 — licença CC BY-NC 4.0. É baixado da fonte oficial (SOL/SBC) na hora
da aula, não redistribuído. Por ser em português, recente (o modelo não o conhece) e sobre o próprio tema da
aula, ele serve para mostrar o problema (§2) e a solução (§12). Alternativa automática: Lewis et al. (2020).

## 8. Padrões pedagógicos adotados (de notebooks de referência)

| Padrão | Referência |
|---|---|
| glossário e conceito antes do código; célula de memória da GPU antes de escolher o LLM | [mrdbourke/simple-local-rag](https://github.com/mrdbourke/simple-local-rag) (mediana de 8 linhas por célula) |
| células minúsculas; comparação com × sem retrieval | [HF Cookbook — rag_zephyr_langchain](https://huggingface.co/learn/cookbook/rag_zephyr_langchain) |
| histograma do tamanho dos chunks; imprimir o prompt final | [HF Cookbook — advanced_rag](https://huggingface.co/learn/cookbook/advanced_rag) |
| visão geral primeiro; cosseno calculado "na mão" | [langchain-ai/rag-from-scratch](https://github.com/langchain-ai/rag-from-scratch) |
| id `arquivo:página:chunk` para citar | [pixegami/rag-tutorial-v2](https://github.com/pixegami/rag-tutorial-v2) |
| versões fixadas; nada escondido em módulos externos | [NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques) (como contraexemplo dos helpers) |
| mesma stack, em português | [ramoneirao/llm-projects — RAG sem LangChain](https://github.com/ramoneirao/llm-projects/blob/main/RAG/RAG_sem_LangChain.ipynb) |

Regras resultantes, verificadas por `notebooks/checar_aula.py`: ciclo conceito → analogia → código →
resultado → interpretação; toda célula de código precedida por texto; mediana ≤ 8 e máximo ≤ 15 linhas;
sem API key, provedor externo, Ollama, bitsandbytes ou bf16; sem blocos de trilha avançada.

## Fontes

- PyPI JSON API: langchain, langchain-core, langchain-text-splitters, langchain-community, llama-index,
  llama-index-core, chromadb, sentence-transformers, haystack-ai (consulta em 2026-09-23).
- [LangChain v1 — release notes](https://github.com/langchain-ai/docs/blob/main/src/oss/python/releases/langchain-v1.mdx) ·
  [aviso: langchain-community sem manutenção](https://github.com/langchain-ai/docs/blob/main/src/snippets/oss/langchain-community-unmaintained.mdx) ·
  [tutorial knowledge-base](https://github.com/langchain-ai/docs/blob/main/src/oss/langchain/knowledge-base.mdx)
- [LlamaIndex starter](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/getting_started/starter_example.mdx) ·
  [CHANGELOG](https://github.com/run-llama/llama_index/blob/main/CHANGELOG.md) ·
  [Haystack 3.0](https://haystack.deepset.ai/blog/haystack-3-release)
- [MTEB-BR leaderboard](https://huggingface.co/spaces/MTEB-BR/leaderboard) e [resultados](https://huggingface.co/datasets/MTEB-BR/mteb-pt-results)
- Model cards: [granite-embedding-311m-multilingual-r2](https://hf.co/ibm-granite/granite-embedding-311m-multilingual-r2),
  [bge-m3](https://hf.co/BAAI/bge-m3), [multilingual-e5-small](https://hf.co/intfloat/multilingual-e5-small),
  [Qwen3-4B-Instruct-2507](https://hf.co/Qwen/Qwen3-4B-Instruct-2507), [Qwen3-1.7B](https://hf.co/Qwen/Qwen3-1.7B),
  [Qwen3.5-4B](https://hf.co/Qwen/Qwen3.5-4B), [GAIA PT-BR](https://hf.co/CEIA-UFG/Gemma-3-Gaia-PT-BR-4b-it);
  [EmbeddingGemma blog](https://huggingface.co/blog/embeddinggemma)
- [Open PT LLM Leaderboard](https://hf.co/spaces/eduagarcia/open_pt_llm_leaderboard)
- [transformers #36822 (Gemma 3 em fp16)](https://github.com/huggingface/transformers/issues/36822) ·
  [bitsandbytes #611 (NF4 mais lento)](https://github.com/bitsandbytes-foundation/bitsandbytes/issues/611)
- [Artigo de exemplo — SOL/SBC](https://sol.sbc.org.br/index.php/semish/article/view/36829)
