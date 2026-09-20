# ADR-003: fallback remoto de geração

- **Data**: 2026-09-20
- **Status**: Aceito
- **Decisores**: equipe do webinário
- **Tags**: rag, openai, nvidia, gemini, disponibilidade

## Contexto

HTTP 429 da OpenAI bloqueia a validação real de geração. Embeddings já são
locais via Ollama e não precisam de fallback. A resposta precisa continuar
grounded, sem misturar Base Ativa, chunks ou tokens de providers distintos.

## Decisão

Use geração remota na ordem OpenAI, NVIDIA API Catalog e Gemini. O roteador
troca de provider somente antes do primeiro token. Depois do primeiro token,
preserva **Resposta Parcial** e não chama outro provider.

O provider NVIDIA usa endpoint hospedado configurável e a chave
`NVIDIA_API_KEY`. Consulte o [quickstart do NVIDIA API Catalog](https://docs.api.nvidia.com/nim/docs/api-quickstart).
Gemini usa `GEMINI_API_KEY` e SDK `google-genai`.

Falhas 429, timeout, conexão e indisponibilidade avançam para o próximo
provider. Um `retry-after` de até dois segundos permite uma repetição no mesmo
provider. Não há fallback automático para geração local.

MIG-05 só é concluída depois de testes, evidência real dos três providers e
novo gate CTO.

## Consequências

- OpenAI deixa de ser ponto único de falha de geração.
- Retrieval, embeddings e Base Ativa são executados uma vez por pergunta.
- Provider e tentativas ficam observáveis sem registrar credenciais ou prompt
  integral.
- Credenciais NVIDIA e Gemini passam a ser dependências operacionais do ensaio.
- `legacy-pre-openai` continua sendo rollback explícito para geração local.

## Links

- Supera a consequência de indisponibilidade OpenAI da
  [ADR-002](002-bge-m3-local-e-geracao-openai.md).
- [TDD da migração](../tdd/migracao-openai-rag.md)
- [PRD da migração](../prd/migracao-openai-rag.md)
