# Evidência MIG-03F — issue #69

Data: 2026-09-20

## Escopo validado

- A Fachada RAG repete a geração uma vez antes do primeiro token e, se a segunda
  falha já for um `ErroProviderOpenAI`, preserva mensagem segura, `status_code` e
  `retry_after` para autenticação (401), limite (429) e rede.
- Exceções inesperadas continuam convertidas na mensagem genérica segura.
- Texto já emitido continua preservado como **Resposta Parcial**.
- A Fachada exige exatamente um embedding da pergunta e valida sua dimensão
  contra a **Base Ativa** e os metadados da coleção antes de consultar Chroma.
- A prova de dimensão usa uma coleção Chroma efêmera real e simula somente a
  fronteira externa do Ollama por meio de `ProviderEmbeddingsOllama`.

## Ciclos RED → GREEN

### Erro seguro após retry

RED:

```text
python -m unittest tests.test_openai_rag.OpenAIRAGTest.test_apos_retry_preserva_erro_seguro_de_autenticacao_openai
FAIL: mensagem acionável de autenticação substituída por
"A geração falhou antes do primeiro token. Tente novamente."
```

GREEN e regressões próximas:

```text
python -m unittest \
  tests.test_openai_rag.OpenAIRAGTest.test_apos_retry_preserva_erro_seguro_de_autenticacao_openai \
  tests.test_openai_rag.OpenAIRAGTest.test_falha_openai_nao_aciona_geracao_local \
  tests.test_openai_rag.OpenAIRAGTest.test_falha_depois_do_primeiro_token_preserva_e_marca_resposta_parcial
Ran 3 tests — OK
```

Casos adicionais 429 e rede:

```text
python -m unittest \
  tests.test_openai_rag.OpenAIRAGTest.test_apos_retry_preserva_erro_seguro_de_limite_openai \
  tests.test_openai_rag.OpenAIRAGTest.test_apos_retry_preserva_erro_seguro_de_rede_openai
Ran 2 tests — OK
```

### Dimensão antes de Chroma

RED:

```text
.venv/Scripts/python.exe -m unittest \
  tests.test_openai_rag.OpenAIRAGTest.test_retrieval_recusa_dimensao_real_incompativel_antes_de_consultar_chroma
ERROR: chromadb.errors.InvalidArgumentError:
Collection expecting embedding with dimension of 3, got 2
```

GREEN:

```text
.venv/Scripts/python.exe -m unittest \
  tests.test_openai_rag.OpenAIRAGTest.test_retrieval_recusa_dimensao_real_incompativel_antes_de_consultar_chroma
Ran 1 test — OK
```

## Verificações finais

```text
.venv/Scripts/python.exe -m unittest tests.test_openai_rag
Ran 18 tests — OK

.venv/Scripts/python.exe -m unittest discover -s tests -v
Ran 39 tests — OK

.venv/Scripts/python.exe -m compileall -q openai_rag.py tests/test_openai_rag.py
exit 0

git diff --check
exit 0 (apenas avisos de normalização LF/CRLF do Git no Windows)
```

## Revisão focal

O diff permanece restrito à Fachada RAG, aos testes de comportamento e a esta
evidência. Não altera geração local, rollback, coleções existentes, limiar de
retrieval nem inicia MIG-04. Recusa, fontes, retry e **Resposta Parcial** passam
na suíte completa. O gate CTO independente continua sendo a próxima decisão
antes de MIG-04.
