# ADR-002: bge-m3 local e geração OpenAI

- **Data**: 2026-09-19
- **Status**: Aceito
- **Decisores**: equipe do webinário
- **Tags**: rag, ollama, openai, embeddings, chroma

## Contexto

A migração implementou contratos e uma coleção candidata com embeddings OpenAI,
mas a validação real encontrou limite de requisições antes de comprovar a
reindexação completa. O ambiente já dispõe do `bge-m3` via Ollama e a decisão do
webinário prioriza uma recuperação reproduzível sem consumir a cota de
embeddings da OpenAI. A geração continua dependente da OpenAI para manter a
qualidade e o streaming definidos para o P0.

Esta ADR supera somente a escolha do provedor e do modelo de embeddings na
[ADR-001](001-openai-direto-e-chroma-separado.md). Permanecem válidas as
decisões de usar Chroma separado por **Base Ativa**, grounding estrito,
**Recusa**, SDK OpenAI direto para geração e rollback pela tag
`legacy-pre-openai`.

## Direcionadores

- Usar o mesmo espaço vetorial no **Corpus Oficial** e no **Índice de Sessão**.
- Evitar que cota de embeddings bloqueie a reindexação ou o ensaio.
- Preservar metadados, isolamento entre bases e compatibilidade verificável.
- Impedir troca silenciosa de provedor durante uma pergunta.

## Opções

- `bge-m3` via Ollama para embeddings e `gpt-5.6-luna` via OpenAI para geração.
- OpenAI para embeddings e geração, como definido originalmente na ADR-001.
- Ollama para embeddings e geração, como caminho operacional principal.

## Decisão

Use `bge-m3` via Ollama para criar e consultar tanto o **Corpus Oficial** quanto
o **Índice de Sessão**. Identifique cada coleção com provedor, modelo, dimensão
e versão de esquema; recuse coleção incompatível e exija reindexação explícita.

Use `gpt-5.6-luna` via SDK OpenAI direto somente para geração e streaming. Não
implemente fallback automático para geração local. A geração local permanece
apenas no rollback documentado pela tag `legacy-pre-openai`, acionado como uma
troca operacional explícita.

## Consequências

Positivas:

- Reindexação e consultas não consomem cota de embeddings da OpenAI.
- As duas bases compartilham o mesmo modelo e espaço vetorial.
- A fronteira entre recuperação local e geração remota fica explícita e
  testável.

Negativas:

- Ollama e `bge-m3` voltam ao caminho crítico de indexação e retrieval.
- A coleção candidata criada com embeddings OpenAI não pode ser reutilizada.
- O gate precisa validar reindexação híbrida e a fachada antes de liberar
  MIG-04.
- Indisponibilidade da OpenAI usa fallback remoto conforme a
  [ADR-003](003-fallback-remoto-de-geracao.md); não há fallback automático
  para geração local.

## Links

- Supera parcialmente:
  [ADR-001: OpenAI direto; Chroma separado](001-openai-direto-e-chroma-separado.md)
- [TDD da migração](../tdd/migracao-openai-rag.md)
- [PRD da migração](../prd/migracao-openai-rag.md)
- [ADR-003: fallback remoto de geração](003-fallback-remoto-de-geracao.md)
- [Issue #61](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/61)
