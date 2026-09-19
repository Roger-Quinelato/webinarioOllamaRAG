# MIG-01 — validação

Data: 2026-09-19

## Contratos testados

- ausência de `OPENAI_API_KEY` informa como configurá-la, sem revelar valor;
- embeddings usam `text-embedding-3-small`;
- geração e streaming usam `gpt-5.6-luna`;
- falhas de autenticação, limite e rede retornam mensagens acionáveis sem o
  detalhe do provider;
- resposta síncrona incompleta e streaming sem `response.completed` chegam à
  futura fachada como erro; o provider não realiza retentativas implícitas.

## Comandos e resultado

```text
python -m unittest discover -s tests -v
Ran 12 tests
OK

python -m compileall -q openai_provider.py
OK

requirements.lock
Inclui openai==3.16.2, distro==1.9.0, jiter==0.17.0 e sniffio==1.3.1.
```

O ambiente global de desenvolvimento ainda executa `openai==2.24.0`. A instalação
do pin no ambiente isolado do projeto continua necessária antes de chamada real
à API; esta evidência não declara compatibilidade de runtime com a API.

O SDK e o uso direto da API foram conferidos na documentação oficial da OpenAI:
https://developers.openai.com/pt-BR/api/docs/libraries

## Rollback

Reverter este commit remove somente o novo limite OpenAI e sua dependência; o
caminho legado e a tag `legacy-pre-openai` permanecem inalterados.
