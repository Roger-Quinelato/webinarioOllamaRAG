# Handoff: documentação da migração OpenAI RAG

## Estado

- Branch: `feat/openai-rag-migration`.
- MIG-04 commitada em `f8ec561`.
- MIG-05 commitada em `738cc0c`; 50 testes passam.
- Gate CTO de MIG-05 retornou `ALTERAÇÕES NECESSÁRIAS` por cobertura AppTest
  insuficiente. Citações, histórico entre bases e PDF sem texto foram corrigidos
  depois do gate; repetir revisão antes de MIG-06.
- MIG-06 e MIG-07 ainda não iniciadas. Geração OpenAI real segue bloqueada por
  HTTP 429; não marcar aceite final.

## Arquitetura vigente

Use `bge-m3` via Ollama apenas para embeddings. Use OpenAI direto para geração e
streaming. Preserve Chroma separado: Corpus Oficial persistente e Índice de
Sessão efêmero. Uma pergunta usa uma Base Ativa. Recuse sem contexto suficiente.

## Próximo passo

Completar AppTests de upload, limites, falhas, streaming, memória, fontes,
Recusa, Resposta Parcial e descarte. Reexecutar suíte, atualizar evidência,
rodar gate CTO somente leitura. Só depois iniciar MIG-06.

## Skills sugeridas

`docs-writer`, `caveman`, `caveman-review`, `coding-guidelines`, `verify-and-stop`.
