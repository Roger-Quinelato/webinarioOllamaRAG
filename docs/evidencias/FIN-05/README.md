# FIN-05 — matriz real dos providers com modelo NVIDIA de instrução

**Data da execução:** 2026-09-21
**Corpus Oficial:** `artigos_rag_hibrido_a280e65e16ee` (661 chunks, `bge-m3`,
limiar de distância 0,51)
**Base Ativa em todos os cenários:** Corpus Oficial
**Branch:** `fix/fin-03-ordem-providers`

## Limites do registro

Registra só metadados: status, classe de fontes, arquivo e página citados,
provider, tempo até o primeiro token e tempo total. Não contém chave, prompt nem
texto de resposta ou de chunk. Conferi que nenhuma chave de `secrets.toml` aparece
em [`matriz-real-2026-09-21.jsonl`](matriz-real-2026-09-21.jsonl).
Reprodução: `python docs/evidencias/FIN-05/medir_fin05.py` a partir da raiz, com
Ollama ativo e chaves em `.streamlit/secrets.toml`.

## Modelos

| Provider | Modelo |
|---|---|
| NVIDIA | `meta/llama-3.2-11b-vision-instruct` |
| Gemini | `gemini-3.5-flash` |
| OpenAI | `gpt-5.6-luna` |

## Matriz

As perguntas foram validadas antes, só com retrieval, sem geração:

| Cenário | Pergunta | Retrieval validado | Esperado |
|---|---|---|---|
| recuperação | "Como o modelo RAG combina o retriever DPR com o gerador BART?" | 5/5 chunks de `lewis2020_rag.pdf` | citar `lewis2020_rag.pdf` |
| citação | "Quais métricas o Ragas usa para avaliar fidelidade e relevância?" | 5/5 de `es2023_ragas.pdf` | citar `es2023_ragas.pdf` |
| Recusa | "Qual é a receita de pão de queijo mineiro?" | 0 chunks | **Recusa** sem chamar geração |
| filtro | "O que é Dense Passage Retrieval (DPR)?" com `ano >= 2023` | 5/5 de `gao2023_survey.pdf`; Karpukhin (2020) excluído | citar só fontes de 2023 |

Duas perguntas da medição de 2026-09-20 foram trocadas:

- A pergunta antiga de recuperação ("arquitetura RAG proposta por Lewis et
  al.?") não recupera nenhum chunk de Lewis (FIN-01). As 3 **Recusas** do Gemini
  naquela medição vieram dessa pergunta, não de falha do provider.
- O filtro antigo `ano >= 2020` e `idioma = en` não exclui nada, pois todo o
  corpus é de 2020 em diante. Ele devolvia o mesmo resultado sem filtro.

## Resultado por provider isolado

Três repetições por cenário, e uma na Recusa, que não chama geração.

| Provider | Sucesso | Fonte esperada citada | Tempo até o 1º token (típico) | Observações |
|---|---:|---:|---|---|
| NVIDIA | 9/9 | 6/9 | 0,7–1,1 s; 5,5 s na 1ª chamada | Nas outras 3 respostas (uma por cenário), o texto veio sem marcador válido e foi classificado como **fallback**, não como citação. |
| Gemini | 8/9 | 6/9 | 4–9 s; 37–61 s nas 1ªs chamadas | Recuperação e citação: 6/6 citadas. Filtro: 2 **Recusas** diante do contexto mais fraco (distâncias de 0,46 a 0,51) e 1 HTTP 503. |
| OpenAI | 0/3 | — | — | HTTP 429 em todas, por falta de saldo (FIN-03). |

A **Recusa** saiu correta nos três providers, sem chamar a geração (0,1–0,2 s).
Nenhuma resposta citou fonte fora do filtro.

## Cadeia canônica NVIDIA → Gemini → OpenAI

| Cenário | Provider | Resultado | 1º token |
|---|---|---|---|
| recuperação | NVIDIA | citou `lewis2020_rag.pdf` p. 2 | 10,39 s (1ª chamada) |
| citação | NVIDIA | citou `es2023_ragas.pdf` p. 5 | 2,81 s |
| Recusa | — | **Recusa** sem geração | 0,10 s total |
| filtro | NVIDIA | **fallback**, sem marcador válido | 0,79 s |

Nenhum cenário precisou de fallback de provider.

## Incidente de configuração

A primeira rodada da NVIDIA deu HTTP 404 em todas as chamadas.
`NVIDIA_BASE_URL` estava como `https://integrate.api.nvidia.com/v1/chat/completions`,
a URL completa do exemplo do catálogo. O SDK acrescenta `/chat/completions`
por conta própria, então o caminho ficava duplicado. Com
`https://integrate.api.nvidia.com/v1`, as chamadas funcionaram. As linhas
dessa rodada foram descartadas. A cadeia daquela rodada caiu no Gemini, o que
confirmou o fallback: os 3 cenários com geração concluíram pelo Gemini.

## Conclusão

- **FIN-05:** o modelo de instrução resolve a lentidão. O primeiro token caiu de
  20–29 s (modelo de *reasoning*, 2026-09-20) para menos de 1,1 s depois da
  chamada inicial, com 9/9 de disponibilidade.
- **FIN-03 / ADR-004:** a ordem padrão NVIDIA → Gemini → OpenAI se confirma. A
  NVIDIA é a mais rápida e a mais disponível. O Gemini cita com mais disciplina,
  mas teve 503 e latência alta na primeira chamada.
- **Risco para o ensaio:** a NVIDIA respondeu sem marcador em 3 de 9 casos. A
  UI mostra isso como **fallback**, sem inventar citação. Esse comportamento
  segue a regra, mas pode enfraquecer a demonstração de citação.
