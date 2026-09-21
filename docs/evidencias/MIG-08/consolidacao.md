# MIG-08 — consolidação de evidências e rollback

**Data:** 2026-09-21
**Estado:** parcial. Cada critério P0 abaixo aponta para teste ou evidência
versionada, mas dois itens seguem sem prova real (geração OpenAI e fallback de
provider pela UI). Por isso a #65 **não deve ser fechada ainda**, e a migração
não pode ser declarada aceita (CLAUDE.md, seção Estado).

## Critérios de aceite do PRD × evidência

| Critério P0 (`docs/prd/migracao-openai-rag.md`) | Situação | Teste / evidência |
|---|---|---|
| Sem credencial remota: explicar a configuração e não consultar | Provado | `tests/test_generation_providers.py::test_sem_credencial_expoe_configuracao_acionavel`; `tests/test_app.py` (linha 64) |
| Sem Ollama ou `bge-m3`: explicar e não consultar | Provado | `tests/test_ollama_embedding_provider.py` (`test_ollama_indisponivel_tem_mensagem_acionavel`, `test_bge_m3_ausente_orienta_instalacao`) |
| Coleção incompatível: recusar e orientar a reindexação | Provado | `tests/test_openai_rag.py::test_base_ativa_rejeita_cada_metadado_incompativel_e_orienta_reindexacao` e `::test_retrieval_recusa_dimensao_real_incompativel_antes_de_consultar_chroma`; AppTest de orientação em `tests/test_app.py` |
| Resposta grounded: só fontes referenciadas; sem citação vira Chunk Recuperado | Provado | `tests/test_openai_rag.py`; `tests/test_app.py`; UI real em [`fluxo-real-ui-pt-br-2026-09-21.md`](../MIG-07/fluxo-real-ui-pt-br-2026-09-21.md) (perguntas 2 e 4) |
| Sem evidência: Recusa sem conhecimento externo | Provado | `tests/test_openai_rag.py`; UI real (pergunta 3, `sem_resultados`) |
| Upload isolado e sem alterar a coleção oficial | Provado no domínio, não pela UI | `tests/test_session_index.py` (`test_indices_sao_isolados_com_cliente_compartilhado`, `test_descartar_preserva_corpus_oficial`). O upload está desativado na UI |
| Falha antes do 1º token: próximo provider; `retry-after` curto repete; depois, Resposta Parcial | Provado por testes; **sem prova real** | `tests/test_generation_router.py` (linhas 25, 44 e 62); `tests/test_openai_rag.py` (linhas 303 e 396). O fallback real só foi observado em 2026-09-20 ([`MIG-05/validacao-real-2026-09-20.md`](../MIG-05/validacao-real-2026-09-20.md)) |
| Matriz de quatro perguntas passa e tem evidência versionada | Parcial | [`matriz-pt-br`](../matriz-pt-br/README.md) e a UI real: retrieval, citação, Recusa e filtro passam; a pergunta de recuperação falhou em 3 de 6 execuções com a NVIDIA. Upload é requisito futuro |
| Geração real pela OpenAI | **Não provado** | HTTP 429 (`credit_balance_exhausted`); issue #70 |

## Rollback

- **Tag:** `legacy-pre-openai` → `d68205d40f23952c4370305f9a3ab362c4c29f17`.
- **Coleção ativa:** `artigos_rag_hibrido_a7e480ac787f` (213 chunks, `bge-m3`,
  1024 dimensões, `ready`), apontada por `chroma_db/hybrid_manifest.json`.
- **Coleções preservadas, nenhuma apagada:** `artigos_rag_hibrido_a280e65e16ee`
  (661 chunks, 8 artigos), `artigos_rag_openai` e
  `artigos_rag_openai_1789869651617850`.

Sequência, por ordem de custo:

1. **Voltar ao corpus anterior, sem sair do fluxo híbrido:** seguir a seção
   "Rollback" de [`corpus-pt-br/README.md`](../corpus-pt-br/README.md) (manifesto
   anterior, `config.py`, `metadados.csv` e PDFs em inglês).
2. **Trocar a ordem de providers, sem alterar código:** definir
   `GENERATION_PROVIDERS_ORDER` (ADR-004), por exemplo `gemini,nvidia,openai`.
3. **Voltar à geração local:** `git checkout legacy-pre-openai`. A coleção
   `artigos_rag` pode não existir na máquina; nesse caso, reindexe com
   `python scripts/02_indexar.py` (cerca de 19 a 24 min; exige `qwen2.5:1.5b` e
   `qwen2.5:3b`). Detalhes em [`docs/troubleshooting.md`](../../troubleshooting.md).
   Não há fallback automático para geração local.

## Segredos

`git ls-files` não contém `.env` nem `.streamlit/secrets.toml` (ambos ignorados
no `.gitignore`). A varredura de `docs/evidencias/matriz-pt-br/` não achou nenhum
valor de chave. O revisor do gate repetiu a varredura em todo o histórico
(`git log --all -S`) sem achar valores reais.

## P1/P2 adiados

- #52: recalcular SHAP e RAGAS no corpus híbrido `bge-m3`, depois do ensaio.
- #57: crítica de design do chat, depois do ensaio.
- Upload de PDFs e Índice de Sessão na UI, quando `UPLOADS_STREAMLIT_HABILITADOS`
  for ligado ([`MIG-04`](../MIG-04/validacao.md)).
- Ressalvas 3, 4, 7, 9 e 10 do [gate CTO](../MIG-05/gate-cto-2026-09-21.md).
