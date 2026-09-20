# Instruções para agentes

## Prioridade de fontes

Siga, nesta ordem: ADR-002, ADR-001, PRD, TDD, `CONTEXT.md`, issue ativa e este
arquivo. A ADR-002 supera somente a decisão de embeddings da ADR-001.
Documentos do fluxo Ollama que tratam geração local descrevem o legado; não
anulam a arquitetura híbrida aceita nesta branch.

## Limites da entrega P0

- Use `bge-m3` via Ollama para embeddings e OpenAI diretamente para geração, sem
  LangChain, FAISS ou SentenceTransformers locais.
- Preserve Chroma, separando Corpus Oficial persistente e Índice de Sessão
  efêmero.
- Uma pergunta usa uma Base Ativa. Não misture bases, sessões ou uploads.
- A resposta é grounded: chunks insuficientes produzem Recusa, não conhecimento
  externo.
- Upload é temporário, textual, limitado a três PDFs de 20 MB; OCR é pós-webinar.

## Método de trabalho

1. Escolha uma única issue do milestone e leia seus critérios de aceite.
2. Use a linguagem de `CONTEXT.md`; não chame Chunk Recuperado de Fonte Citada.
3. Escreva um teste de comportamento no seam combinado antes da implementação.
4. Faça a menor mudança necessária, execute testes e revise o diff.
5. Registre evidência, atualize a issue e faça um commit por issue.

## Operação por subagentes

Leia [o plano de execução no TDD](docs/tdd/migracao-openai-rag.md#operação-por-subagentes)
antes de delegar. Use as definições versionadas em `.agent/subagents/`.

- `openai-rag-implementer`: uma issue por vez; escreve código com
  `gpt-5.6-terra` e esforço `medium`.
- `openai-rag-mechanical`: inventário, links, testes e documentação isolados;
  usa `gpt-5.6-luna` e esforço `medium`; não altera código de produto.
- `openai-rag-cto-reviewer`: gate somente-leitura com `gpt-5.6-sol` e esforço
  `medium`, após MIG-01, após a adaptação híbrida de MIG-02/MIG-03, após MIG-05
  e antes do ensaio. Gate MIG-05 atual: `ALTERAÇÕES NECESSÁRIAS`; não iniciar
  MIG-06 até novo gate.

Não execute tarefas de escrita em paralelo no mesmo worktree. Um gate aprovado
é necessário antes de iniciar a issue dependente; o revisor reporta achados, mas
não corrige o código.

## Seams de teste

- Provider de embeddings Ollama: `bge-m3`; mock somente a fronteira externa.
- Provider OpenAI: geração e streaming; mock somente a fronteira externa.
- Fachada RAG: Base Ativa, retrieval, fontes, recusa, retry e resposta parcial.
- Streamlit: estado, histórico, upload, limpeza, fontes e erros via AppTest.

## Segurança, migração e rollback

- Nunca registre ou versione `OPENAI_API_KEY`, `.env` ou `secrets.toml`.
- Não apague a coleção Chroma legada nem o corpus original durante a migração.
- Preserve a tag `legacy-pre-openai`; ela é o rollback aprovado.
- Não implemente fallback automático para geração local; ele existe somente no
  rollback explícito pela tag.
- Falhas devem ser observáveis e acionáveis, sem traceback ou segredo na UI.

## Fora do escopo

Não implementar OCR, bounding boxes, persistência de uploads, consulta combinada,
SHAP/RAGAS, Playwright ou revisão ampla de UX antes do ensaio.
