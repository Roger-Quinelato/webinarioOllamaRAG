from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parents[1]
celulas = []


def md(texto):
    """Descreve md."""
    celulas.append(nbf.v4.new_markdown_cell(texto.strip()))


def code(texto):
    """Descreve code."""
    celulas.append(nbf.v4.new_code_cell(texto.strip()))


md("""
# Construindo um Assistente com RAG, Ollama e Streamlit
**Webinário CIIA — Encontro 2** · Roger Quinelato (condução) · João Victor Rikio Enomoto (suporte)

| Bloco | Conteúdo | Min |
|---|---|---|
| 1 | Recapitulando o pipeline RAG + ambiente | 10 |
| 2 | Indexação: PDFs → chunks → embeddings → ChromaDB (+ metadados com LLM) | 18 |
| 3 | Retrieval top-k na prática: k, distâncias, filtros, cross-lingual | 15 |
| 3b | Busca em dois estágios: resumos → chunks | 7 |
| 4 | SHAP: explicando o retrieval | 12 |
| 5 | Prompt augmentation: respostas com e sem contexto | 12 |
| 6 | Integração com LLM local usando Ollama | 12 |
| 7 | Construção do chatbot com Streamlit | 15 |
| 8 | Avaliação (RAGAS), reranking e próximos passos | 8 |

> Antes de rodar: siga o `README.md` (Ollama, modelos, `.venv`). Toda etapa lenta tem uma **saída pré-computada**
> em `resultados/`; as chaves abaixo decidem se a célula roda ao vivo ou só carrega o resultado salvo.
""")

code("""
import json
import sys
import time
import warnings
from pathlib import Path

import pandas as pd
from IPython.display import HTML, Markdown, display

RAIZ = Path.cwd()
sys.path.insert(0, str(RAIZ))
import config
import rag

REINDEXAR = False        # True: apaga e recria a coleção — 1420 s (23,7 min) medidos nesta máquina
LLM_AO_VIVO = True       # False: usa as respostas salvas em resultados/
SHAP_AO_VIVO = True      # False: mostra o gráfico SHAP salvo em resultados/

warnings.filterwarnings("ignore", message="IProgress not found")
pd.set_option("display.max_colwidth", 120)


def tabela(resultados, colunas=("posicao", "distancia", "arquivo", "pagina", "ano", "tema", "idioma", "texto")):
    if not resultados:
        return pd.DataFrame(columns=list(colunas))
    df = pd.DataFrame(resultados)[list(colunas)]
    if "texto" in df:
        df["texto"] = df["texto"].str.slice(0, 110) + "…"
    return df.round({"distancia": 4})


def carregar_resultado(nome):
    return json.loads((config.PASTA_RESULTADOS / nome).read_text(encoding="utf-8"))
""")

md("""
## Bloco 1 — Recapitulando o pipeline RAG

```
PDFs ──► texto por página ──► chunks ──► embeddings (bge-m3) ──► ChromaDB
                                                                     │
pergunta ──► embedding ──► top-k (+ filtros de metadados) ◄──────────┘
                              │
                              ▼
               prompt = instruções + trechos + pergunta ──► LLM (qwen2.5) ──► resposta com fontes
```

Tudo roda **localmente**: o Ollama serve o modelo de embedding e o modelo de chat; o ChromaDB guarda os vetores em disco.
""")

code("""
instalados, faltando = rag.verificar_ollama([config.MODELO_EMBEDDING, config.MODELO_CHAT, config.MODELO_CHAT_PLANO_B])
print("Modelos no Ollama:", sorted(instalados))
print("Faltando:", faltando or "nenhum")
print("Embedding:", config.MODELO_EMBEDDING, "| Chat:", config.MODELO_CHAT, "| Plano B:", config.MODELO_CHAT_PLANO_B)
""")

md("""
## Bloco 2 — Indexação

### 2.1 Corpus e metadados escritos à mão
Os PDFs não vêm no repositório: `scripts/01_preparar_corpus.py` baixa cada um do arXiv para `arquivosPDF/artigos/`.

| Arquivo | Artigo |
|---|---|
| `lewis2020_rag.pdf` | Lewis et al. (2020) — https://arxiv.org/abs/2005.11401 |
| `karpukhin2020_dpr.pdf` | Karpukhin et al. (2020) — https://arxiv.org/abs/2004.04906 |
| `gao2023_survey.pdf` | Gao et al. (2023) — https://arxiv.org/abs/2312.10997 |
| `es2023_ragas.pdf` | Es et al. (2023) — https://arxiv.org/abs/2309.15217 |
| `asai2023_selfrag.pdf` | Asai et al. (2023) — https://arxiv.org/abs/2310.11511 |
| `liu2023_lost_middle.pdf` | Liu et al. (2023) — https://arxiv.org/abs/2307.03172 |

Metadado é **decisão de engenharia**: escolhemos campos que viram filtros úteis na busca (`ano`, `tema`, `idioma`).
""")

