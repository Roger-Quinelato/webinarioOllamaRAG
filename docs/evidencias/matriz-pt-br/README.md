# Matriz de quatro perguntas no corpus pt-br

**Data da execução:** 2026-09-21
**Corpus Oficial:** `artigos_rag_hibrido_a7e480ac787f` (213 chunks, `bge-m3`,
limiar de distância 0,4769). Substitui a matriz de
[FIN-05](../FIN-05/README.md), medida no corpus anterior de 661 chunks.
**Base Ativa em todos os cenários:** Corpus Oficial
**Ordem de providers:** NVIDIA → Gemini → OpenAI (ADR-004)

## Limites do registro

Só metadados: status, classe de fontes, arquivo e página citados, provider,
tempo até o primeiro token e tempo total. Sem chave, prompt ou texto de resposta.
Conferi que nenhum valor de chave de `.streamlit/secrets.toml` aparece nos
arquivos desta pasta. Os nomes de modelo aparecem no campo `modelo`, porque não
são segredo.

Reprodução, a partir da raiz, com Ollama ativo e chaves em `.streamlit/secrets.toml`:

```bash
python docs/evidencias/matriz-pt-br/validar_retrieval.py
python docs/evidencias/matriz-pt-br/medir_matriz.py
python docs/evidencias/matriz-pt-br/medir_matriz.py filtro-tema NVIDIA,cadeia
```

## Modelos

| Provider | Modelo |
|---|---|
| NVIDIA | `meta/llama-3.2-11b-vision-instruct` |
| Gemini | `gemini-3.5-flash` |
| OpenAI | `gpt-5.6-luna` |

## Perguntas e retrieval validado

O retrieval foi validado antes, sem geração
([`retrieval-validado.txt`](retrieval-validado.txt)):

| Cenário | Pergunta | Filtro | Retrieval | Esperado |
|---|---|---|---|---|
| recuperação | "Quais modelos de embeddings tiveram melhor desempenho em RAG para português?" | — | 5/5 de `medeiros2025_embeddings_pt.pdf` | citar `medeiros2025_embeddings_pt.pdf` |
| citação | "Como a segmentação ancorada e o enriquecimento com pré-contexto otimizam os chunks no domínio jurídico?" | — | 5/5 de `brakes2025_rag_juridico.pdf` | citar `brakes2025_rag_juridico.pdf` |
| Recusa | "Qual é a receita de pão de queijo mineiro?" | — | 0 chunks | **Recusa** sem chamar geração |
| filtro (exclusão) | "O que são grafos de conhecimento e como eles se integram ao RAG?" | `ano >= 2025` | sem filtro: 5/5 de Xavier (2024); com filtro: nenhum de Xavier | não citar Xavier; **Recusa** é aceitável |
| filtro (tema) | "O que é geração aumentada por recuperação?" | `tema` em `avaliacao`, `retrieval` | sem filtro: 5 chunks de 4 artigos; com filtro: só Rocha e Medeiros | só essas fontes |

## Resultado por provider isolado

Três repetições por cenário; a Recusa roda uma vez porque não chama geração.

| Provider | Cenário | Resultado | 1º token |
|---|---|---|---|
| NVIDIA | recuperação | 2 citadas (`medeiros2025_embeddings_pt.pdf`), 1 **Recusa** | 2,9–20,9 s |
| NVIDIA | citação | 3/3 citadas (`brakes2025_rag_juridico.pdf`) | 2,2–8,1 s |
| NVIDIA | Recusa | **Recusa** sem geração | 0,1 s total |
| NVIDIA | filtro (exclusão) | 3/3 **Recusa** | 0,8–3,7 s |
| NVIDIA | filtro (tema) | 3/3 **fallback**, sem marcador válido | 2,9–9,0 s |
| Gemini | recuperação | 1 citada; 2 HTTP 429 | 113,8 s |
| Gemini | citação | 1 citada; 2 HTTP 429 | 89,4 s |
| Gemini | Recusa | **Recusa** sem geração | 0,2 s total |
| Gemini | filtro (exclusão) | 3/3 HTTP 429 | — |
| OpenAI | recuperação, citação, filtro | 3/3 HTTP 429 | — |
| OpenAI | Recusa | **Recusa** sem geração | 0,1 s total |

