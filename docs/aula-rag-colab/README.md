# Aula prática de RAG no Google Colab

Material para público amplo: um RAG completo, etapa por etapa, executado **inteiramente no runtime do
Google Colab** (GPU T4), sem chave de API. Épico: [#137](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/137).

| Peça | Onde | Como manter |
|---|---|---|
| Notebook da aula | [`notebooks/aula_rag_colab.ipynb`](../../notebooks/aula_rag_colab.ipynb) · [Abrir no Colab](https://colab.research.google.com/github/Roger-Quinelato/webinarioOllamaRAG/blob/main/notebooks/aula_rag_colab.ipynb) | editar [`notebooks/gerar_aula_rag_colab.py`](../../notebooks/gerar_aula_rag_colab.py) e rodar `python notebooks/gerar_aula_rag_colab.py`; nunca editar o `.ipynb` à mão |
| Checagem automática | [`notebooks/checar_aula.py`](../../notebooks/checar_aula.py) | `python notebooks/checar_aula.py` depois de cada mudança (só biblioteca padrão) |
| Slides (27, teoria) | Artifact "Aula prática de RAG" no claude.ai — [link](https://claude.ai/artifact/XMNHKsuN5v58Di9vzWpUS3) | fonte em [`docs/slides/gerar_deck_aula.py`](../slides/gerar_deck_aula.py) (paleta em hex no topo); gera `docs/slides/deck_aula/project/`, que é republicado no mesmo Artifact |
| Identidade visual de referência | [`docs/slides/parte1-rag-python-puro.pdf`](../slides/parte1-rag-python-puro.pdf) | não muda |
| Decisões e benchmarks | [`decisoes.md`](decisoes.md) | atualizar quando trocar modelo, biblioteca ou regra pedagógica |
| Validação no Colab | [`validacao-colab.md`](validacao-colab.md) | roteiro + tabela de registros datados |

## Relação slides → notebook

| Slides | Seção do notebook |
|---|---|
| 1–2 capa e objetivos · 5 RAG em um minuto · 26 mão na massa | §0 Boas-vindas |
| 21 onde a GPU trabalha | §1 Preparar o Colab |
| 3–4 o que um LLM sabe · LLM sozinho × RAG | §2 O problema |
| 7 documentos | §3 Documentos |
| 8–9 chunk · tamanho e sobreposição | §4 Chunking |
| 10–12 embedding · similaridade · modelo | §5 Embeddings |
| 13 banco vetorial | §6 Banco vetorial |
| 14–16 busca semântica · retrieval · quando nada é relevante | §7 Retrieval |
| 17 contexto | §8 Contexto |
| 18–19 prompt · grounding | §9 Prompt |
| 20 geração | §10 Geração |
| 22 citações | §11 Fontes |
| 23 com × sem RAG | §12 Com × sem RAG |
| 6 o caminho completo | §13 Pipeline completo |
| 24–25, 27 limites · glossário · para discutir | §14 Limites e glossário |

## Diferença para o notebook anterior

[`notebooks/rag_com_seus_documentos.ipynb`](../../notebooks/rag_com_seus_documentos.ipynb) continua no
repositório, inalterado: é a versão para quem já programa, com LangChain, provedores remotos (chave de API)
e técnicas avançadas (busca híbrida, reranking, HyDE, avaliação). Seu histórico de decisões está em
[`../roadmap-notebook-publico-chunking-didatica.md`](../roadmap-notebook-publico-chunking-didatica.md).
