# Handoff: continuar a migração OpenAI RAG

## Prompt para uma nova conversa

```text
Continue a migração OpenAI RAG no worktree
D:\webinarioOllamaRAG-openai, branch feat/openai-rag-migration.

Leia primeiro AGENTS.md, CLAUDE.md,
docs/handoff/continuar-migracao-openai-rag.md,
docs/adr/001-openai-direto-e-chroma-separado.md,
docs/adr/002-bge-m3-local-e-geracao-openai.md,
docs/prd/migracao-openai-rag.md, docs/tdd/migracao-openai-rag.md,
docs/testing/estrategia-test-first-openai-rag.md e CONTEXT.md.

O gate CTO conjunto da reindexação híbrida e da Fachada RAG foi aprovado;
continue somente MIG-04 (#62), em test-first, sem ampliar o escopo. A prova real
de geração da #70 continua bloqueada por HTTP 429 e não bloqueia MIG-04, mas
bloqueia o aceite final e o gate pré-webinar. Preserve o rollback e não exponha
segredos.
```

## Estado comprovado

- Branch: `feat/openai-rag-migration`.
- MIG-01: concluída; SDK `openai==3.16.2`.
- Corpus Oficial híbrido: 8 artigos, 661 chunks, `bge-m3`, dimensão 1024.
- Fachada RAG híbrida e limiar de retrieval: validados; gate CTO aprovado para
  iniciar MIG-04.
- MIG-03G/#70: chamada mínima real alcançou a OpenAI, mas retornou HTTP 429;
  issue aberta e bloqueada. A evidência está em
  `docs/evidencias/MIG-03G/validacao.md`.
- Ambiente canônico: `.venv`, usando `requirements.lock`.
- `.venv-incomplete-20260919` e `.venv-openai`: não são ambientes canônicos.
- Rollback: tag remota `legacy-pre-openai`, no commit `8726fef`.
- A migração possui ADR, PRD, glossário, TDD, estratégia test-first, backlog
  GitHub e perfis de subagentes versionados.
- A geração OpenAI ainda não tem prova real concluída. Não apresentar a
  migração como aceita nem o gate pré-webinar como aprovado.
- A issue #45 permanece aberta e bloqueada apenas pela prova positiva contra um
  Ollama disponível; sua implementação e teste de reprovação foram preservados
  no commit do rollback. Ela não autoriza mudar o legado incidentalmente.

## Decisões aceitas

- Use `bge-m3` via Ollama para embeddings e OpenAI direto com `gpt-5.6-luna`
  para geração.
- Preserve Chroma: Corpus Oficial persistente e Índice de Sessão efêmero.
- Consulte uma Base Ativa por pergunta, sem misturar corpus e upload.
- Recuse quando não houver contexto suficiente; não complemente com conhecimento
  externo.
- Mantenha até dois turnos apenas na geração; retrieval usa a pergunta atual.
- Limite upload a três PDFs de 20 MB; OCR é pós-webinar.

## Próxima unidade de trabalho: MIG-04

Trabalhe apenas a issue GitHub #62: criar o Índice de Sessão temporário e provar
o isolamento entre sessões e entre bases. O gate CTO híbrido já permite iniciar
essa issue. A #70 permanece um bloqueio externo separado: só uma geração real
com status `completed` libera o aceite final e o gate pré-webinar.

Faça primeiro testes de comportamento e preserve o Corpus Oficial e todas as
coleções legadas. Não instale LangChain, FAISS ou SentenceTransformers.

## Modelo operacional

- `gpt-5.6-terra`, esforço `medium`: implementa uma issue por vez.
- `gpt-5.6-luna`, esforço `medium`: tarefas mecânicas isoladas, sem código de
  produto.
- `gpt-6-astra`, esforço `medium`, somente leitura: gate após MIG-01, MIG-03,
  MIG-05 e antes do ensaio.

Não faça escritas paralelas no mesmo worktree. O gate do CTO revisa o diff e o
impacto em componentes relacionados, incluindo provider, índice, retrieval,
metadados, fontes, configuração, testes e rollback.

## Referências canônicas

- `AGENTS.md` e `CLAUDE.md`: sequência e regras de trabalho.
- `docs/adr/002-bge-m3-local-e-geracao-openai.md`: decisão vigente para
  embeddings; supera somente esse ponto da ADR-001.
- `docs/adr/001-openai-direto-e-chroma-separado.md`: demais decisões
  arquiteturais.
- `docs/prd/migracao-openai-rag.md`: escopo e aceite P0.
- `docs/tdd/migracao-openai-rag.md`: desenho e operação por subagentes.
- `docs/testing/estrategia-test-first-openai-rag.md`: testes obrigatórios.
- `CONTEXT.md`: termos de domínio.
- `.agent/subagents/`: prompts versionados dos três papéis.
