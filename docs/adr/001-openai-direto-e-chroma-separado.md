# ADR-001: OpenAI direto; Chroma separado

- **Data**: 2026-09-19
- **Status**: Aceito
- **Decisores**: equipe do webinário
- **Tags**: rag, openai, chroma, grounding

## Contexto

Legado usa Ollama para embeddings, geração e auxiliares. Indexação e respostas
não atendem ao ensaio. Migração deve reduzir inferência local, preservar ensino
RAG, chunks recuperados e rollback simples.

## Direcionadores

- Reduzir risco operacional para ensaio de 21/09.
- Preservar corpus fixo, retrieval explícito e Chroma persistente.
- Bloquear conhecimento externo quando contexto não basta.
- Isolar uploads entre sessões.

## Opções

- OpenAI direto + Chroma persistente + índice efêmero por sessão.
- LangChain, FAISS e SentenceTransformers locais.
- Ollama como caminho crítico.

## Decisão

Use SDK OpenAI direto: `gpt-5.6-luna` para geração;
`text-embedding-3-small` para embeddings. **Corpus Oficial** fica em coleção
Chroma persistente; **Índice de Sessão**, em coleção Chroma efêmera exclusiva da
sessão.
Cada pergunta consulta exatamente uma **Base Ativa**. Geração afirma apenas fatos
sustentados pelos chunks enviados; contexto insuficiente produz **Recusa**.

## Consequências

Positivas:

- Ollama/modelos locais saem do caminho crítico.
- Retrieval, metadados e fontes continuam visíveis na aula.
- Índice de upload pode ser apagado sem tocar Corpus Oficial.
- Rollback continua simples via `legacy-pre-openai`.

Negativas:

- Exige chave OpenAI, conectividade e observação de custo/erros API.
- Exige reindexação: vetores legados são incompatíveis.
- Esta entrega não adota upload persistente, OCR, bounding boxes ou destaques
  de página.

## Links

- [TDD da migração](../tdd/migracao-openai-rag.md)
- [PRD da migração](../prd/migracao-openai-rag.md)
- [Glossário do contexto RAG](../../CONTEXT.md)
