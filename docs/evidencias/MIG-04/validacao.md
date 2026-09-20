# Evidência MIG-04

**Issue:** #62
**Objetivo:** criar Índice de Sessão efêmero, isolado e compatível com o Corpus Oficial `bge-m3`.

## Comandos executados

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_session_index -v
.\.venv\Scripts\python.exe -m unittest discover tests -v
```

## Resultado

- `tests.test_session_index`: 7 testes passaram.
- Suíte completa: 49 testes passaram.
- Vetores de sessão exigem dimensão `1024`; dimensão `3`, vetores vazios e quantidade divergente são recusados antes de criar coleção.
- Provider deve ser `ProviderEmbeddingsOllama` com `bge-m3`; falha do Ollama é propagada sem publicar coleção.
- Cliente Chroma compartilhado mantém coleções de sessões distintas isoladas.
- `IndiceSessao.descartar()` remove somente sua coleção e aceita repetição.
- Teste preserva coleção `artigos_rag_hibrido`, representando o Corpus Oficial.
- Upload válido é publicado antes do descarte do Índice de Sessão anterior. Limpar conversa chama `descartar()`.