code("""
metadados = rag.carregar_metadados()
pd.DataFrame(metadados)[["arquivo", "titulo", "ano", "veiculo", "tema", "idioma"]]
""")

md("""
### 2.2 Do PDF ao chunk
Chunking **por página**; páginas longas são subdivididas em pedaços de `TAMANHO_CHUNK` caracteres com `SOBREPOSICAO`
para que uma frase cortada no fim de um chunk apareça inteira no próximo.
""")

code("""
paginas = rag.extrair_paginas(config.PASTA_ARTIGOS / "lewis2020_rag.pdf")
print(f"{len(paginas)} páginas; página 3 tem {len(paginas[2])} caracteres")
pedacos = rag.dividir_texto(paginas[2])
for i, pedaco in enumerate(pedacos):
    print(f"chunk {i}: {len(pedaco)} caracteres | início: {pedaco[:70]!r}")
print("\\nSobreposição entre chunk 0 e chunk 1:")
print("  fim do 0:   …", pedacos[0][-config.SOBREPOSICAO:])
print("  início do 1:", pedacos[1][:config.SOBREPOSICAO], "…")
""")

code("""
chunks = rag.gerar_chunks()
contagem = pd.DataFrame([c["metadados"] for c in chunks]).groupby(["arquivo", "tipo_chunk"]).size().unstack(fill_value=0)
print(f"{len(chunks)} chunks no total")
contagem
""")

md("""
### 2.3 Embeddings + ChromaDB
Cada chunk vira um vetor gerado pelo `bge-m3` (multilíngue) e é gravado com seus metadados.
""")

# hazard (achado A3-03, T31): a condição desta célula era
# `if REINDEXAR or colecao.count() != len(chunks)`, e o `or` fazia REINDEXAR = False NÃO impedir a
# reindexação — bastava a contagem divergir para o notebook gastar 1420 s (23,7 min) ao vivo, no
# bloco 2, sob transmissão. Agora quem autoriza reindexar é a chave, e só ela; divergência de
# contagem é aviso. O comentário fica aqui, no gerador, e não dentro da célula: a célula é projetada
# ao vivo e não é lugar de narrar o histórico do bug.
# hazard: avisar e seguir não basta — com o índice defasado, o `colecao.get()` abaixo pode voltar
# vazio e a célula morreria num IndexError opaco logo depois do aviso, trocando 24 min por um crash.
# Por isso a amostra é conferida antes de ser usada.
code("""
colecao = rag.abrir_colecao()
if REINDEXAR:
    inicio = time.perf_counter()
    colecao = rag.indexar(chunks)
    print(f"Indexação em {time.perf_counter() - inicio:.0f}s")
elif colecao.count() != len(chunks):
    print(f"[AVISO] a coleção tem {colecao.count()} vetores e os PDFs geram {len(chunks)} chunks.\\n"
          f"        O índice está defasado, mas NÃO vou reindexar agora (leva ~24 min em CPU).\\n"
          f"        Rode `python scripts/02_indexar.py` fora da aula, ou ponha REINDEXAR = True acima.")

amostra = colecao.get(ids=["es2023_ragas-p001-c00"], include=["metadatas", "embeddings"])
if not amostra["ids"]:
    print(f"{colecao.count()} vetores | o chunk de exemplo não está no índice — reindexe fora da aula")
    metadados_amostra = {}
else:
    print(f"{colecao.count()} vetores | dimensão {len(amostra['embeddings'][0])}")
    metadados_amostra = amostra["metadatas"][0]
{k: (v[:80] + "…" if isinstance(v, str) and len(v) > 80 else v) for k, v in metadados_amostra.items()}
""")

md("""
### 2.4 E se o LLM preenchesse os metadados?
Alternativa ao CSV manual: pedir ao LLM um JSON a partir da 1ª página. Comparamos campo a campo com o CSV.
""")

