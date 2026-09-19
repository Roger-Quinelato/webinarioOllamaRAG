# MIG-01 — validação

Data: 2026-09-19

## Contratos testados

- ausência de `OPENAI_API_KEY` informa como configurá-la, sem revelar valor;
- embeddings usam `text-embedding-3-small`;
- geração e streaming usam `gpt-5.6-luna`;
- falhas de autenticação, limite e rede retornam mensagens acionáveis sem o
  detalhe do provider;
- `response.failed` e `response.incomplete` do streaming chegam à futura
  fachada como erro; o provider não realiza retentativas implícitas.

## Comandos e resultado

```text
python -m unittest discover -s tests -v
Ran 10 tests
OK

python -m compileall -q openai_provider.py
OK

python -m pip check
No broken requirements found.

python -m pip install --dry-run --disable-pip-version-check -r requirements.txt
Collecting openai==3.16.2
```

O interpretador de desenvolvimento ainda tem `openai==2.24.0`; por isso esta
validação confirma que o resolvedor aceita o pin 3.16.2, mas não declara uma
chamada real à API nem compatibilidade em runtime até que a dependência seja
instalada no ambiente do projeto.

O SDK e o uso direto da API foram conferidos na documentação oficial da OpenAI:
https://developers.openai.com/pt-BR/api/docs/libraries

## Rollback

Reverter este commit remove somente o novo limite OpenAI e sua dependência; o
caminho legado e a tag `legacy-pre-openai` permanecem inalterados.
