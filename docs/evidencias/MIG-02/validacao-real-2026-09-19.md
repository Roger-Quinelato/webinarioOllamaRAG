# Validação real MIG-02/MIG-03 — 2026-09-19

## Resultado

- Credencial: configurada em `st.secrets`, sem registrar o valor.
- Corpus local: 8 PDFs em `artigos/`.
- Reindexação real: **bloqueada pela OpenAI com HTTP 429 (limite de requisições)**.
- Nova publicação: não ocorreu.
- Manifesto local existente: `ready`, mas aponta para uma coleção que não está presente na listagem atual; portanto não é aceito como prova de indexação real.
- Suíte local: `24` testes passaram.
- Coleção legada: não alterada pela tentativa.

## Gate

`BLOQUEADO — evidência real insuficiente.`

Não iniciar MIG-04. Repetir a indexação após normalizar o limite/quota da conta e validar manifesto, contagem, metadados e preservação da coleção legada.