code("""
artigo = "es2023_ragas.pdf"
if LLM_AO_VIVO:
    primeira = rag.extrair_paginas(config.PASTA_ARTIGOS / artigo, limpar=False)[0]
    manual = next(m for m in metadados if m["arquivo"] == artigo)
    inicio = time.perf_counter()
    comparacao = rag.comparar_metadados(manual, rag.extrair_metadados_llm(primeira))
    print(f"Extração em {time.perf_counter() - inicio:.1f}s")
else:
    comparacao = carregar_resultado("metadados_llm.json")["comparacao"]
pd.DataFrame(comparacao)
""")

md("""
### 2.5 Resumo do abstract gerado pelo LLM
O campo `resumo` do CSV foi gerado assim (no idioma do artigo) e também é indexado como um chunk próprio
(`tipo_chunk = "resumo"`), usado na busca em dois estágios.
""")

code("""
primeira = rag.extrair_paginas(config.PASTA_ARTIGOS / "liu2023_lost_middle.pdf", limpar=False)[0]
abstract = rag.extrair_abstract(primeira)
print("ABSTRACT:", abstract[:600], "…\\n")
if LLM_AO_VIVO:
    inicio = time.perf_counter()
    resumo = rag.resumir_abstract(abstract, "en")
    print(f"RESUMO AO VIVO ({time.perf_counter() - inicio:.1f}s):", resumo)
print("\\nRESUMO NO CSV:", next(m["resumo"] for m in metadados if m["arquivo"] == "liu2023_lost_middle.pdf"))
""")

md("""
## Bloco 3 — Retrieval top-k na prática
A distância é **cosseno** (0 = idêntico). Observe como a lista cresce com `k` e onde entram trechos menos relevantes.
""")

code("""
pergunta = "Quais métricas o Ragas usa para avaliar um pipeline de RAG?"
for k in (1, 4, 8):
    display(Markdown(f"**k = {k}**"), tabela(rag.buscar(pergunta, k=k, colecao=colecao)))
""")

md("### 3.1 Filtros de metadados (`where`)")

code("""
pergunta = "Como funciona a recuperação de passagens?"
for nome, filtro in {
    "sem filtro": None,
    "ano >= 2023": {"ano": {"$gte": 2023}},
    "tema = retrieval": {"tema": "retrieval"},
    "idioma = pt": {"idioma": "pt"},
}.items():
    display(Markdown(f"**{nome}** `{filtro}`"), tabela(rag.buscar(pergunta, k=4, where=filtro, colecao=colecao)))
""")

md("""
### 3.2 Cross-lingual
Corpus majoritariamente em inglês (6 artigos) + 2 em português: o `bge-m3` coloca as duas línguas no
mesmo espaço vetorial, então uma pergunta em português também recupera bem os trechos em inglês.
""")

code("""
for texto in ("O desempenho cai quando a informação relevante está no meio de um contexto longo?",
              "Does performance drop when relevant information is in the middle of a long context?"):
    display(Markdown(f"**{texto}**"), tabela(rag.buscar(texto, k=3, colecao=colecao)))
""")

md("""
## Bloco 3b — Busca em dois estágios
1. Busca só nos chunks de **resumo** e escolhe os `N_ARTIGOS_ESTAGIO_1` artigos mais próximos.
2. Busca os chunks de página **só dentro desses artigos** (`where={"arquivo": {"$in": [...]}}`).
""")

code("""
def comparar_buscas(pergunta):
    display(Markdown(f"### {pergunta}\\n**Busca simples**"), tabela(rag.buscar(pergunta, k=4, colecao=colecao)))
    dois = rag.buscar_dois_estagios(pergunta, k=4, colecao=colecao)
    display(Markdown(f"**Estágio 1 — artigos escolhidos** ({dois['caminho']})"),
            tabela(dois["artigos"], colunas=("posicao", "distancia", "arquivo", "titulo")))
    display(Markdown("**Estágio 2 — chunks desses artigos**"), tabela(dois["resultados"]))


comparar_buscas("Como avaliar se a resposta é fiel ao contexto recuperado?")
""")

md("""
Quando o estágio 1 **ajuda**: o top-4 fica concentrado no artigo certo (Ragas). Agora um caso em que ele **atrapalha**:
o resumo do *Lost in the Middle* não fala em "mais documentos", então o artigo não passa no estágio 1.
""")

