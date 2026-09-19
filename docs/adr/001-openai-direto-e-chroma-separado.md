# ADR-001: Usar OpenAI direto e índices Chroma separados

- **Data**: 2026-09-19
- **Status**: Aceito
- **Decisores**: equipe do webinário
- **Tags**: rag, openai, chroma, grounding

## Contexto e problema

O caminho legado depende de Ollama para embeddings, geração e etapas auxiliares.
As medições mostram indexação e respostas incompatíveis com o ensaio. A migração
precisa reduzir a dependência de inferência local sem perder a explicação didática
do pipeline RAG, as fontes recuperadas nem uma forma simples de rollback.

## Direcionadores

- Reduzir risco operacional para o ensaio de 21/09.
- Preservar o corpus fixo, a recuperação explícita e o Chroma persistente já usados.
- Impedir respostas baseadas em conhecimento externo quando o contexto não basta.
- Isolar documentos enviados por uma pessoa de outras sessões.

## Opções consideradas

- OpenAI direto, Chroma persistente e índice efêmero por sessão.
- LangChain, FAISS e SentenceTransformers locais, como no repositório de referência.
- Manter Ollama como caminho crítico.

## Decisão

Usaremos o SDK OpenAI diretamente, com `gpt-5.6-luna` para geração e
`text-embedding-3-small` para embeddings. O corpus oficial ficará em uma coleção
Chroma persistente; uploads usarão uma coleção Chroma efêmera exclusiva da sessão.
Cada pergunta consulta exatamente uma base. A geração só pode afirmar fatos
sustentados pelos chunks enviados e recusa quando eles forem insuficientes.

## Consequências

### Positivas

- Remove Ollama e modelos locais do caminho crítico.
- Mantém retrieval, metadados e fontes visíveis para a aula.
- Permite apagar o índice de upload ao fim da sessão sem tocar no corpus oficial.
- Mantém rollback simples pela tag `legacy-pre-openai`.

### Negativas

- Exige chave OpenAI, conectividade e observação de custo/erros da API.
- Requer reindexar o corpus, pois os vetores legados não são compatíveis.
- Não adota upload persistente, OCR, bounding boxes ou destaques de página nesta
  entrega.

## Links

- [TDD da migração](../tdd/migracao-openai-rag.md)
- [PRD da migração](../prd/migracao-openai-rag.md)
- [Glossário do contexto RAG](../../CONTEXT.md)
