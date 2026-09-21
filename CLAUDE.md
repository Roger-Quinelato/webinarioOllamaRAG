# CLAUDE.md

Orientação para agentes nesta branch de migração.

## Estado

Branch principal contém MIG-04 e MIG-05, incluindo fallback remoto OpenAI,
NVIDIA e Gemini. AppTests adicionais e prova real dos providers ainda exigem
gate CTO. MIG-06 permanece material de treinamento separado. Não afirme aceite
final enquanto a prova real de geração segue bloqueada por HTTP 429.

Preserve tag `legacy-pre-openai` para rollback. Não apague coleção Chroma legada.

## Fontes canônicas

- [ADR-004](docs/adr/004-ordem-configuravel-de-providers.md): ordem padrão
  Gemini, NVIDIA e OpenAI, configurável; supera só a ordem da ADR-003.
- [ADR-003](docs/adr/003-fallback-remoto-de-geracao.md): fallback remoto de
  geração; supera a consequência de indisponibilidade da ADR-002.
- [ADR-002](docs/adr/002-bge-m3-local-e-geracao-openai.md): decisão vigente de
  embeddings e geração.
- [ADR-001](docs/adr/001-openai-direto-e-chroma-separado.md): decisões
  preservadas de Chroma separado, grounding e geração OpenAI.
- [PRD](docs/prd/migracao-openai-rag.md): escopo P0 e critérios.
- [TDD](docs/tdd/migracao-openai-rag.md): componentes, fluxo, riscos, rollback.
- [Estratégia test-first](docs/testing/estrategia-test-first-openai-rag.md):
  seams e cenários.
- [Glossário](CONTEXT.md): termos obrigatórios.
- [Milestone GitHub](https://github.com/Roger-Quinelato/webinarioOllamaRAG/milestone/1):
  ordem das issues.

Conflito: ADR e PRD prevalecem sobre documentação histórica. A ADR-004 supera
somente a ordem de providers da ADR-003. A ADR-003 supera
a consequência de indisponibilidade da ADR-002; a ADR-002 supera somente a
decisão de embeddings da ADR-001.

## Arquitetura P0

- Use `bge-m3` via Ollama para embeddings do Corpus Oficial e do Índice de
  Sessão; use providers remotos OpenAI, NVIDIA e Gemini somente para geração.
- Preserve Chroma: coleção persistente para **Corpus Oficial**; coleção efêmera
  por sessão para **Índice de Sessão**.
- Cada pergunta consulta uma **Base Ativa**. Nunca misture corpus e upload.
- Responda apenas com chunks enviados. Evidência insuficiente: **Recusa**,
  sem conhecimento externo.
- Mostre **Fonte Citada** só com marcador válido. Chunk recuperado sem marcador:
  fallback, não citação.
- Upload: até três PDFs, 20 MB cada; ano opcional; a UI permanece desativada
  durante o treino; sem OCR no P0.
- Geração recebe as duas últimas turnos; retrieval recebe só pergunta atual.
- Faça no máximo uma repetição antes do primeiro token. Depois, preserve e
  identifique **Resposta Parcial**.
- Não faça fallback automático para geração local. O caminho local de geração
  existe somente no rollback explícito pela tag `legacy-pre-openai`.

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
- CTO: somente leitura; gates após `MIG-01`, após a adaptação híbrida de
  `MIG-02`/`MIG-03`, após `MIG-05` e antes do ensaio.

Gate: revise diff e critérios; rastreie dados por componentes; cubra provider,
reindexação, compatibilidade Chroma, retrieval, metadados, fontes, configuração,
testes e rollback. Não paralelize escritas no mesmo worktree.

## Segurança e verificação

- Leia `OPENAI_API_KEY` de secrets/ambiente. Nunca versione, exiba ou registre a
  chave. `MIG-01` ignora `.env` e `.streamlit/secrets.toml` antes de configurar
  provider.
- Registre modelo, Base Ativa, quantidade de chunks, latência, tentativa, recusa
  e resposta parcial; nunca chave nem conteúdo integral de upload.
- Antes do ensaio, matriz de quatro perguntas deve cobrir recuperação, citação,
  recusa e filtro. Upload entra em uma quinta pergunta somente quando
  `UPLOADS_STREAMLIT_HABILITADOS=True`.
- Comandos dependentes de Ollama e evidências históricas removidas comprovam
  legado. Não marque critério OpenAI verificado com essa saída.

## Legado

Código, notebook e scripts são referência de migração/rollback. Não remova legado
por limpeza incidental. Mudança destrutiva exige issue com migração, compatibilidade
e rollback explícitos.
