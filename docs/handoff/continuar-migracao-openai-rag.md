# Handoff: continuar a migração OpenAI RAG

## Prompt para uma nova conversa

```text
Continue a migração OpenAI RAG no worktree
D:\webinarioOllamaRAG-openai, branch feat/openai-rag-migration.

Leia primeiro AGENTS.md, CLAUDE.md, docs/handoff/continuar-migracao-openai-rag.md,
docs/adr/001-openai-direto-e-chroma-separado.md,
docs/prd/migracao-openai-rag.md, docs/tdd/migracao-openai-rag.md,
docs/testing/estrategia-test-first-openai-rag.md e CONTEXT.md.

O código OpenAI ainda não foi iniciado. Comece somente MIG-01, em test-first,
sem ampliar o escopo. Para SDK, modelos ou API OpenAI, use a skill openai-docs
e documentação oficial atual. Para escrever código, use coding-guidelines,
migration e tdd. Preserve o rollback e não exponha segredos.
```

## Estado comprovado

- Branch: `feat/openai-rag-migration`, limpa e publicada em `origin`.
- Último commit: `12dc85c` (`docs: define RAG migration subagents`).
- Rollback: tag remota `legacy-pre-openai`, no commit `8726fef`.
- A migração possui ADR, PRD, glossário, TDD, estratégia test-first, backlog
  GitHub e perfis de subagentes versionados.
- O código ainda usa o caminho legado Ollama. Não apresentar OpenAI como pronto.
- A issue #45 permanece aberta e bloqueada apenas pela prova positiva contra um
  Ollama disponível; sua implementação e teste de reprovação foram preservados
  no commit do rollback. Ela não autoriza mudar o legado incidentalmente.

## Decisões aceitas

- Use OpenAI direto: `text-embedding-3-small` para embeddings e
  `gpt-5.6-luna` para geração.
- Preserve Chroma: Corpus Oficial persistente e Índice de Sessão efêmero.
- Consulte uma Base Ativa por pergunta, sem misturar corpus e upload.
- Recuse quando não houver contexto suficiente; não complemente com conhecimento
  externo.
- Mantenha até dois turnos apenas na geração; retrieval usa a pergunta atual.
- Limite upload a três PDFs de 20 MB; OCR é pós-webinar.

## Próxima unidade de trabalho: MIG-01

Trabalhe apenas a issue GitHub #60: contratos OpenAI, secrets e tratamento de
erros. Antes de configurar qualquer provider, ignore `.env` e
`.streamlit/secrets.toml`. Não há chave `OPENAI_API_KEY` configurada no ambiente
atual. Crie primeiro testes de comportamento para chave ausente e erros de
provider; faça mock somente na fronteira OpenAI.

Confirme a versão e o uso do SDK na documentação oficial atual antes de alterar
dependências. Não instale LangChain, FAISS ou SentenceTransformers.

## Modelo operacional

- `gpt-5.6-terra`, esforço `high`: implementa uma issue por vez.
- `gpt-5.6-luna`, esforço `medium`: tarefas mecânicas isoladas, sem código de
  produto.
- `gpt-6-astra`, esforço `medium`, somente leitura: gate após MIG-01, MIG-03,
  MIG-05 e antes do ensaio.

Não faça escritas paralelas no mesmo worktree. O gate do CTO revisa o diff e o
impacto em componentes relacionados, incluindo provider, índice, retrieval,
metadados, fontes, configuração, testes e rollback.

## Referências canônicas

- `AGENTS.md` e `CLAUDE.md`: sequência e regras de trabalho.
- `docs/adr/001-openai-direto-e-chroma-separado.md`: decisões arquiteturais.
- `docs/prd/migracao-openai-rag.md`: escopo e aceite P0.
- `docs/tdd/migracao-openai-rag.md`: desenho e operação por subagentes.
- `docs/testing/estrategia-test-first-openai-rag.md`: testes obrigatórios.
- `CONTEXT.md`: termos de domínio.
- `.agent/subagents/`: prompts versionados dos três papéis.