code("""
comparar_buscas("Recuperar mais documentos sempre melhora a resposta do modelo?")
""")

md("""
## Bloco 4 — SHAP: explicando o retrieval

> ⚠️ Aqui explicamos o **retrieval**: quais palavras da pergunta aproximam o vetor da pergunta do vetor de um chunk.
> **Não** é uma explicação do raciocínio do LLM.

A função explicada é `similaridade_cosseno(embedding(pergunta mascarada), embedding(chunk))`. O SHAP mascara palavras
da pergunta e mede quanto a similaridade muda.
""")

code("""
import shap

pergunta = "Quais métricas o Ragas usa para avaliar fidelidade e relevância das respostas?"
chunk = rag.buscar(pergunta, k=1, colecao=colecao)[0]
print(f"Chunk explicado: {chunk['arquivo']} p.{chunk['pagina']} (similaridade {chunk['similaridade']:.4f})")
if SHAP_AO_VIVO:
    inicio = time.perf_counter()
    explicacao, funcao = rag.explicar_similaridade(pergunta, chunk["texto"])
    print(f"SHAP em {time.perf_counter() - inicio:.0f}s")
    base, soma, real = explicacao.base_values[0], explicacao.values[0].sum(), funcao([pergunta])[0]
    print(f"base {base:.4f} + soma dos SHAP {soma:+.4f} = {base + soma:.4f} | similaridade real {real:.4f}")
    shap.plots.text(explicacao[0])
else:
    salvo = carregar_resultado("shap_similaridade_chunk1.json")
    print(f"base {salvo['base']:.4f} + soma {sum(salvo['valores']):+.4f} | similaridade real {salvo['similaridade_real']:.4f}")
    display(HTML((config.PASTA_RESULTADOS / "shap_similaridade_chunk1.html").read_text(encoding="utf-8")))
""")

md("""
### 4.1 Shapley dos chunks sobre a resposta (pré-computado)
Para cada subconjunto dos k chunks geramos uma resposta e medimos a similaridade com a resposta que usa todos
(2^k gerações — muito lento para ao vivo). O valor de Shapley de cada chunk é sua contribuição média.
Gerado por `opcional/calcular_shapley_chunks.py`.
""")

code("""
shapley = carregar_resultado("shapley_chunks.json")
print("Pergunta:", shapley["pergunta"], "| modelo:", shapley["modelo"])
print(f"v(nenhum chunk) = {shapley['valor_sem_chunks']:.4f} | v(todos) = {shapley['valor_com_todos']:.4f}")
pd.DataFrame(shapley["contribuicoes"]).round(4)
""")

md("""
## Bloco 5 — Prompt augmentation: com e sem contexto
O prompt enriquecido tem duas mensagens: **system** com as instruções (português, só os trechos, citar `[n]`,
responder "não encontrei" quando faltar informação) e **user** com os trechos numerados com fonte + a pergunta.
Com um modelo pequeno (3B), separar as instruções na mensagem de sistema fez diferença: com tudo numa mensagem só,
ele às vezes respondia em inglês ou recusava perguntas que os trechos respondiam.
""")

code("""
# TODO(autor): trocar pela pergunta-teste definitiva.
pergunta = "Quais são os tokens de reflexão (reflection tokens) propostos no Self-RAG?"
resultados = rag.buscar(pergunta, k=config.K_PADRAO, colecao=colecao)
print(rag.formatar_mensagens(rag.montar_mensagens(pergunta, resultados))[:1800], "\\n[…]")
""")

code("""
if LLM_AO_VIVO:
    sem = rag.gerar_texto(rag.montar_mensagens(pergunta))
    com = rag.gerar_texto(rag.montar_mensagens(pergunta, resultados))
else:
    salvo = next(r for r in carregar_resultado("com_sem_contexto.json") if r["pergunta"] == pergunta)
    sem, com = salvo["sem_contexto"], salvo["com_contexto"]
# why: mostrar todo o top-k como "Fontes" mistura o que entrou no prompt com o que a resposta de
# fato citou (achado 6.5) — rag.fontes_da_resposta() só lista os [n] citados (ou nenhuma, em
# recusa ou sem resultados); os trechos recuperados ficam à parte, já que são "o que foi
# oferecido ao modelo", não "o que ele usou". Usa fontes_da_resposta()+formatar_fontes() direto,
# não rag.montar_bloco_fontes() — que embute o rótulo/formato "\\n\\nFontes:\\n" pronto para o
# streaming de responder(), formato interno que este bloco não deveria precisar desmontar.
citadas = rag.fontes_da_resposta(com, resultados)
if citadas:
    indices, resultados_citados = zip(*citadas)
    fontes_citadas = rag.formatar_fontes(list(resultados_citados), list(indices))
else:
    fontes_citadas = "nenhuma"
display(Markdown(f"### Sem contexto\\n{sem}\\n\\n### Com contexto\\n{com}\\n\\n"
                 f"**Fontes citadas**\\n```\\n{fontes_citadas}\\n```\\n\\n"
                 f"**Trechos enviados ao prompt**\\n```\\n{rag.formatar_fontes(resultados)}\\n```"))
""")

