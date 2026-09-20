# Evidência MIG-02H — issue #67

Data: 2026-09-20

## Estado do gate

Implementação e testes automatizados concluídos. A prova runtime de reindexação
e a calibração real estão **bloqueadas** neste host porque `ollama list` não
retorna modelos instalados; em particular, `bge-m3` está ausente. Nenhuma
contagem ou distância real foi inferida.

MIG-04 permanece bloqueada até a reindexação, a calibração e o gate CTO conjunto.

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

## Prova runtime bloqueada

Pré-condições locais:

```text
> ollama list
NAME    ID    SIZE    MODIFIED
> Get-ChildItem artigos -Filter *.pdf
PDF_COUNT=8
```

Comando reproduzível de reindexação:

```text
> .venv\Scripts\python.exe scripts\02_indexar_hibrido.py
ERRO: O modelo bge-m3 não está instalado. Execute `ollama pull bge-m3` e tente novamente.
EXIT_CODE=2
```

Comando reproduzível de calibração, que depende da publicação anterior:

```text
> .venv\Scripts\python.exe scripts\calibrar_retrieval_hibrido.py
ERRO: Corpus Oficial híbrido não publicado; execute a reindexação.
CALIBRATION_EXIT_CODE=2
```

Depois de instalar `bge-m3`, execute os dois comandos acima nessa ordem e salve
a saída. O segundo comando reutiliza as oito perguntas positivas e cinco
negativas já versionadas e só aprova o limiar ativo se ele estiver no intervalo
separador medido.

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