## Cadeia canônica NVIDIA → Gemini → OpenAI

| Cenário | Provider | Resultado | 1º token |
|---|---|---|---|
| recuperação | NVIDIA | citou `medeiros2025_embeddings_pt.pdf` | 23,7 s (1ª chamada) |
| citação | NVIDIA | citou `brakes2025_rag_juridico.pdf` | 3,9 s |
| Recusa | — | **Recusa** sem geração | 2,1 s total |
| filtro (exclusão) | NVIDIA | **Recusa** | 1,2 s |
| filtro (tema) | NVIDIA | **fallback**, sem marcador válido | 3,0 s |

Nenhum cenário precisou de fallback de provider. Nenhum cenário citou fonte
fora do filtro.

## Conclusão

- **Aprovado:** o retrieval separa bem os artigos do corpus novo, a **Recusa**
  saiu correta nos três providers, e os filtros mudam de fato o que é
  recuperado. A ordem NVIDIA → Gemini → OpenAI funciona: a NVIDIA respondeu
  todas as perguntas sem precisar de fallback.
- **Risco 1, citação no filtro:** no cenário de filtro por tema, a NVIDIA
  respondeu 4 de 4 vezes sem marcador `[n]`. A UI mostra **Chunks Recuperados**
  como fallback, sem inventar **Fonte Citada**. Nos cenários de recuperação e
  citação a NVIDIA citou 5 de 6 vezes. Para a demonstração de citação, use as
  perguntas de recuperação e citação.
- **Risco 2, Gemini indisponível por cota:** 7 de 9 chamadas responderam HTTP 429
  e, quando responderam, o 1º token levou 89 a 114 s. Na prática, o Gemini não
  cobre uma falha da NVIDIA durante o ensaio até a cota normalizar.
- **Risco 3, latência da NVIDIA:** o 1º token variou de 0,8 a 20,9 s (mediana
  3,3 s), acima dos menos de 1,1 s de [FIN-05](../FIN-05/README.md). A primeira
  chamada é a mais lenta. Faça uma pergunta de aquecimento antes do ensaio.
- **Pendente:** a OpenAI segue em HTTP 429 (saldo), o que mantém a #70 bloqueada.
  A pergunta de upload não entra, pois `UPLOADS_STREAMLIT_HABILITADOS=False`.
- **Registro da primeira rodada:** o cenário "filtro" desta rodada usou a
  pergunta de exclusão e devolveu **Recusa**, por isso foi acrescentado o
  cenário "filtro (tema)", executado em separado só para NVIDIA e cadeia, para
  poupar a cota do Gemini.
- **Atualização, mesma data:** o fluxo pela UI real está em
  [`../MIG-07/fluxo-real-ui-pt-br-2026-09-21.md`](../MIG-07/fluxo-real-ui-pt-br-2026-09-21.md).
  A pergunta de recuperação deu **Recusa** também na UI e em uma sonda direta:
  com a matriz, são 3 Recusas em 6 execuções da NVIDIA, embora o retrieval seja
  5/5 do artigo certo. Para abrir o ensaio com citação, prefira a pergunta de
  citação (5 de 5 citadas, somando matriz, cadeia e UI).
- **Modelos alternativos da NVIDIA, testados e descartados:** os modelos de
  instrução da listagem `/models` não respondem nesta conta (HTTP 410 ou 404) e
  `meta/llama-3.2-90b-vision-instruct` não terminou em 100 s. Ver
  [`../MIG-05/gate-cto-2026-09-21.md`](../MIG-05/gate-cto-2026-09-21.md).
