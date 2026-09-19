# CLAUDE.md

Orientação para agentes nesta branch de migração.

## Estado

Branch `feat/openai-rag-migration`. Arquitetura-alvo aceita; código ainda usa
Ollama até `MIG-01`–`MIG-08` concluídas. Não descreva, teste ou apresente OpenAI
como implementado antes do aceite da issue correspondente.

Preserve tag `legacy-pre-openai` para rollback. Não apague coleção Chroma legada.

## Fontes canônicas

- [ADR-001](docs/adr/001-openai-direto-e-chroma-separado.md): decisão.
- [PRD](docs/prd/migracao-openai-rag.md): escopo P0 e critérios.
- [TDD](docs/tdd/migracao-openai-rag.md): componentes, fluxo, riscos, rollback.
- [Estratégia test-first](docs/testing/estrategia-test-first-openai-rag.md):
  seams e cenários.
- [Glossário](CONTEXT.md): termos obrigatórios.
- [Milestone GitHub](https://github.com/Roger-Quinelato/webinarioOllamaRAG/milestone/1):
  ordem das issues.

Conflito: ADR e PRD prevalecem sobre documentação histórica Ollama.

## Arquitetura P0

- Use SDK OpenAI direto: `text-embedding-3-small` para embeddings;
  `gpt-5.6-luna` para geração.
- Preserve Chroma: coleção persistente para **Corpus Oficial**; coleção efêmera
  por sessão para **Índice de Sessão**.
- Cada pergunta consulta uma **Base Ativa**. Nunca misture corpus e upload.
- Responda apenas com chunks enviados. Evidência insuficiente: **Recusa**,
  sem conhecimento externo.
- Mostre **Fonte Citada** só com marcador válido. Chunk recuperado sem marcador:
  fallback, não citação.
- Upload: até três PDFs, 20 MB cada; ano opcional; sem OCR no P0.
- Geração recebe as duas últimas turnos; retrieval recebe só pergunta atual.
- Faça no máximo uma repetição antes do primeiro token. Depois, preserve e
  identifique **Resposta Parcial**.

Não use LangChain, FAISS, SentenceTransformers locais, OCR/Tesseract, bounding
boxes, upload persistente, SHAP/RAGAS ou revisão ampla de UX no P0.

## Fluxo por issue

1. Escolha uma issue; siga `MIG-01`–`MIG-08` em ordem.
2. Leia issue, ADR, PRD, TDD e termos relevantes de `CONTEXT.md`.
3. Escreva/atualize teste no seam acordado; mock apenas fronteira OpenAI.
4. Faça menor mudança que passa teste.
5. Rode testes, revisão e verificações; salve evidências reproduzíveis em
   `docs/evidencias/`.
6. Após revisão, faça um commit por issue com número da issue.

## Subagentes

[TDD](docs/tdd/migracao-openai-rag.md#operação-por-subagentes) define papéis,
modelos, esforços e gates. Use prompts em `.agent/subagents/`.

- Implementador: uma issue, sozinho.
- Executor mecânico: não concorre com código; não altera produto.
- CTO: somente leitura; gates após `MIG-01`, `MIG-03`, `MIG-05` e antes do ensaio.

Gate: revise diff e critérios; rastreie dados por componentes; cubra provider,
reindexação, compatibilidade Chroma, retrieval, metadados, fontes, configuração,
testes e rollback. Não paralelize escritas no mesmo worktree.

## Segurança e verificação

- Leia `OPENAI_API_KEY` de secrets/ambiente. Nunca versione, exiba ou registre a
  chave. `MIG-01` ignora `.env` e `.streamlit/secrets.toml` antes de configurar
  provider.
- Registre modelo, Base Ativa, quantidade de chunks, latência, tentativa, recusa
  e resposta parcial; nunca chave nem conteúdo integral de upload.
- Antes do ensaio, matriz de cinco perguntas deve cobrir recuperação, citação,
  recusa, filtro e upload.
- Comandos dependentes de Ollama e evidências históricas removidas comprovam
  legado. Não marque critério OpenAI verificado com essa saída.

## Legado

Código, notebook e scripts são referência de migração/rollback. Não remova legado
por limpeza incidental. Mudança destrutiva exige issue com migração, compatibilidade
e rollback explícitos.
