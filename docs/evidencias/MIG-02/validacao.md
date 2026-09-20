# MIG-02 — validação automatizada

## Escopo

Os testes exercitam a fronteira do reindexador com Chroma efêmero e um Provider
OpenAI dublê. Nenhuma chave OpenAI, PDF ou coleção persistente foi usado nesta
validação.

## Comando

```text
.venv/Scripts/python -m unittest tests.test_openai_index -v
```

## Resultado

- 3 testes passaram.
- Coleção incompatível: recusada com orientação de reindexação.
- Corpus sintético com oito arquivos: 8 chunks, modelo e versão registrados.
- Metadados obrigatórios preservados: arquivo, página, ano, idioma, tema e
  identificador de chunk.
- Coleção legada dublê permaneceu com seu vetor.
- Segunda execução não duplicou os chunks.

A reindexação real depende da chave OpenAI e dos PDFs locais; este artefato não
afirma que a coleção persistente foi gerada ao vivo.
