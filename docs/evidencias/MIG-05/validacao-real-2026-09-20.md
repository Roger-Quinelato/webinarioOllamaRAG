# MIG-05 — validação real dos providers remotos

**Data da execução:** 2026-09-20
**Corpus Oficial:** `artigos_rag_hibrido_a280e65e16ee` (`ready`, 661 chunks,
`bge-m3`, dimensão 1024)
**Base Ativa em todos os cenários:** Corpus Oficial

## Limites do registro

Esta evidência registra metadados operacionais. Não contém chave, prompt
integral nem conteúdo de documento. As chamadas usaram credenciais locais, lidas
sem impressão por um script temporário fora do repositório.

## Modelos configurados

| Provider | Modelo |
|---|---|
| OpenAI | `gpt-5.6-luna` |
| NVIDIA | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` |
| Gemini | `gemini-3.5-flash` |

## Providers isolados

| Cenário | Provider | Tentativa | Resultado | Primeiro token | Classe de fontes | Fontes Citadas |
|---|---|---:|---|---:|---|---|
| recuperação | OpenAI | 1 | HTTP 429; saldo da conta esgotado | — | — | — |
| recuperação | NVIDIA | 3 | 2 sucessos; 1 **Recusa** | não registrado por execução | variável | não registrado por execução |
| recuperação | Gemini | 3 | 3 **Recusas** | não aplicável | `sem_resultados` | — |
| citação | OpenAI | 1 | HTTP 429; saldo da conta esgotado | — | — | — |
| citação | NVIDIA | 1 | sucesso | 19,85 s | `citadas` | `es2023_ragas.pdf`, p. 5 |
| citação | Gemini | 1 | HTTP 503 | — | — | — |
| Recusa | OpenAI | 0 | **Recusa** sem geração | 0,12 s total | `sem_resultados` | — |
| Recusa | NVIDIA | 0 | **Recusa** sem geração | 2,40 s total | `sem_resultados` | — |
| Recusa | Gemini | 0 | **Recusa** sem geração | 2,14 s total | `sem_resultados` | — |
| filtro composto | OpenAI | 1 | HTTP 429; saldo da conta esgotado | — | — | — |
| filtro composto | NVIDIA | 1 | sucesso | 29,20 s | fontes recuperadas | 2 chunks de `karpukhin2020_dpr.pdf` |
| filtro composto | Gemini | 1 | sucesso | 3,91 s | fontes recuperadas | 3 chunks de `karpukhin2020_dpr.pdf` |

`—` indica que não houve resposta gerada. O tempo de primeiro token não se
aplica à **Recusa**, pois ela não chama provider de geração.

## Cadeia canônica

| Ordem | Provider | Resultado |
|---:|---|---|
| 1 | OpenAI | falhou antes do primeiro token |
| 2 | NVIDIA | falhou antes do primeiro token |
| 3 | Gemini | resposta completa; primeiro token em 6,55 s |

Metadados finais: `generation_provider: "Gemini"`, `fallback_used: true`,
`attempted_providers: ["OpenAI", "NVIDIA", "Gemini"]`.

## Conclusão e pendência

A cadeia de fallback remoto concluiu com Gemini. A **Recusa** ocorreu sem
chamar geração nos três providers. A geração isolada da OpenAI permanece
pendente por HTTP 429 com `credit_balance_exhausted`, não por falha de
integração. NVIDIA e Gemini foram validados com chamadas reais.

Fonte dos dados: adendo “Prova real dos providers”, na auditoria integral da
RODADA-2.
