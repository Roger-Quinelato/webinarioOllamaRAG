# MIG-03 — validação automatizada

## Comando

```text
.venv/Scripts/python -m unittest tests.test_openai_rag -v
```

## Cobertura observável

- Retrieval recebe apenas a pergunta atual, respeita filtro e limita a cinco
  Chunks Recuperados.
- Geração usa no máximo as duas últimas turnos e envia no máximo três chunks no
  prompt.
- Marcadores válidos classificam somente as respectivas Fontes Citadas.
- Resposta sem marcador é Fallback, sem promover Chunk Recuperado a Fonte
  Citada.
- Ausência de resultados produz Recusa sem chamar geração.
- Falha antes do primeiro token repete uma vez; falha posterior preserva e marca
  Resposta Parcial.

Não houve chamada real à OpenAI neste teste; o Provider foi dublado apenas na
fronteira externa.
