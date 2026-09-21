# MIG-07 — fluxo real pela UI no corpus pt-br

**Data:** 2026-09-21
**Corpus Oficial:** `artigos_rag_hibrido_a7e480ac787f` (213 chunks, `bge-m3`,
limiar 0,4769). Substitui, para o ensaio, o registro de
[`fluxo-real-ui-2026-09-21.md`](fluxo-real-ui-2026-09-21.md), medido no corpus
anterior de 661 chunks.
**Método:** Streamlit real (`app.py` da branch, porta 8502), navegador da
aplicação, geração real pela NVIDIA (`meta/llama-3.2-11b-vision-instruct`), k = 4
(padrão), sem upload (`UPLOADS_STREAMLIT_HABILITADOS=False`).

Registra só o que a interface mostrou e o log `rag.geracao` do servidor. Não
contém chave, prompt nem texto integral de chunk.

## As quatro perguntas

| # | Cenário | Pergunta | Filtro na UI | O que a UI mostrou | Log (`rag.geracao`) |
|---|---|---|---|---|---|
| 1 | recuperação | "Quais modelos de embeddings tiveram melhor desempenho em RAG para português?" | — | "Não encontrei essa informação nos documentos." · `Classe: recusa` · `Geração: NVIDIA` | NVIDIA, 4 chunks, 1º token 1,08 s, `recusa=True` |
| 2 | citação | "Como a segmentação ancorada e o enriquecimento com pré-contexto otimizam os chunks no domínio jurídico?" | — | Resposta com marcadores `[1]` e `[2]`; **Fontes Citadas (2)** · `brakes2025_rag_juridico.pdf` (p. 4, distância 0,3389, 2025; p. 1, distância 0,4059, 2025) | NVIDIA, 4 chunks, 1º token 0,69 s, `recusa=False` |
| 3 | Recusa | "Qual é a receita de pão de queijo mineiro?" | — | "Não encontrei essa informação nos documentos." · `Classe: sem_resultados`, sem provider | 0 chunks, sem chamada de geração |
| 4 | filtro | "O que é geração aumentada por recuperação?" | Tema: `retrieval`, `avaliacao` | Resposta sem marcador `[n]` · `Classe: fallback` · **Chunks Recuperados (4)**: `rocha2025_ragsft.pdf` (p. 2, 0, 4) e `medeiros2025_embeddings_pt.pdf` (p. 2), todos de 2025 | NVIDIA, 4 chunks, 1º token 0,70 s, `recusa=False` |

## O que ficou provado

- **Streaming, fontes e Recusa pela UI no corpus atual.** A pergunta 2 mostra
  **Fonte Citada** só com marcador válido, com arquivo, página, distância e ano.
  A pergunta 3 recusa sem chamar provider.
- **Fallback nunca vira citação.** Na pergunta 4 a resposta traz referências no
  texto (`[Lewis et al. 2020]`), que não são marcadores `[n]`. A UI classificou
  como `fallback` e listou **Chunks Recuperados**, sem inventar **Fonte Citada**.
- **O filtro de metadados atua na UI.** Com Tema `retrieval` + `avaliacao`, os
  quatro chunks recuperados vêm só de Rocha e Medeiros. O seletor de Idioma não
  existe mais e o de Tema lista os quatro temas do corpus novo.
- **Sem traceback e sem segredo** em nenhuma das quatro interações.
- **Upload segue desativado**, com a mensagem "Upload de PDFs ficará disponível
  após a apresentação."

## Riscos observados

1. **A pergunta de recuperação falhou.** A NVIDIA recusou uma pergunta cujo
   retrieval é 100% do artigo certo. Somando esta execução, a matriz
   ([`matriz-pt-br`](../matriz-pt-br/README.md)) e uma sonda direta, a pergunta
   deu **3 Recusas em 6 execuções**. Se ela abrir o ensaio, a demonstração
   começa com uma Recusa indevida.
2. **O filtro não demonstra Fonte Citada** (pergunta 4), como já registrado na
   matriz.
3. **Chunk de resumo aparece como "p. 0".** Um dos chunks da pergunta 4 é o
   resumo do artigo, gravado com `pagina = 0` (`corpus.py`). Não corresponde a
   página do PDF.
4. **Demora do primeiro envio.** A primeira pergunta levou algumas dezenas de
   segundos até o 1º token, e o log mostra a geração terminando só depois da
   carga do `bge-m3` no Ollama. Faça uma pergunta de aquecimento antes do ensaio.
5. **Instância de Streamlit presa.** Uma instância já aberta na porta 8501 por
   outra sessão não respondeu à primeira pergunta (balão vazio por mais de dois
   minutos), enquanto a mesma chamada pelo roteador levava 5 s. A instância nova
   na 8502 funcionou. Não investiguei a causa; reinicie o Streamlit antes do
   ensaio.
