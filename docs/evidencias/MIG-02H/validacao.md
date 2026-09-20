# Evidência MIG-02H — issue #67

Data: 2026-09-20

## Estado do gate

Implementação, testes automatizados e prova runtime de reindexação concluídos.
O `bge-m3` está instalado e a coleção híbrida foi publicada e calibrada. A
correção do limiar medido está registrada na evidência da issue #68.

MIG-04 permanece bloqueada até o gate CTO conjunto.

## TDD

Primeiro RED no seam público do índice:

```text
> .venv\Scripts\python.exe -m unittest tests.test_hybrid_index -v
ImportError: Failed to import test module: test_hybrid_index
ModuleNotFoundError: No module named 'hybrid_index'
FAILED (errors=1)
```

RED adicional para manifesto apontando para coleção ausente:

```text
chromadb.errors.NotFoundError: Collection [candidata-ausente] does not exist
FAILED (errors=1)
```

GREEN focado final:

```text
> .venv\Scripts\python.exe -m unittest tests.test_hybrid_index tests.test_retrieval_calibration tests.test_ollama_embedding_provider -v
Ran 10 tests in 1.297s
OK
FOCUSED_EXIT_CODE=0
```

Os testes cobrem metadados da coleção e do manifesto, dimensão descoberta,
provider/modelo, IDs únicos, preservação atômica, idempotência por identidade do
corpus, preservação das coleções legada e candidata OpenAI, erros acionáveis e
validação determinística do limiar.

## Prova runtime concluída

Pré-condições locais:

```text
> ollama list
NAME             ID              SIZE
bge-m3:latest    790764642607    1.2 GB
> Get-ChildItem artigos -Filter *.pdf
PDF_COUNT=8
```

Resultado real de `.venv\Scripts\python.exe scripts\02_indexar_hibrido.py`:

```text
artigos=8
chunks=661
embeddings_gerados=661
modelo_embedding=bge-m3
dimensao_embedding=1024
colecao=artigos_rag_hibrido_a280e65e16ee
duracao_segundos=1318.342029499996
EXIT_CODE=0
```

O manifesto publicado aponta para a mesma coleção com provider `Ollama`, modelo
`bge-m3`, dimensão `1024`, versão `bge-m3-v1`, corpus `Corpus Oficial` e estado
`ready`.

A calibração real inicial demonstrou que o antigo limiar `0.60` não separava a
matriz: maior positiva `0.44007039070129395` e menor negativa
`0.5800204873085022`. A issue #68 definiu o ponto médio
`0.5100454390048981`, com margem igual `0.06997504830360413` dos dois lados.
As 13 medições completas estão em
[`../MIG-03C/validacao.md`](../MIG-03C/validacao.md).

```text
> .venv\Scripts\python.exe scripts\calibrar_retrieval_hibrido.py
limiar_validado=0.5100454390048981
maior_distancia_positiva=0.44007039070129395
menor_distancia_negativa=0.5800204873085022
CALIBRATION_EXIT_CODE=0
```

## Verificações

```text
> .venv\Scripts\python.exe -m unittest discover -s tests -v
Ran 31 tests in 2.594s
OK
FULL_EXIT_CODE=0

> .venv\Scripts\python.exe -m compileall -q hybrid_index.py retrieval_calibration.py scripts tests ferramentas\verificar.py
COMPILE_EXIT_CODE=0

> git diff --check
DIFF_CHECK_EXIT_CODE=0
```

`git diff --check` emitiu apenas o aviso informativo de conversão LF/CRLF para
`ferramentas/verificar.py` no Windows.
