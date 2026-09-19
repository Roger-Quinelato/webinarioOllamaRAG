# CLAUDE.md

Orientação para agentes que trabalham nesta branch de migração.

## Estado da branch

Esta é a branch `feat/openai-rag-migration`. A arquitetura-alvo está aceita, mas
o código ainda contém o caminho legado com Ollama até as issues `MIG-01` a
`MIG-08` serem concluídas. Não descreva, teste ou apresente o caminho OpenAI como
implementado antes da issue correspondente passar seus critérios de aceite.

A tag `legacy-pre-openai` aponta para o rollback do estado anterior. Preserve-a e
não apague a coleção Chroma legada durante a migração.

## Fontes canônicas

- [ADR-001](docs/adr/001-openai-direto-e-chroma-separado.md): decisão aceita.
- [PRD](docs/prd/migracao-openai-rag.md): escopo P0 e critérios do webinário.
- [TDD](docs/tdd/migracao-openai-rag.md): componentes, fluxo, riscos e rollback.
- [Estratégia test-first](docs/testing/estrategia-test-first-openai-rag.md):
  seams e cenários obrigatórios.
- [Glossário](CONTEXT.md): termos de domínio obrigatórios.
- [Milestone no GitHub](https://github.com/Roger-Quinelato/webinarioOllamaRAG/milestone/1):
  ordem operacional das issues.

Em caso de conflito, ADR e PRD prevalecem sobre documentação histórica do
caminho Ollama.

## Arquitetura-alvo P0

- Use SDK OpenAI diretamente: `text-embedding-3-small` para embeddings e
  `gpt-5.6-luna` para geração.
- Mantenha Chroma: uma coleção persistente para o **Corpus Oficial** e uma coleção
  efêmera por sessão para o **Índice de Sessão**.
- Consulte uma única **Base Ativa** por pergunta. Nunca combine corpus e upload.
- Restrinja a resposta aos chunks enviados. Sem evidência suficiente, devolva a
  **Recusa** padronizada, sem conhecimento externo.
- Mostre **Fonte Citada** apenas quando a resposta usar um marcador válido;
  resultado recuperado sem marcador é fallback, não citação.
- Limite uploads a três PDFs de 20 MB, sem OCR no P0. O ano é opcional.
- Use as duas últimas turnos apenas para geração; retrieval usa a pergunta atual.
- Faça no máximo uma repetição antes do primeiro token. Depois disso, preserve e
  identifique a **Resposta Parcial**.

Não adote LangChain, FAISS, SentenceTransformers locais, OCR/Tesseract, bounding
boxes, persistência de upload, SHAP/RAGAS ou revisão ampla de UX no P0.

## Fluxo por issue

1. Trabalhe uma issue por vez, na ordem `MIG-01` a `MIG-08`.
2. Antes de editar, leia a issue, o ADR, o PRD, o TDD e os termos relevantes do
   `CONTEXT.md`.
3. Defina ou atualize primeiro o teste no seam acordado; use mocks apenas na
   fronteira OpenAI.
4. Implemente a menor mudança que faz o teste passar.
5. Rode testes, revisão de código e verificações da issue. Salve evidências
   reproduzíveis em `docs/evidencias/`.
6. Faça um commit por issue, com o número da issue, depois da revisão.

## Operação por subagentes

O [TDD](docs/tdd/migracao-openai-rag.md#operação-por-subagentes) define os
papéis, modelos, esforços e gates. Use os prompts versionados em
`.agent/subagents/`. Um implementador trabalha sozinho por issue; tarefas
mecânicas não concorrem com alterações de código; o CTO é somente-leitura e atua
nos gates de MIG-01, MIG-03, MIG-05 e do ensaio.

Para cada gate, revise o diff e os critérios da issue, depois siga o fluxo de
dados pelos componentes relacionados. A revisão de embeddings, por exemplo,
cobre provider, reindexação, compatibilidade de coleção, retrieval, metadados,
fontes, configuração, testes e rollback — não apenas o módulo editado.

## Segurança e verificação

- Leia `OPENAI_API_KEY` de secrets ou ambiente. Nunca versione, exiba ou registre
  a chave; MIG-01 deve ignorar `.env` e `.streamlit/secrets.toml` antes de o
  provider ser configurado.
- Registre modelo, Base Ativa, quantidade de chunks, latência, tentativa, recusa
  e resposta parcial, sem registrar a chave ou o conteúdo integral de uploads.
- A matriz de cinco perguntas deve cobrir recuperação, citação, recusa, filtro e
  upload antes do ensaio.
- `docs/VERIFICACAO.md` e os comandos que dependem de Ollama são evidência do
  legado. Não marque critérios OpenAI como verificados com essas saídas.

## Legado

O código, notebook e scripts atuais são referência de migração e rollback. Não
remova o legado por limpeza incidental. Alterações destrutivas exigem uma issue
que tenha plano de migração, prova de compatibilidade e rollback explícito.
