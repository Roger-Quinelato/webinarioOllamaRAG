# Evidência de validação — MIG-03H / #66

Data: 2026-09-20

## Escopo validado

- provider de embeddings `bge-m3` via Ollama, com o cliente externo simulado;
- provider OpenAI restrito a geração e streaming;
- Fachada RAG com providers separados para retrieval e geração;
- validação da Base Ativa por provider, modelo, dimensão, versão e estado;
- preservação de Recusa, Fonte Citada, retry e Resposta Parcial;
- ausência de fallback automático para geração local.

Reindexação híbrida e upload não foram implementados nesta issue.

## Ciclos red-green

1. Provider Ollama: `python -m unittest tests.test_ollama_embedding_provider -v`
   falhou primeiro com `ModuleNotFoundError: No module named
   'ollama_embedding_provider'`; passou após o adapter mínimo.
2. Provider OpenAI: o teste `test_expoe_somente_geracao_e_streaming` falhou
   enquanto `gerar_embeddings` e `MODELO_EMBEDDING` ainda estavam expostos;
   passou após remover ambos da fronteira OpenAI. A constante do indexador
   legado foi apenas realocada, sem mudar seu comportamento.
3. Fachada RAG: o teste `test_retrieval_e_geracao_usam_providers_distintos`
   falhou com `TypeError` no construtor de um provider; passou após separar os
   providers de embedding e geração.
4. Compatibilidade: o teste parametrizado da Base Ativa falhou para provider,
   modelo, dimensão, versão e estado; passou após validar todos os metadados e
   orientar reindexação explícita.

## Comandos finais

```text
.venv\Scripts\python.exe -m unittest tests.test_ollama_embedding_provider tests.test_openai_provider tests.test_openai_rag -v
Ran 24 tests in 4.418s
OK

.venv\Scripts\python.exe -m unittest discover -v
Ran 32 tests in 2.744s
OK

.venv\Scripts\python.exe -m compileall -q openai_provider.py ollama_embedding_provider.py openai_rag.py openai_index.py tests
exit 0

git diff --check
exit 0 (somente avisos de conversão LF/CRLF do Git no Windows)
```

O primeiro ensaio da suíte completa com o Python global não carregou
`tests.test_openai_index` porque esse interpretador não possui `chromadb`. A
execução canônica acima usou o `.venv` do repositório e passou integralmente.
