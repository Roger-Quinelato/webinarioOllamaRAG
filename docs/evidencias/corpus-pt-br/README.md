# Corpus Oficial só em português — reindexação e calibração

**Data:** 2026-09-21
**Decisão:** do autor, em chat. Saem os seis artigos em inglês e entram dois
artigos em português com temas que o corpus ainda não tinha.
**Branch:** `feat/corpus-pt-br`

## Corpus

| Arquivo | Artigo | Tema | Ano | Chunks |
|---|---|---|---:|---:|
| `rocha2025_ragsft.pdf` | Olivera et al., SBBD 2025: ajuste fino sequencial de modelos pequenos para RAG | retrieval | 2025 | 54 |
| `medeiros2025_embeddings_pt.pdf` | Medeiros & Oliveira, SEMISH 2025: comparação de embeddings e LLMs para RAG em português | avaliacao | 2025 | 50 |
| `brakes2025_rag_juridico.pdf` | Brakes et al., ERI-GO 2025: RAG jurídico com segmentação ancorada e filtros estruturados | aplicacoes (novo) | 2025 | 38 |
| `xavier2024_rag_grafos.pdf` | Xavier & Soares, Minicursos do SBBD 2024: RAG em grafos de conhecimento | fundamentos | 2024 | 71 |

Saíram `lewis2020_rag.pdf`, `karpukhin2020_dpr.pdf`, `gao2023_survey.pdf`,
`es2023_ragas.pdf`, `asai2023_selfrag.pdf` e `liu2023_lost_middle.pdf`.
`config.TEMAS` passou a `fundamentos, retrieval, avaliacao, aplicacoes`, só com
temas presentes. `config.IDIOMAS` passou a `pt`, e a UI deixou de ter o seletor
de Idioma.

## Reindexação

`python scripts/02_indexar_hibrido.py`, com CPU apenas:

| Campo | Valor |
|---|---|
| Coleção nova | `artigos_rag_hibrido_a7e480ac787f` (`ready`, `bge-m3-v1`, dimensão 1024) |
| Chunks | 213, com 213 embeddings gerados |
| Duração | 510,7 s |
| Integridade | 0 vazios, 0 com menos de 100 caracteres, 0 `U+FFFD`, 0 com menos de 50% de letras, 0 duplicados; idioma `pt` em 213/213 |

## Calibração do limiar

`python scripts/calibrar_retrieval_hibrido.py` →
[`calibracao.json`](calibracao.json). As 7 perguntas positivas recuperaram o
artigo esperado no top 1.

| | Distância |
|---|---:|
| Maior positiva | 0,3738 ("O que é geração aumentada por recuperação?", pergunta genérica) |
| Menor negativa | 0,5800 ("Como trocar o óleo de um carro?") |
| **Novo limiar** (`DISTANCIA_MAXIMA_RETRIEVAL`) | **0,4769**, com margem de 0,103 para cada lado |
| Limiar anterior | 0,5100 |

## Rollback

A coleção anterior (`artigos_rag_hibrido_a280e65e16ee`, 661 chunks e 8 artigos)
continua no Chroma, e nenhuma coleção foi apagada. Para voltar:

1. Restaurar em `chroma_db/hybrid_manifest.json` o conteúdo de
   [`manifesto-anterior.json`](manifesto-anterior.json).
2. Reverter `config.py` (`ARTIGOS_CORPUS`, `TEMAS`, `IDIOMAS` e
   `DISTANCIA_MAXIMA_RETRIEVAL = 0.5100454390048981`) e `metadados.csv`.
3. Recolocar os PDFs em inglês em `artigos/` com
   `python scripts/01_preparar_corpus.py`.

## Pendências

- As evidências de [FIN-05](../FIN-05/README.md) e
  [MIG-07](../MIG-07/fluxo-real-ui-2026-09-21.md) usam perguntas do corpus
  anterior e agora são históricas. A matriz de quatro perguntas do ensaio
  precisa ser refeita com o corpus novo.
- Os PDFs em inglês continuam em `artigos/` até o autor removê-los. Com eles
  na pasta, `rag.validar_metadados` acusa "PDF sem linha no CSV". A indexação
  não os usa, porque lê o `metadados.csv`.