md("Respostas salvas das outras perguntas-teste (geradas por `scripts/06_com_sem_contexto.py`):")

code("""
pd.DataFrame(carregar_resultado("com_sem_contexto.json"))[["pergunta", "sem_contexto", "com_contexto"]]
""")

md("""
## Bloco 6 — Integração com LLM local usando Ollama
`rag.responder()` busca a resposta em **streaming** e acrescenta as fontes. Para trocar para o plano B, mude
`MODELO_CHAT` em `config.py` (ou passe `modelo=config.MODELO_CHAT_PLANO_B`).
""")

code("""
pergunta = "Como o Self-RAG decide quando buscar documentos?"
resultados_bloco6 = rag.buscar(pergunta, colecao=colecao)
salva = config.PASTA_RESULTADOS / "resposta_bloco6.md"
if LLM_AO_VIVO:
    inicio = time.perf_counter()
    saida, texto = display(Markdown("…"), display_id=True), ""
    for pedaco in rag.responder(pergunta, resultados_bloco6):
        texto += pedaco
        saida.update(Markdown(texto))
    print(f"[{time.perf_counter() - inicio:.1f}s com {config.MODELO_CHAT}]")
    salva.write_text(texto, encoding="utf-8")
else:
    display(Markdown(salva.read_text(encoding="utf-8")))
# why: rag.responder() já cita só as fontes usadas (achado 6.5); aqui mostramos também os trechos
# recuperados que foram oferecidos ao modelo, separados e rotulados, para não confundir os dois.
display(Markdown(f"**Trechos enviados ao prompt**\\n```\\n{rag.formatar_fontes(resultados_bloco6)}\\n```"))
""")

md("""
## Bloco 7 — Chatbot com Streamlit
O app reaproveita as mesmas funções de `rag.py`. No terminal, com o `.venv` ativo:

```bash
streamlit run app.py
```
""")

code("""
display(Markdown("```python\\n" + (RAIZ / "app.py").read_text(encoding="utf-8") + "\\n```"))
""")

md("""
## Bloco 8 — Avaliação, reranking e próximos passos
- **RAGAS** (Es et al., 2023): avalia sem resposta de referência — *faithfulness* (a resposta é sustentada pelo
  contexto?), *answer relevancy* (responde à pergunta?) e *context relevance/precision* (os trechos ajudam?).
  `opcional/avaliacao_estilo_ragas.py` implementa essas três ideias com o próprio Ollama como juiz.
- **Reranking**: recuperar top-20 barato e reordenar com um *cross-encoder* antes de mandar top-4 ao LLM.
- **Lost in the Middle** (Liu et al., 2023): mais k nem sempre é melhor — posição do trecho no prompt importa.
- **Escalabilidade**: índices maiores, busca híbrida (BM25 + vetores), cache de embeddings, servidores dedicados.
""")

code("""
arquivo = config.PASTA_RESULTADOS / "avaliacao_estilo_ragas.json"
if arquivo.exists():
    display(pd.DataFrame(carregar_resultado(arquivo.name))[["pergunta", "fidelidade", "relevancia_resposta", "precisao_contexto"]].round(2))
else:
    print("Rode opcional/avaliacao_estilo_ragas.py para gerar o resultado.")
""")

notebook = nbf.v4.new_notebook(cells=celulas)
notebook.metadata["kernelspec"] = {"name": "webinario-rag", "display_name": "Python (webinario-rag)", "language": "python"}
destino = RAIZ / "webinario_rag.ipynb"
nbf.write(notebook, destino)
print(f"{len(celulas)} células escritas em {destino}")
