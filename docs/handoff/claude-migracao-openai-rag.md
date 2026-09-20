# Handoff: documentação da migração OpenAI RAG

## Estado

- Base: `main`.
- MIG-04 está mergeada em `f8ec561`.
- PR #72 está mergeado: fallback remoto OpenAI, NVIDIA e Gemini.
- PR #73 está mergeado: CTO usa `gpt-5.6-sol`, esforço `medium`.
- Gate MIG-05 ainda exige AppTests adicionais e validação real dos providers.
- MIG-06 tem material híbrido preparado, mas não equivale a aceite do gate.
- HTTP 429 ainda bloqueia aceite final da geração real.

## Arquitetura vigente

Use `bge-m3` via Ollama apenas para embeddings. Use router remoto OpenAI,
NVIDIA e Gemini para geração e streaming. Preserve Chroma separado: Corpus
Oficial persistente e Índice de Sessão efêmero. Uma pergunta usa uma Base
Ativa. Recuse sem contexto suficiente.

## Próximo passo

Completar AppTests do fluxo enxuto: falhas, streaming, memória, fontes, Recusa,
Resposta Parcial e descarte. Reexecutar suíte, atualizar evidência e rodar gate
CTO somente leitura. Só depois liberar MIG-07 e ensaio.

## Skills sugeridas

`docs-writer`, `caveman`, `caveman-review`, `coding-guidelines`, `verify-and-stop`.
